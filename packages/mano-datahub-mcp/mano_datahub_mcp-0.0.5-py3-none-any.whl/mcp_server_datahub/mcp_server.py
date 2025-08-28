import ast
import contextlib
import contextvars
import functools
import inspect
import pathlib
import json
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    ParamSpec,
    TypeVar,
)

import asyncer
import jmespath
from datahub.errors import ItemNotFoundError
from datahub.ingestion.graph.client import DataHubGraph
from datahub.metadata.urns import DatasetUrn, SchemaFieldUrn, Urn
from datahub.sdk.main_client import DataHubClient
from datahub.sdk.search_client import compile_filters
from datahub.sdk.search_filters import Filter, FilterDsl, load_filters
from datahub.utilities.ordered_set import OrderedSet
from fastmcp import FastMCP
from pydantic import BaseModel

_P = ParamSpec("_P")
_R = TypeVar("_R")


# See https://github.com/jlowin/fastmcp/issues/864#issuecomment-3103678258
# for why we need to wrap sync functions with asyncify.
def async_background(fn: Callable[_P, _R]) -> Callable[_P, Awaitable[_R]]:
    if inspect.iscoroutinefunction(fn):
        raise RuntimeError("async_background can only be used on non-async functions")

    @functools.wraps(fn)
    async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        return await asyncer.asyncify(fn)(*args, **kwargs)

    return wrapper


mcp = FastMCP[None](name="datahub")


_mcp_dh_client = contextvars.ContextVar[DataHubClient]("_mcp_dh_client")


def get_datahub_client() -> DataHubClient:
    # Will raise a LookupError if no client is set.
    return _mcp_dh_client.get()


def set_datahub_client(client: DataHubClient) -> None:
    _mcp_dh_client.set(client)


@contextlib.contextmanager
def with_datahub_client(client: DataHubClient) -> Iterator[None]:
    token = _mcp_dh_client.set(client)
    try:
        yield
    finally:
        _mcp_dh_client.reset(token)


def _enable_cloud_fields(query: str) -> str:
    return query.replace("#[CLOUD]", "")


def _is_datahub_cloud(graph: DataHubGraph) -> bool:
    try:
        # Only DataHub Cloud has a frontend base url.
        _ = graph.frontend_base_url
    except ValueError:
        return False
    return True


def _execute_graphql(
    graph: DataHubGraph,
    *,
    query: str,
    operation_name: Optional[str] = None,
    variables: Optional[Dict[str, Any]] = None,
) -> Any:
    if _is_datahub_cloud(graph):
        query = _enable_cloud_fields(query)

    return graph.execute_graphql(
        query=query, variables=variables, operation_name=operation_name
    )


def inject_urls_for_urns(
    graph: DataHubGraph, response: Any, json_paths: List[str]
) -> None:
    if not _is_datahub_cloud(graph):
        return

    for path in json_paths:
        for item in jmespath.search(path, response) if path else [response]:
            if isinstance(item, dict) and item.get("urn"):
                # Update item in place with url, ensuring that urn and url are first.
                new_item = {"urn": item["urn"], "url": graph.url_for(item["urn"])}
                new_item.update({k: v for k, v in item.items() if k != "urn"})
                item.clear()
                item.update(new_item)


def maybe_convert_to_schema_field_urn(urn: str, column: Optional[str]) -> str:
    if column is not None:
        maybe_dataset_urn = Urn.from_string(urn)
        if not isinstance(maybe_dataset_urn, DatasetUrn):
            raise ValueError(
                f"Input urn should be a dataset urn if column is provided, but got {urn}."
            )
        urn = str(SchemaFieldUrn(maybe_dataset_urn, column))
    return urn


query_by_keywords_gql = (
    pathlib.Path(__file__).parent / "gql/query_by_keywords.gql"
).read_text()
search_gql = (pathlib.Path(__file__).parent / "gql/search.gql").read_text()
entity_details_fragment_gql = (
    pathlib.Path(__file__).parent / "gql/entity_details.gql"
).read_text()

queries_gql = (pathlib.Path(__file__).parent / "gql/queries.gql").read_text()


def clean_gql_response(response: Any) -> Any:
    if isinstance(response, dict):
        banned_keys = {
            "__typename",
        }

        cleaned_response = {}
        for k, v in response.items():
            if k in banned_keys or v is None or v == []:
                continue
            cleaned_v = clean_gql_response(v)
            if cleaned_v is not None and cleaned_v != {}:
                cleaned_response[k] = cleaned_v

        return cleaned_response
    elif isinstance(response, list):
        return [clean_gql_response(item) for item in response]
    else:
        return response


