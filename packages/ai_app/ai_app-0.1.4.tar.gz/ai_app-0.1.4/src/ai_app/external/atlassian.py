import enum
import json
import logging
import re
import urllib
import warnings

import atlassian
import bidict
import polars as pl
import tqdm.auto

from ai_app.utils import filter_dict_by_keys, get_number_of_batches


def get_jira_base_url() -> str:
    return "http://jira-support.kapitalbank.az"


def fetch_all_jira_project_keys(jira: atlassian.Jira) -> list[str]:
    projects = jira.get_all_projects()
    projects = pl.DataFrame(projects, infer_schema_length=None)
    project_keys = sorted(set(projects["key"]))
    return project_keys


def fetch_all_jira_usernames(jira: atlassian.Jira) -> list[str]:
    start = 0
    users = []
    while True:
        batch_users = jira.user_find_by_user_string(username=".", start=start, limit=500)
        if not batch_users:
            break

        start += len(batch_users)
        users.extend(batch_users)

    users = pl.DataFrame(users, infer_schema_length=None)
    usernames = sorted(set(users["name"]))
    return usernames


def build_issue_url(issue_key: str, base_url: str | None = None) -> str:
    base_url = base_url or get_jira_base_url()
    issue_url = f"{base_url}/browse/{issue_key}"
    return issue_url


class IssueLink(enum.StrEnum):
    tests = "Tests"
    has_to_be_done_before = "Has to be done before"

    def get_link_type(self):
        link_types = {
            IssueLink.has_to_be_done_before: "Gantt End to Start",
            IssueLink.tests: "Tests",
        }
        link_type = link_types[self]
        return link_type

    def link_issues(self, jira: atlassian.Jira, inward_issue: str, outward_issue: str) -> None:
        jira.create_issue_link(
            {
                "type": {"name": self.get_link_type()},
                "inwardIssue": {"key": inward_issue},
                "outwardIssue": {"key": outward_issue},
            }
        )


def extract_jira_issue_fields(issue: dict, max_length: int | None = None) -> dict[str, str]:
    extracted_fields = {}
    for key, value in issue["fields"].items():
        match key:
            case "issuetype":
                value = value["name"]

        value = value[:max_length] if max_length and value else value
        extracted_fields[key] = value

    return extracted_fields


def get_service_desks(service_desk: atlassian.ServiceDesk) -> dict:
    service_desks = service_desk.get_service_desks()
    service_desks = {int(i["id"]): i for i in service_desks}
    return service_desks


def generate_from_pages(
    service_desk: atlassian.ServiceDesk,
    path: str,
    limit: int | None = None,
    verbose: bool = False,
    tqdm_description="Fetching pages",
    **kwargs,
):
    progress_bar = tqdm.auto.tqdm(desc=tqdm_description, disable=not verbose)
    start = 0
    while True:
        response = service_desk.get(path, params=dict(start=start), **kwargs)
        start += response["size"]
        yield from response["values"]
        progress_bar.update()
        if response["isLastPage"] or limit and start > limit:
            progress_bar.close()
            return


def get_service_desks_request_types(
    service_desk: atlassian.ServiceDesk,
    service_desk_id: int,
    tqdm_description="Fetching request types",
    verbose: bool = False,
) -> dict:
    """Collect all request types for given service desk."""
    request_types = generate_from_pages(
        service_desk,
        f"/rest/servicedeskapi/servicedesk/{service_desk_id}/requesttype",
        tqdm_description=tqdm_description,
        verbose=verbose,
    )
    request_types = {int(i["id"]): i for i in request_types}
    return request_types


def build_request_url(
    service_desk_id: int, request_type_id: int, base_url: str | None = None, **parameters
) -> str:
    base_url = base_url or get_jira_base_url()
    url = f"{base_url}/servicedesk/customer/portal/{service_desk_id}/create/{request_type_id}"
    if parameters:
        query = urllib.parse.urlencode(parameters)
        url += f"?{query}"

    return url


