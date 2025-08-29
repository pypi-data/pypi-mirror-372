import contextlib
import enum
import re
import string

import certifi
import gitlab as gl
import httpx
import pydantic

from ai_app.utils import PydanticForbidExtra, filter_dict_by_keys, try_match_regex, value_to_key


class GitlabUrl(enum.StrEnum):
    # Urls may have different permissions.
    gitlab = "https://gitlab.kapitalbank.az"
    dr_gitlab = "https://dr-gitlab.kapitalbank.az"


def build_gitlab_client(
    url: GitlabUrl = GitlabUrl.gitlab,
    private_token: str | None = None,
    verbose: bool = False,
) -> gl.Gitlab:
    gitlab = gl.Gitlab(
        url=url,
        private_token=private_token,
        ssl_verify=certifi.where(),
        keep_base_url=url != GitlabUrl.gitlab,
    )
    if verbose:
        gitlab.enable_debug()

    return gitlab


def build_gitlab_async_graphql_client(
    url: GitlabUrl = GitlabUrl.gitlab,
    private_token: str | None = None,
) -> gl.AsyncGraphQL:
    """
    Docs: https://docs.gitlab.com/api/graphql/
    Local instance GraphQL explorer: https://gitlab.kapitalbank.az/-/graphql-explorer
    """
    graphql = gl.AsyncGraphQL(
        url=url,
        token=private_token,
        ssl_verify=certifi.where(),
    )
    return graphql


def build_httpx_client(
    url: GitlabUrl = GitlabUrl.gitlab,
    private_token: str | None = None,
):
    headers = {"PRIVATE-TOKEN": private_token}
    client = httpx.AsyncClient(headers=headers, base_url=url)
    return client


class GraphqlGlobalId(PydanticForbidExtra):
    """
    GitLab GraphQL often uses global ids for object identifiers,
    see https://docs.gitlab.com/api/graphql/#global-ids
    """

    global_id: str
    schema_: str = pydantic.Field(alias="schema")
    provider: str
    path: list[str]
    entity_id: int

    @staticmethod
    def from_global_id(global_id: str):
        schema, path = global_id.split("://")
        provider, *path, entity_id = path.split("/")
        global_id = GraphqlGlobalId(
            global_id=global_id,
            schema=schema,
            provider=provider,
            path=path,
            entity_id=int(entity_id),
        )
        return global_id


async def get_project_id_from_path(graphql: gl.AsyncGraphQL, project: str) -> int:
    query = """
        query {
            project(fullPath: "$project") {
                id
            }
        }
    """
    result = await execute_parametrized_graphql_query(graphql, query, project=project)
    global_id = result["project"]["id"]
    global_id = GraphqlGlobalId.from_global_id(global_id)
    return global_id.entity_id


def get_gitlab_project_url_pattern() -> str:
    base_url_pattern = "|".join(re.escape(u) for u in GitlabUrl)
    pattern = rf"(?P<base_url>{base_url_pattern})/?(?P<project_path>[\w\-/]+)"
    return pattern


def get_gitlab_merge_request_url_pattern() -> str:
    pattern = rf"{get_gitlab_project_url_pattern()}/-/merge_requests/(?P<merge_request_iid>\d+)"
    return pattern


def gitlab_project_url_to_path(project_url: str) -> str:
    """
    For example, from
        https://gitlab.kapitalbank.az/kapitalbankojsc/birbank/birbank-payments/birbank-payments/ms-product-usage/
    to
        kapitalbankojsc/birbank/birbank-payments/birbank-payments/ms-product-usage
    """
    pattern = get_gitlab_project_url_pattern()
    match = try_match_regex(pattern, project_url, flags=re.ASCII)
    project_path = match.groupdict()["project_path"].strip("/")
    return project_path


class MergeRequest(pydantic.BaseModel):
    project_path: str
    merge_request_iid: int

    @staticmethod
    def from_url(merge_request_url: str):
        """For example, from https://gitlab.kapitalbank.az/kapitalbankojsc/birbank/birbank-payments/birbank-payments/ms-product-usage/-/merge_requests/4"""
        pattern = get_gitlab_merge_request_url_pattern()
        match = try_match_regex(pattern, merge_request_url, flags=re.ASCII)
        project_path = match.groupdict()["project_path"]
        merge_request_iid = int(match.groupdict()["merge_request_iid"])
        merge_request = MergeRequest(project_path=project_path, merge_request_iid=merge_request_iid)
        return merge_request