# def _parse_ownership(ownership: dict) -> dict:


def _parse_structured_properties(structured_properties: dict) -> list:
    """
    Flattens the structuredProperties dict to a list of property dicts, each containing:
    - urn
    - displayName
    - qualifiedName
    - values (list of stringValue)
    Returns a list of property dicts.
    """
    result = []
    properties_list = structured_properties.get("properties", [])
    for prop in properties_list:
        structured_prop = prop.get("structuredProperty", {})
        values = prop.get("values", [])
        if "stringValue" in json.dumps(values):
            # Use ast.literal_eval to preserve empty values and handle Python literals safely
            try:
                values = [ast.literal_eval(v.get("stringValue")) for v in values]
            except (ValueError, SyntaxError):
                # Fallback to string values if parsing fails
                values = [v.get("stringValue") for v in values]
        if "numberValue" in json.dumps(values):
            values = [v.get("numberValue") for v in values]
        flattened = {
            "urn": structured_prop.get("urn"),
            "displayName": structured_prop.get("definition", {}).get("displayName"),
            "qualifiedName": structured_prop.get("definition", {}).get("qualifiedName"),
            "values": values,
        }
        result.append(flattened)
    return result


def _parse_institutional_memory(knowledge_links: dict) -> dict[str, list]:
    """
    Flattens the institutionalMemory/knowledge_links dict to a list of dicts with 'url' and 'name' (from 'label').
    Returns a dict with key 'knowledge_links' and value as the list.
    """
    elements = knowledge_links.get("elements", [])
    flattened_links = []
    for element in elements:
        url = element.get("url")
        name = element.get("label")
        if url or name:
            flattened_links.append({"url": url, "name": name})
    return {"knowledge_links": flattened_links}


def _parse_dataproduct_relationships(data_product: dict) -> dict:
    """
    Parses a dataset relationship dict and flattens it to only include:
    - urn
    - dataproduct_name
    - dataproduct_description
    - dataproduct_urn

    Returns the flattened dict.
    """
    relationships = data_product.get("relationships", [])
    dataproduct_urn = None
    dataproduct_name = None
    dataproduct_description = None

    # Find the first DataProductContains relationship, if any
    for rel in relationships:
        if rel.get("type") == "DataProductContains":
            entity = rel.get("entity", {})
            dataproduct_urn = entity.get("urn")
            properties = entity.get("properties", {})
            dataproduct_name = properties.get("name")
            dataproduct_description = properties.get("description")
            break

    flattened = {
        "dataproduct_urn": dataproduct_urn,
        "dataproduct_name": dataproduct_name,
        "dataproduct_description": dataproduct_description,
    }
    return flattened


def _parse_ownership(ownership: dict) -> list:
    """
    Converts an ownership dict to a list of owners with username and ownership type.
    """
    owners = ownership.get("owners", [])
    flattened_owners = []
    for owner_entry in owners:
        username = owner_entry.get("owner", {}).get("username")
        ownership_type = (
            owner_entry.get("ownershipType", {}).get("info", {}).get("name")
        )
        flattened_owners.append({"username": username, "ownershipType": ownership_type})
    return flattened_owners


def _parse_parent_nodes(parent_nodes: dict) -> list:
    """
    Flattens the parentNodes dict to a list of urns.
    """
    nodes = parent_nodes.get("nodes", [])
    return [node.get("urn") for node in nodes if "urn" in node]


def _parse_domain(domain: dict) -> list:
    """
    Flattens the domain dict to a list of dicts with 'urn', 'name', and 'description'.
    Handles parent domains as well.
    """
    domains: list = []
    if not domain:
        return domains

    # Add the main domain
    domains.append(
        {
            "urn": domain.get("urn"),
            "name": domain.get("properties", {}).get("name"),
            "description": domain.get("properties", {}).get("description"),
        }
    )

    # Add parent domains if present
    parent_domains = domain.get("parentDomains", {}).get("domains", [])
    for parent in parent_domains:
        domains.append(
            {
                "urn": parent.get("urn"),
                "name": parent.get("properties", {}).get("name"),
                "description": parent.get("properties", {}).get("description"),
            }
        )

    return domains