def generate_jql_issues(
    jira: atlassian.Jira,
    jql: str,
    verbose: bool = False,
    fields: list[str] | str | None = None,
    expand: list[str] | str | None = None,
    soft_limit: int | None = None,
):
    def to_expected_jira_format(value: list[str] | str | None = None):
        value = value if value is None or isinstance(value, str) else ",".join(value)
        return value

    progress_bar = tqdm.auto.tqdm(desc="Fetching issue pages", disable=not verbose)
    fetched_issues_count = 0
    soft_limit = soft_limit or float("inf")
    while fetched_issues_count < soft_limit:
        try:
            response = jira.jql(
                jql,
                start=fetched_issues_count,
                fields=to_expected_jira_format(fields),
                expand=to_expected_jira_format(expand),
                limit=min(soft_limit, 50),
            )
        except Exception:
            logging.error(f"Failed to fetch issues from JQL: {jql}")
            raise

        fetched_issues_count += len(response["issues"])
        soft_limit = int(min(soft_limit, response["total"]))
        if not progress_bar.total:
            progress_bar.total = get_number_of_batches(soft_limit, response["maxResults"])

        progress_bar.update()
        yield from response["issues"]

    progress_bar.close()


def normalize_line_breaks(string: str) -> str:
    string = string.replace("\r\n", "\n")
    string = re.sub(r"\n+", r"\n", string)
    return string


def try_inferring_jira_field_representation(
    value, dict_key_preference=("displayName", "name", "value", "key")
):
    def recursive_infer(value):
        if isinstance(value, list):
            value = [recursive_infer(i) for i in value]
            if all(isinstance(i, str) for i in value):
                value = ", ".join(value)

        if isinstance(value, dict):
            for key in dict_key_preference:
                if key in value:
                    value = value[key]
                    value = recursive_infer(value)
                    return value

        return value

    value = recursive_infer(value)
    return value


def extract_issue_field_values(issue: dict, include_issue_key: bool = True) -> dict:
    values = {}
    if include_issue_key:
        values["Issue key"] = issue["key"]

    for field, value in issue["fields"].items():
        if not value:
            values[field] = None
            continue

        match field:
            case "issuetype" | "priority" | "status" | "resolution":
                value = value["name"]
            case (
                "customfield_20163"
                | "customfield_20901"
                | "customfield_20902"
                | "customfield_20906"
                | "customfield_23001"
                | "customfield_23101"
                | "customfield_23608"
                | "customfield_23609"
                | "customfield_23710"
                | "customfield_23712"
                | "customfield_15542"
                | "customfield_24810"
                | "customfield_23109"
            ):
                value = value["value"]
            case "project":
                value = value["key"]
            case (
                "labels"
                | "customfield_20160"
                | "customfield_20800"
                | "customfield_20164"
                | "customfield_20118"
                | "customfield_11626"
                | "customfield_11300"
            ):
                value = ", ".join(value)
            case "components" | "customfield_20145" | "customfield_10300":
                value = ", ".join(i["name"] for i in value)
            case "assignee" | "reporter":
                value = value["displayName"]
            case "comment":
                value = sorted(value["comments"], key=lambda c: c["created"])
                value = [c["body"] for c in value]
                value = json.dumps(value)

        value = try_inferring_jira_field_representation(value)

        valid_types = [type(None), int, float, str]
        if not any(isinstance(value, t) for t in valid_types):
            raise ValueError(
                f"Processed field '{field}' has unexpected type {type(value)}:\n{value}"
            )

        if isinstance(value, str):
            value = normalize_line_breaks(value)

        values[field] = value

    return values


def get_request_fields(
    service_desk: atlassian.ServiceDesk, service_desk_id: int, request_type_id: int
) -> pl.DataFrame | None:
    response = service_desk.get(
        path=f"/rest/servicedeskapi/servicedesk/{service_desk_id}/requesttype/{request_type_id}/field",
    )
    df = pl.DataFrame(response["requestTypeFields"])
    if df.is_empty():
        return

    can_be_passed_as_url_parameter = {
        "any": False,
        "array": False,
        "date": True,  # in format 1/Apr/25, https://jira-support.kapitalbank.az/servicedesk/customer/portal/21/create/2495
        "datetime": True,  # in format 1/Apr/25 09:56 AM, https://jira-support.kapitalbank.az/servicedesk/customer/portal/21/create/2495
        "option": True,
        "priority": True,  # similar to option, https://jira-support.kapitalbank.az/servicedesk/customer/portal/21/create/5155
        "string": True,
        "user": False,  # similar to any, https://jira-support.kapitalbank.az/servicedesk/customer/portal/21/create/2018
        "number": True,  # just string with frontend/backend validation https://jira-support.kapitalbank.az/servicedesk/customer/portal/1/create/2287
        "BundledFields": False,  # Kampaniyanın keçirilmə aralığı in https://jira-support.kapitalbank.az/servicedesk/customer/portal/1/create/1838
    }
    field_type_expr = pl.col("jiraSchema").struct["type"]
    if field_types := (set(df.select(field_type_expr.unique()).to_series())) - set(
        can_be_passed_as_url_parameter
    ):
        warnings.warn(
            f"Unexpected field types: {field_types} for service desk {service_desk_id} "
            f"and request type {request_type_id}\n"
            f"Request URL: {build_request_url(service_desk_id, request_type_id)}"
        )

    df = df.with_columns(
        field_type_expr.replace_strict(can_be_passed_as_url_parameter, default=False).alias(
            "can_be_passed_as_url_parameter"
        ),
    )
    try:
        df = df.sort("fieldId").with_columns(
            pl.col("validValues")
            .explode()
            .struct["label"]
            .drop_nulls()
            .implode()
            .over("fieldId", order_by="fieldId")
            .alias("valid_value_labels")
        )
    except pl.exceptions.StructFieldNotFoundError:
        df = df.with_columns(pl.lit(None, dtype=list[str]).alias("valid_value_labels"))

    df = df.with_columns(
        pl.when(pl.col("valid_value_labels").list.len() > 0).then("valid_value_labels")
    )
    return df


