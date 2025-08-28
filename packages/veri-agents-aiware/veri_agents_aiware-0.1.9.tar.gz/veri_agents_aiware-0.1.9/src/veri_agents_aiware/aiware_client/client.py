from typing import Optional
from veri_agents_aiware.aiware_client.graphql.client_generated.client import (
    AgentsAiwareGraphQL,
)
from aiware.client import Aiware as _Aiware
from aiware.common.auth import AbstractTokenAuth
from aiware.search.client import AiwareSearch


class AgentsAiware(_Aiware[AgentsAiwareGraphQL, AiwareSearch]):
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
            graphql_factory=lambda endpoint, auth: AgentsAiwareGraphQL(endpoint, auth),
            auth=auth,
        )