def _parse_field(field: dict) -> dict:
    """
    Parses a field dict to a list of dicts with 'name' and 'description'.
    """
    final_field = {}
    final_field["name"] = field.get("fieldPath")
    final_field["description"] = field.get("description")
    final_field["type"] = field.get("nativeDataType")
    glossary_terms = []
    for glossary_term in field.get("glossaryTerms", {}).get("terms", []):
        final_glossary_term = {}
        final_glossary_term["name"] = (
            glossary_term.get("term", {}).get("properties", {}).get("name")
        )
        final_glossary_term["urn"] = glossary_term.get("term", {}).get("urn")
        final_glossary_term["description"] = (
            glossary_term.get("term", {}).get("properties", {}).get("description")
        )
        for prop in _parse_structured_properties(
            glossary_term.get("term", {}).get("structuredProperties", {})
        ):
            if "term_type" in prop["qualifiedName"]:
                final_glossary_term["term_type"] = prop["values"]
            else:
                final_field[prop["qualifiedName"].split(".")[-1]] = prop["values"]
        glossary_terms.append(final_glossary_term)
    final_field["glossary_terms"] = glossary_terms
    return final_field


def _clean_entity_response(response: dict) -> dict:
    if response and (properties := response.get("properties")):
        response.update(properties)
        response.pop("properties", None)
        response.pop("termSource", None)
    if response and (structured_properties := response.get("structuredProperties")):
        response["structuredProperties"] = _parse_structured_properties(
            structured_properties
        )

    if response and (ownership := response.get("ownership")):
        response["ownership"] = _parse_ownership(ownership)

    if response and (institutional_memory := response.get("institutionalMemory")):
        response.update(_parse_institutional_memory(institutional_memory))
        response.pop("institutionalMemory", None)

    if response and (parent_nodes := response.get("parentNodes")):
        response["parentNodes"] = _parse_parent_nodes(parent_nodes)
    return response


def _clean_glossary_term_response(response: dict) -> dict:
    # Clean up glossary term relationships - remove SchemaFieldWithGlossaryTerm without data products
    if response and (
        relationships := response.get("datasets", {}).get("relationships")
    ):
        # Filter out SchemaFieldWithGlossaryTerm relationships that don't have data products
        filtered_relationships = []
        for rel in relationships:
            if rel.get("type") == "SchemaFieldWithGlossaryTerm":
                # Check if the entity has data products with relationships
                entity = rel.get("entity", {})
                data_product = entity.get("dataProduct", {})
                data_product_rels = data_product.get("relationships", [])
                dataset_urn = rel.get("entity", {}).get("urn")

                # Only keep relationships that have data products with actual relationships
                if data_product_rels:
                    rel = _parse_dataproduct_relationships(data_product)
                    rel["dataset_urn"] = dataset_urn
                    filtered_relationships.append(rel)

        # Update the relationships list
        response["datasets"] = filtered_relationships

    return response


def _clean_dataset_response(response: dict) -> dict:
    """
    Cleans dataset response by parsing relationships and applying dataset-specific cleaning.
    """
    parsed_dataproduct = _parse_dataproduct_relationships(
        response.get("dataProduct", {})
    )
    response["dataProduct"] = parsed_dataproduct
    response["table_name"] = response.get("schemaMetadata", {}).get("name")
    response["platform_name"] = response.get("platform", {}).get("name")
    response.pop("platform", None)
    response.pop("viewProperties", None)
    columns = []
    for field in response.get("schemaMetadata", {}).get("fields", []):
        columns.append(_parse_field(field))
    response["columns"] = columns
    response.pop("schemaMetadata", None)
    response["domains"] = _parse_domain(response.get("domain", {}).get("domain", {}))
    response.pop("domain", None)

    return response


def _parse_data_product_glossary_terms(glossary_terms: dict) -> list:
    """
    Parses glossary terms for data products, similar to _parse_field but for data product entities.
    """
    if not glossary_terms or not glossary_terms.get("terms"):
        return []

    parsed_terms = []
    for term_entry in glossary_terms.get("terms", []):
        term = term_entry.get("term", {})
        if not term:
            continue

        parsed_term = {
            "name": term.get("properties", {}).get("name"),
            "urn": term.get("urn"),
            "description": term.get("properties", {}).get("description"),
        }

        # Parse structured properties if they exist
        if term.get("structuredProperties"):
            structured_props = _parse_structured_properties(
                term.get("structuredProperties", {})
            )
            for prop in structured_props:
                if "term_type" in prop["qualifiedName"]:
                    parsed_term["term_type"] = prop["values"]
                else:
                    # Extract the property name from the qualified name
                    prop_name = prop["qualifiedName"].split(".")[-1]
                    parsed_term[prop_name] = prop["values"]

        parsed_terms.append(parsed_term)

    return parsed_terms


