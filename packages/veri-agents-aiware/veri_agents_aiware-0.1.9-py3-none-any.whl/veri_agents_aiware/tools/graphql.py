from abc import abstractmethod

from graphql import OperationDefinitionNode, OperationType, build_client_schema, get_introspection_query, parse, print_schema, GraphQLSchema
import requests
import logging
from typing import Optional, Tuple, Any, Type

from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field

log = logging.getLogger(__name__)


def filter_none_values(data) -> dict | list:
    if isinstance(data, dict):
        return {k: filter_none_values(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [filter_none_values(item) for item in data]
    return data


class AiWareExecuteOperationToolInput(BaseModel):
    """Input for the aiWARE tool."""

    gql_query: str = Field(
        description="GraphQL query to execute against Veritone aiWARE."
    )
    variables: dict[str, Any] = Field(
        description="Variables for graphql query"
    )
    # aiware_api_key: Annotated[Optional[str], InjectedToolArg] = Field(
    #    description="Possibly injected aiWARE API key."
    # )


class _BaseAiwareTool(BaseTool):
    aiware_api_key: Optional[str]
    aiware_url: Optional[str]

    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    allow_mutation: bool = False

    def _execute_query(self, config: RunnableConfig | None, gql_query: str, variables: dict[str, Any], aiware_session_token: Optional[str]) -> dict:
        """Execute the aiWARE GraphQL query."""

        # get session_token from runnable config
        if config:
            aiware_session_token = aiware_session_token or config.get("configurable", {}).get("aiware_session_token")

        # # TODO: hack :)
        # if not self.allow_mutation and "mutation" in gql_query:
        #     raise ToolException("Mutation not supported.")

        aiware_session_token = aiware_session_token or self.aiware_api_key
        if not aiware_session_token:
            raise ToolException("aiWARE API key not set.")
        if not self.aiware_url:
            raise ToolException("aiWARE URL not set.")

        headers = {
            "Authorization": f"Bearer {aiware_session_token}",
            "Content-Type": "application/json",
        }
        payload = {"query": gql_query, "variables": variables}

        document = parse(source=gql_query)
        
        for definition in document.definitions:
            if isinstance(definition, OperationDefinitionNode):
                if definition.operation == OperationType.MUTATION and not self.allow_mutation or definition.operation == OperationType.SUBSCRIPTION:
                    raise Exception(f"Operation type not supported: {definition.operation}")
        
        # graphql.validation.validate?

        response = requests.post(
            self.aiware_url,
            json=payload,
            headers=headers,
        )
        if response.status_code != 200:
            raise ToolException(f"Error: {response.status_code} - {response.text}")

        return response.json()

    @abstractmethod
    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Use the tool.

        Add run_manager: Optional[CallbackManagerForToolRun] = None
        to child implementations to enable tracing.
        """


class AiWareExecuteOperationTool(_BaseAiwareTool):
    """Generic aiWARE GraphQL tool."""

    name: str = "aiware_tool"
    description: str = "Performs GraphQL calls to Veritone aiWARE. Use this tool if you have no other, more specialized aiWARE tool. Before using this tool, pull the schema using the aiware_tool_schema tool. Use as few output arguments as possible."
    args_schema: Type[BaseModel] = AiWareExecuteOperationToolInput # pyright: ignore[reportIncompatibleVariableOverride]

    allow_mutation: bool = False

    def execute_query(self, gql_query: str, variables: dict[str, Any] = {}, aiware_session_token: Optional[str] = None, config: RunnableConfig | None = None) -> dict:
        return self._execute_query(
            gql_query=gql_query,
            variables=variables,
            aiware_session_token=aiware_session_token,
            config=config
        )

    def _run(
        self,
        config: RunnableConfig | None,
        gql_query: str,
        variables: dict[str, Any] = {},
        aiware_session_token: Optional[str] = None
    ) -> Tuple[str, dict]:
        """Run the aiWARE GraphQL query."""
        result = self._execute_query(config=config, gql_query=gql_query, variables=variables, aiware_session_token=aiware_session_token)
        return str(result), {"items": result, "type": "json", "source": "aiware"}


class AiWareIntrospectSchemaToolInput(BaseModel):
    # TODO: aiware api key, perhaps which category of fields to pull
    pass


class AiWareIntrospectSchemaTool(_BaseAiwareTool):
    """Tool to get aiWARE schema."""

    name: str = "aiware_tool_schema"
    description: str = "Get aiWARE GraphQL schema. Use this tool to get the schema of the aiWARE GraphQL API."
    args_schema: Type[BaseModel] = AiWareIntrospectSchemaToolInput # pyright: ignore[reportIncompatibleVariableOverride]

    def get_schema(self, config: RunnableConfig | None = None) -> tuple[str, GraphQLSchema]:
        introspection_query = get_introspection_query(
            descriptions=True,
            specified_by_url=False,
            directive_is_repeatable=True,
            schema_description=True,
            input_value_deprecation=True
        )

        result = self._execute_query(
            gql_query=introspection_query,
            config=config,
            variables={},
            aiware_session_token=None
        )

        schema = build_client_schema(result["data"])

        # TODO: filter just queries

        return (print_schema(schema), schema)

    def _run(self, config: RunnableConfig) -> Tuple[str, dict]:
        (schema_sdl, schema) = self.get_schema(config=config)
        return schema_sdl, {"schema_sdl": schema_sdl, "type": "graphql-schema", "source": "aiware"}


# TODO: end to end tool to generate query