def get_merge_request_diffs(gitlab: gl.Gitlab, project: str, merge_request_iid: int) -> dict:
    project = gitlab.projects.get(project)
    merge_request = project.mergerequests.get(merge_request_iid)
    # https://docs.gitlab.com/api/merge_requests/#get-single-merge-request-changes
    changes = merge_request.changes(access_raw_diffs=True, unidiff=True)
    changes = [
        filter_dict_by_keys(change, ["old_path", "new_path", "diff"])
        for change in changes["changes"]
    ]
    merge_request = filter_dict_by_keys(merge_request.asdict(), ["title", "description"])
    merge_request |= {"changes": changes}
    return merge_request


async def aget_merge_request_diffs(
    gitlab: gl.Gitlab,
    project: str,
    merge_request_iid: int,
    graphql: gl.AsyncGraphQL | None = None,
    httpx_client: httpx.AsyncClient | None = None,
    access_raw_diffs: bool = True,
    unidiff: bool = True,
) -> dict:
    """https://docs.gitlab.com/api/merge_requests/#get-single-merge-request-changes"""
    gitlab_kwargs = dict(url=gitlab.url, private_token=gitlab.private_token)
    graphql = graphql or build_gitlab_async_graphql_client(**gitlab_kwargs)
    project_id = await get_project_id_from_path(graphql, project)

    changes_url = f"api/v4/projects/{project_id}/merge_requests/{merge_request_iid}/changes"
    if httpx_client:
        # Do not take responsibility to close httpx_client if it is provided.
        context = contextlib.nullcontext()
    else:
        httpx_client = context = build_httpx_client(**gitlab_kwargs)
    async with context:
        response = await httpx_client.get(
            changes_url, params=dict(access_raw_diffs=access_raw_diffs, unidiff=unidiff)
        )

    response.raise_for_status()
    merge_request = response.json()
    merge_request = filter_dict_by_keys(merge_request, ["title", "description", "changes"])
    merge_request["changes"] = [
        filter_dict_by_keys(change, ["old_path", "new_path", "diff"])
        for change in merge_request["changes"]
    ]
    return merge_request


async def execute_parametrized_graphql_query(
    graphql: gl.AsyncGraphQL, query: str, **parameters
) -> dict:
    query = string.Template(query).substitute(parameters)
    result = await graphql.execute(query)
    return result


async def get_all_schema_types(graphql: gl.AsyncGraphQL) -> dict[str, str]:
    query = """
        query {
            __schema {
                types {
                    name
                    kind
                }
            }
        }
    """
    result = await graphql.execute(query)
    types = value_to_key(result["__schema"]["types"], "name")
    return types


async def get_all_entity_type_fields(
    graphql: gl.AsyncGraphQL, entity_type: str, include_datatype_metadata: bool = False
) -> dict:
    """Note that entity_type is case-sensitive."""
    datatype_metadata = """
        type {
            name
            kind
            ofType {
                name
                kind
            }
        }
    """
    query = """
        query {
        __type(name: "$entity_type") {
            fields {
                name
                description
                $datatype_metadata
                args {
                    name
                    description
                    $datatype_metadata
                }
            }
        }
    }
    """
    result = await execute_parametrized_graphql_query(
        graphql,
        query,
        entity_type=entity_type,
        datatype_metadata=datatype_metadata if include_datatype_metadata else "",
    )
    fields = result["__type"]["fields"]
    for field in fields:
        field["args"] = value_to_key(field["args"], "name")

    fields = value_to_key(fields, "name")
    return fields


async def get_merge_request_commits(
    graphql: gl.AsyncGraphQL, project: str, merge_request_iid: int, first: int = 1
) -> list:
    query = """
        query {
            project(fullPath: "$project") {
                mergeRequest(iid: "$merge_request_iid") {
                    commits(first: $first) {
                        nodes {
                            title
                            message
                            diffs {
                                oldPath
                                newPath
                                diff
                            }
                        }
                    }
                }
            }
        }
    """
    result = await execute_parametrized_graphql_query(
        graphql, query, project=project, merge_request_iid=merge_request_iid, first=first
    )
    commits = result["project"]["mergeRequest"]["commits"]["nodes"]
    return commits