def _clean_data_product_response(response: dict) -> dict:
    """
    Cleans data product response by flattening tables and parsing glossary terms.
    """
    # Handle tables
    if response and (tables := response.get("tables", {}).get("searchResults")):
        flattened_tables = []
        for table in tables:
            entity = table.get("entity", {})
            flattened_tables.append(
                {"name": entity.get("name"), "urn": entity.get("urn")}
            )
        response["tables"] = flattened_tables

    # Handle glossary terms
    if response and (glossary_terms := response.get("glossaryTerms")):
        response["glossary_terms"] = _parse_data_product_glossary_terms(glossary_terms)

    response.pop("glossaryTerms", None)
    return response


def clean_get_entity_response(raw_response: dict) -> dict:
    response = clean_gql_response(raw_response)

    if response and (schema_metadata := response.get("schemaMetadata")):
        # Remove empty platformSchema to reduce response clutter
        if platform_schema := schema_metadata.get("platformSchema"):
            schema_value = platform_schema.get("schema")
            if not schema_value or schema_value == "":
                del schema_metadata["platformSchema"]

        # Remove default field attributes (false values) to keep only meaningful data
        if fields := schema_metadata.get("fields"):
            for field in fields:
                if field.get("recursive") is False:
                    field.pop("recursive", None)
                if field.get("isPartOfKey") is False:
                    field.pop("isPartOfKey", None)

    if response and response.get("type") in [
        "GLOSSARY_TERM",
        "DATASET",
        "DATA_PRODUCT",
    ]:
        response = _clean_entity_response(response)
        if response.get("type") == "GLOSSARY_TERM":
            return _clean_glossary_term_response(response)
        elif response.get("type") == "DATASET":
            return _clean_dataset_response(response)
        elif response.get("type") == "DATA_PRODUCT":
            return _clean_data_product_response(response)

    return response


def _remove_empty_fields(obj):
    """Recursively remove empty fields from dictionaries and lists."""
    if isinstance(obj, dict):
        # Create a new dict with non-empty values
        cleaned = {}
        for key, value in obj.items():
            cleaned_value = _remove_empty_fields(value)
            # Only keep non-empty values (not None, not empty dict/list, not empty string)
            if (
                cleaned_value is not None
                and cleaned_value != {}
                and cleaned_value != []
                and cleaned_value != ""
            ):
                cleaned[key] = cleaned_value
        return cleaned
    elif isinstance(obj, list):
        # Filter out empty items from lists
        cleaned_list = [_remove_empty_fields(item) for item in obj]
        return [
            item
            for item in cleaned_list
            if item is not None and item != {} and item != [] and item != ""
        ]
    else:
        # Return primitive values as-is
        return obj


@mcp.tool(description="Get an entity by its DataHub URN.")
@async_background
def get_entity(urn: str) -> dict:
    client = get_datahub_client()

    if not client._graph.exists(urn):
        # TODO: Ideally we use the `exists` field to check this, and also deal with soft-deleted entities.
        raise ItemNotFoundError(f"Entity {urn} not found")

    # Execute the GraphQL query
    variables = {"urn": urn}
    result = _execute_graphql(
        client._graph,
        query=entity_details_fragment_gql,
        variables=variables,
        operation_name="GetEntity",
    )["entity"]

    inject_urls_for_urns(client._graph, result, [""])

    return clean_get_entity_response(result)


