import json

import httpx
from loguru import logger
from mcp.server.fastmcp import Context

from solargis.documentation_mcp_server.models import SearchResult
from solargis.documentation_mcp_server.utils import (
    paginate_documentation_result,
    to_markdown,
)

SEARCH_INFO_API = "https://kb.solargis.com/api/search/get-search-info"
SEARCH_API_BASE = "https://{application_id}-dsn.algolia.net/1/indexes/{index_name}/query"
KB_DOC_JSON_API_BASE = "https://kb.solargis.com/api/document/get-article-body?article-slug={slug}&x-versiontype=Knowledgebase"


async def read_kb_documentation_impl(
    ctx: Context,
    url: str,
    max_length: int,
    start_index: int,
    session_uuid: str,
) -> str:
    logger.debug(f"Fetching documentation from {url}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url=url,
                headers={
                    "X-MCP-Session-Id": session_uuid,
                },
                timeout=30,
            )
        except httpx.HTTPError as e:
            error_msg = f"Failed to fetch {url}: {str(e)}"
            logger.error(error_msg)
            await ctx.error(error_msg)
            return error_msg

        if response.status_code >= 400:
            error_msg = f"Failed to fetch {url} - status code {response.status_code}"
            logger.error(error_msg)
            await ctx.error(error_msg)
            return error_msg

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            error_msg = f"Error parsing fetch results: {str(e)}"
            logger.error(error_msg)
            await ctx.error(error_msg)
            return error_msg

        block_content = data["result"]["articleData"]["articleContentForSsr"]
        content = to_markdown(block_content)
        result = paginate_documentation_result(url, content, start_index, max_length)

        if len(content) > start_index + max_length:
            logger.debug(f"Content truncated at {start_index + max_length} of {len(content)} characters")

        return result


async def search_kb_documentation_impl(
    ctx: Context,
    search_phrase: str,
    limit: int,
    session_uuid: str,
) -> list[SearchResult]:
    logger.debug(f"Searching Solargis documentation for: {search_phrase}")

    async with httpx.AsyncClient() as client:
        try:
            search_info_response = await client.get(
                url=SEARCH_INFO_API,
                headers={
                    "X-MCP-Session-Id": session_uuid,
                },
                timeout=30,
            )
        except httpx.HTTPError as e:
            error_msg = f"Error searching Solargis docs: {str(e)}"
            logger.error(error_msg)
            await ctx.error(error_msg)
            return [
                SearchResult(
                    rank_order=1,
                    url="",
                    title=error_msg,
                    breadcrumb="",
                ),
            ]

        if search_info_response.status_code >= 400:
            error_msg = f"Error searching Solargis docs - status code {search_info_response.status_code}"
            logger.error(error_msg)
            await ctx.error(error_msg)
            return [
                SearchResult(
                    rank_order=1,
                    url="",
                    title=error_msg,
                    breadcrumb="",
                )
            ]

        try:
            search_info_data = search_info_response.json()
        except json.JSONDecodeError as e:
            error_msg = f"Error parsing search results: {str(e)}"
            logger.error(error_msg)
            await ctx.error(error_msg)
            return [
                SearchResult(
                    rank_order=1,
                    url="",
                    title=error_msg,
                    breadcrumb="",
                ),
            ]

    application_id = search_info_data["algoliaAppId"]
    index_name = search_info_data["algoliaArticlesIndexId"]
    api_key = search_info_data["algoliaSearchKey"]

    async with httpx.AsyncClient() as client:
        request_body = {
            "query": search_phrase,
            "page": 0,
            "attributesToRetrieve": [
                "title",
                "slug",
                "isCategory",
                "breadcrumb",
            ],
            "hitsPerPage": limit,
            "analytics": False,
            "filters": "(languageId:f8cd6cda-aa49-4e95-be69-a921517b8e43) AND (NOT isPrivate:true) AND (NOT isDeleted:true AND isDraft:false AND exclude:false AND isHidden:false AND NOT isCategoryHidden:true) AND (NOT isUnpublished:true)",
        }

        try:
            response = await client.post(
                url=SEARCH_API_BASE.format(application_id=application_id, index_name=index_name),
                json=request_body,
                headers={
                    "Content-Type": "application/json",
                    "X-Algolia-Api-Key": api_key,
                    "X-Algolia-Application-Id": application_id,
                    "X-MCP-Session-Id": session_uuid,
                },
            )
        except httpx.HTTPError as e:
            error_msg = f"Error searching Solargis docs: {str(e)}"
            logger.error(error_msg)
            await ctx.error(error_msg)
            return [
                SearchResult(
                    rank_order=1,
                    url="",
                    title=error_msg,
                    breadcrumb="",
                ),
            ]

        if response.status_code >= 400:
            error_msg = f"Error searching Solargis docs - status code {response.status_code}"
            logger.error(error_msg)
            await ctx.error(error_msg)
            return [
                SearchResult(
                    rank_order=1,
                    url="",
                    title=error_msg,
                    breadcrumb="",
                )
            ]

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing search results: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        return [
            SearchResult(
                rank_order=1,
                url="",
                title=error_msg,
                breadcrumb="",
            )
        ]

    results = []
    for i, hit in enumerate(data["hits"]):
        if hit["isCategory"]:
            # do not return category pages
            continue

        url = KB_DOC_JSON_API_BASE.format(slug=hit["slug"])
        results.append(
            SearchResult(
                rank_order=i,
                url=url,
                title=hit["title"],
                breadcrumb=hit["breadcrumb"],
            )
        )

    logger.debug(f"Found {len(results)} search results for: {search_phrase}")
    return results