def get_request_field_names(
    service_desk: atlassian.ServiceDesk, service_desk_id: int, request_type_id: int
) -> bidict.bidict:
    """Returns field id to name bidict, keeps the largest field id if names are duplicated."""
    request_field_names = bidict.bidict()
    request_fields = get_request_fields(service_desk, service_desk_id, request_type_id)
    if request_fields is None:
        return request_field_names

    request_fields = request_fields.sort("fieldId").unique("name", keep="last")
    request_field_names.putall(
        (row["fieldId"], row["name"]) for row in request_fields.iter_rows(named=True)
    )
    return request_field_names


def build_new_request_url_similar_to_given(
    jira: atlassian.Jira, service_desk: atlassian.ServiceDesk, issue_key: str
) -> str:
    """Note that partial url parameters don't work for fields which are linked to Jira assets."""
    issue = jira.issue(issue_key)
    request_type = issue["fields"]["customfield_10202"]["requestType"]
    service_desk_id = int(request_type["serviceDeskId"])
    request_type_id = int(request_type["id"])
    fields = get_request_fields(service_desk, service_desk_id, request_type_id)
    fields = list(fields["fieldId"])
    fields = {f: issue["fields"][f] for f in fields}
    fields = {
        k: try_inferring_jira_field_representation(
            v, dict_key_preference=["displayName", "id", "name", "value", "key"]
        )
        for k, v in fields.items()
    }
    url = build_request_url(service_desk_id, request_type_id, **fields)
    return url


def build_jql_last_resolved(project_key: str) -> str:
    """Latest resolved issues, ordered by resolution time descending."""
    return f"project = {project_key} AND resolutiondate IS NOT EMPTY ORDER BY resolutiondate DESC"


def build_jql_current_open(project_key: str) -> str:
    """Currently open issues. Using resolution = Unresolved is robust across workflows."""
    return f"project = {project_key} AND resolution = Unresolved ORDER BY created DESC"


def get_project_overview(
    jira: atlassian.Jira,
    project_key: str,
    resolved_issues_count: int = 10,
    unresolved_issues_count: int = 10,
    issue_fields: list[str] = (
        "summary",
        "description",
        "issuetype",
        "priority",
        "comment",
    ),
) -> dict:
    # TODO: Add project boards, add fields:
    # "issuelinks",
    # "parent",
    # "subtasks",
    #  Epic links
    project = jira.project(project_key, expand="description")
    project = filter_dict_by_keys(project, ["key", "name", "description"])
    jqls = {
        "resolved": (
            f"""
                project = {project_key} AND resolutiondate IS NOT EMPTY
                ORDER BY resolutiondate DESC
            """,
            resolved_issues_count,
        ),
        "unresolved": (
            f"""
                project = {project_key} AND resolution = Unresolved
                ORDER BY created DESC
            """,
            unresolved_issues_count,
        ),
    }
    for kind, (jql, limit) in jqls.items():
        issues = []
        for issue in generate_jql_issues(jira, jql, fields=issue_fields, soft_limit=limit):
            if comments := issue["fields"].pop("comment", None):
                comments = sorted(comments["comments"], key=lambda c: c["created"])
                comments = [c["body"] for c in comments]

            issue = extract_issue_field_values(issue)
            issue["comments"] = comments
            issues.append(issue)

        project[f"{kind}_issues"] = issues

    return project
