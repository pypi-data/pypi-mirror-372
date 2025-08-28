from typing import Optional
from veri_agents_aiware.aiware_client.graphql.client_generated.async_client import AsyncAgentsAiwareGraphQL
from aiware.async_client import AsyncAiware as _AsyncAiware
from aiware.search.async_client import AsyncAiwareSearch
from aiware.common.auth import AbstractTokenAuth

class AsyncAgentsAiware(_AsyncAiware[AsyncAgentsAiwareGraphQL, AsyncAiwareSearch]):
    def __init__(
        self,
        *,
        graphql_endpoint: str,
        search_endpoint: str,
        auth: Optional[AbstractTokenAuth],
    ):
        super().__init__(
            graphql_endpoint=graphql_endpoint,
            search_endpoint=search_endpoint,
            graphql_factory=lambda endpoint, auth: AsyncAgentsAiwareGraphQL(endpoint, auth),
            auth=auth,
        )