@mcp.tool(
    description="""Search across DataHub entities.

Returns both a truncated list of results and facets/aggregations that can be used to iteratively refine the search filters.
To search for all entities, use the wildcard '*' as the query and set `filters: null`.

A typical workflow will involve multiple calls to this search tool, with each call refining the filters based on the facets/aggregations returned in the previous call.
After the final search is performed, you'll want to use the other tools to get more details about the relevant entities.

Here are some example filters:
- All Looker assets
```
{"platform": ["looker"]}
```
- Production environment warehouse assets
```
{
  "and": [
    {"env": ["PROD"]},
    {"platform": ["snowflake", "bigquery", "redshift"]}
  ]
}
```
- All non-Snowflake tables
```
{
  "and":[
    {"entity_type": ["DATASET"]},
    {"entity_subtype": ["Table"]},
    {"not": {"platform": ["snowflake"]}}
  ]
}
```
"""
)
@async_background
def search(
    query: str = "*",
    filters: Optional[Filter | str] = None,
    num_results: int = 10,
) -> dict:
    client = get_datahub_client()

    # As of 2025-07-25: Our Filter type is a tagged/discriminated union.
    #
    # We've observed that some tools (e.g. Cursor) don't support discriminated
    # unions in their JSON schema validation, and hence reject valid tool calls
    # before they're even passed to our MCP server.
    # Beyond that, older LLMs (e.g. Claude Desktop w/ Sonnet 3.5) have a tendency
    # to pass tool args as JSON-encoded strings instead of proper objects.
    #
    # To work around these issues, we allow stringified JSON filters that we
    # parse on our end. The FastMCP library used to have built-in support for
    # handling this, but removed it in
    # https://github.com/jlowin/fastmcp/commit/7b9696405b1427f4dc5430891166286744b3dab5
    if isinstance(filters, str):
        # The Filter type already has a BeforeValidator that parses JSON strings.
        filters = load_filters(filters)
    types, compiled_filters = compile_filters(filters)
    variables = {
        "query": query,
        "types": types,
        "orFilters": compiled_filters,
        "count": max(num_results, 1),  # 0 is not a valid value for count.
    }

    response = _execute_graphql(
        client._graph,
        query=search_gql,
        variables=variables,
        operation_name="search",
    )["scrollAcrossEntities"]

    if num_results == 0 and isinstance(response, dict):
        # Hack to support num_results=0 without support for it in the backend.
        response.pop("searchResults", None)
        response.pop("count", None)

    return clean_gql_response(response)


@mcp.tool(
    description="Use this tool to get the SQL queries associated with a dataset or a dataset column."
)
@async_background
def get_dataset_queries(
    urn: str, column: Optional[str] = None, start: int = 0, count: int = 10
) -> dict:
    client = get_datahub_client()

    urn = maybe_convert_to_schema_field_urn(urn, column)

    entities_filter = FilterDsl.custom_filter(
        field="entities", condition="EQUAL", values=[urn]
    )
    _, compiled_filters = compile_filters(entities_filter)

    # Set up variables for the query
    variables = {
        "input": {"start": start, "count": count, "orFilters": compiled_filters}
    }

    # Execute the GraphQL query
    result = _execute_graphql(
        client._graph,
        query=queries_gql,
        variables=variables,
        operation_name="listQueries",
    )["listQueries"]

    for query in result["queries"]:
        if query.get("subjects"):
            query["subjects"] = _deduplicate_subjects(query["subjects"])

    return clean_gql_response(result)


def _deduplicate_subjects(subjects: list[dict]) -> list[str]:
    # The "subjects" field returns every dataset and schema field associated with the query.
    # While this is useful for our backend to have, it's not useful here because
    # we can just look at the query directly. So we'll narrow it down to the unique
    # list of dataset urns.
    updated_subjects: OrderedSet[str] = OrderedSet()
    for subject in subjects:
        with contextlib.suppress(KeyError):
            updated_subjects.add(subject["dataset"]["urn"])
    return list(updated_subjects)


class AssetLineageDirective(BaseModel):
    urn: str
    upstream: bool
    downstream: bool
    max_hops: int
    extra_filters: Optional[Filter]


