import inspect

import altair
import langchain.tools
import langchain_core.language_models
import langchain_core.messages
import langgraph.prebuilt
import pandas as pd

from ai_app.ai_utils import PreModelHook
from ai_app.config import get_config, get_engine, get_sql_toolkit
from ai_app.core import Response, State
from ai_app.tools import extract_tool_artifacts_from_agent_response


def get_system_prompt() -> str:
    prompt = inspect.cleandoc("""
    You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct query to run, then look 
    at the results of the query and return the answer.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the below tools. Only use the information returned by the below tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite 
    the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    To start you should ALWAYS look at the tables in the database to see what you can query.
    Do NOT skip this step.
    Then you should query the schema of the most relevant tables.

    When referring to table columns, always quote them with double quotes, like "Metric" or "Date".
    """)  # noqa: E501
    return prompt


class Bot:
    async def respond(
        self,
        model: langchain_core.language_models.BaseChatModel,
        message: langchain_core.messages.BaseMessage,
        frontend_messages: list[langchain_core.messages.BaseMessage],
        state: State,
        connection_context_name: str,
    ) -> Response:
        connection_context = get_config().sql_connection_contexts[connection_context_name]
        engine = get_engine(connection_context.connection_name)

        @langchain.tools.tool(response_format="content_and_artifact")
        def display_altair_chart(
            vega_lite_json_spec: str,
            sql_query: str,
        ) -> tuple[str, str]:
            """
            Display a single chart from a Vega-Lite JSON specification and a SQL query.
            The connection name can be determined by calling the get_database_info tool of an SQL MCP.
            Refer to data source as "sql_query", for example:
            ```json
            {
            "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
            "data": {"name": "sql_query"},
            "title": "My Bar Chart",
            "mark": "bar",
            "encoding": {
                "x": {"field": "category", "type": "nominal", "title": "Category"},
                "y": {"field": "value", "type": "quantitative", "title": "Value"},
                "color": {"field": "group", "type": "nominal", "title": "Group"}
            },
            "width": 400,
            "height": 300
            }
            ```
            Spaces in the example JSON are just for human readability, when generating the real JSON,
            omit all spaces.

            Column names in both the JSON spec and the SQL query should be lowercase and quoted.
            """
            # Reference: https://vega.github.io/vega-lite
            sql_query = sql_query.strip().strip(";")
            df = pd.read_sql(sql_query, engine)
            chart = altair.Chart.from_json(vega_lite_json_spec)
            chart.data = df

            response = "HTML displayed."
            return response, chart

        toolkit = get_sql_toolkit(connection_context_name)
        agent = langgraph.prebuilt.create_react_agent(
            model=model,
            pre_model_hook=PreModelHook(model),
            tools=toolkit.get_tools() + [display_altair_chart],
            prompt=get_system_prompt(),
        )
        response: dict = await agent.ainvoke({"messages": frontend_messages + [message]})
        response_messages = response["messages"]
        response_content = response_messages[-1].content

        artifacts = extract_tool_artifacts_from_agent_response(response_messages)
        artifacts = artifacts.get(display_altair_chart.name)
        plot = artifacts[-1] if artifacts else None

        return Response(content=response_content, additional_outputs=[plot])