class AssetLineageAPI:
    def __init__(self, graph: DataHubGraph) -> None:
        self.graph = graph

    def get_degree_filter(self, max_hops: int) -> Filter:
        """
        max_hops: Maximum number of hops to search for lineage
        """
        if max_hops == 1 or max_hops == 2:
            return FilterDsl.custom_filter(
                field="degree",
                condition="EQUAL",
                values=[str(i) for i in range(1, max_hops + 1)],
            )
        elif max_hops >= 3:
            return FilterDsl.custom_filter(
                field="degree",
                condition="EQUAL",
                values=["1", "2", "3+"],
            )
        else:
            raise ValueError(f"Invalid number of hops: {max_hops}")

    def get_lineage(
        self, asset_lineage_directive: AssetLineageDirective
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        filter = self.get_degree_filter(asset_lineage_directive.max_hops)
        if asset_lineage_directive.extra_filters:
            filter = FilterDsl.and_(filter, asset_lineage_directive.extra_filters)
        types, compiled_filters = compile_filters(filter)
        variables = {
            "urn": asset_lineage_directive.urn,
            "start": 0,
            "count": 30,
            "types": types,
            "orFilters": compiled_filters,
            "searchFlags": {"skipHighlighting": True, "maxAggValues": 3},
        }
        if asset_lineage_directive.upstream:
            result["upstreams"] = clean_gql_response(
                _execute_graphql(
                    self.graph,
                    query=entity_details_fragment_gql,
                    variables={
                        "input": {
                            **variables,
                            "direction": "UPSTREAM",
                        }
                    },
                    operation_name="GetEntityLineage",
                )["searchAcrossLineage"]
            )
        if asset_lineage_directive.downstream:
            result["downstreams"] = clean_gql_response(
                _execute_graphql(
                    self.graph,
                    query=entity_details_fragment_gql,
                    variables={
                        "input": {
                            **variables,
                            "direction": "DOWNSTREAM",
                        }
                    },
                    operation_name="GetEntityLineage",
                )["searchAcrossLineage"]
            )

        return result


@mcp.tool(
    description="""\
Use this tool to get upstream or downstream lineage for any entity, including datasets, schemaFields, dashboards, charts, etc. \
Set upstream to True for upstream lineage, False for downstream lineage.
Set `column: null` to get lineage for entire dataset or for entity type other than dataset.
Setting max_hops to 3 is equivalent to unlimited hops.
Usage and format of filters is same as that in search tool.
"""
)
@async_background
def get_lineage(
    urn: str,
    column: Optional[str],
    filters: Optional[Filter | str] = None,
    upstream: bool = True,
    max_hops: int = 1,
) -> dict:
    client = get_datahub_client()
    # NOTE: See comment in search tool for why we parse filters as strings.
    if isinstance(filters, str):
        # The Filter type already has a BeforeValidator that parses JSON strings.
        filters = load_filters(filters)

    lineage_api = AssetLineageAPI(client._graph)

    urn = maybe_convert_to_schema_field_urn(urn, column)
    asset_lineage_directive = AssetLineageDirective(
        urn=urn,
        upstream=upstream,
        downstream=not upstream,
        max_hops=max_hops,
        extra_filters=filters,
    )
    lineage = lineage_api.get_lineage(asset_lineage_directive)
    inject_urls_for_urns(client._graph, lineage, ["*.searchResults[].entity"])
    return lineage


@mcp.tool(
    description="""Get data products associated with specific keywords.
    
    Takes a list of keywords, searches for glossary terms that contain those keywords,
    and then finds data products associated with those terms.
    This is useful for finding data products based on business concepts and keywords.
    
    Args:
        keywords: List of keywords to search for
        
    Returns:
        List of unique data product objects with name, description, and URN
    """
)
@async_background
def get_data_products_by_keywords(keywords: List[str]) -> Any:
    client = get_datahub_client()

    # Create a string query with OR conditions for each keyword
    query_parts = []
    for keyword in keywords:
        query_parts.append(f"{keyword}")
        query_parts.append(
            f"structuredProperties.io_appsflyer_glossary_enum_validation:*{keyword}*"
        )

    query = " OR ".join(query_parts)

    # Set up variables for the search
    variables = {
        "query": f"/q {query}",
        "types": ["GLOSSARY_TERM"],
        "count": 50,  # Scale count based on number of keywords
    }

    try:
        response = _execute_graphql(
            client._graph,
            query=query_by_keywords_gql,
            variables=variables,
            operation_name="search",
        )["scrollAcrossEntities"]

        # Extract unique data products from the search results
        unique_data_products = {}
        if response and (search_results := response.get("searchResults")):
            for result in search_results:
                for dataset in (
                    result.get("entity", {})
                    .get("datasets", {})
                    .get("relationships", [])
                ):
                    data_product_relationships = (
                        dataset.get("entity", {})
                        .get("dataProduct", {})
                        .get("relationships", [])
                    )
                    if data_product_relationships:
                        dp_entity = data_product_relationships[0].get("entity", {})
                        dp_urn = dp_entity.get("urn")
                        dp_name = dp_entity.get("properties", {}).get("name")
                        dp_description = dp_entity.get("properties", {}).get(
                            "description"
                        )
                    else:
                        dp_urn = dp_name = dp_description = None

                    if dp_urn and dp_name:
                        # Use URN as key to ensure uniqueness
                        unique_data_products[dp_urn] = {
                            "name": dp_name,
                            "description": dp_description or "",
                            "urn": dp_urn,
                        }

        return list(unique_data_products.values())

    except Exception:
        # Return empty list if search fails
        return []
