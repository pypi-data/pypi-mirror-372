import graphql
import json
import os

import requests

# PROD  US-1 https://api.us-1.veritone.com/v3/graphql
# PROD  UK-1 https://api.uk-1.veritone.com/v3/graphql
# STAGE US-1 https://api.stage.us-1.veritone.com/v3/graphql
# AISGLABS   https://aisglabs1.aiware.run/v3/graphql


class GraphQLQueryError(Exception):
    """Exception to throw when GraphQL queries fail ("errors" in JSON response)."""

    pass


class GraphQLContext:
    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
    ):
        # Precedence:
        # 1. Function arguments
        # 2. Environment variables
        # 3. Default values
        if url is not None:
            self.url = url
        else:
            self.url = os.getenv(
                "GRAPHQL_URL", "https://api.us-1.veritone.com/v3/graphql"
            )
        if token is not None:
            self.token = token
        else:
            self.token = os.getenv("AIWARE_TOKEN", None)

    def run_query(self, query: str, variables: dict = {}, raise_on_error=True) -> dict:
        # Check query
        # This will raise an error if the query is invalid, before even making the request to the server
        graphql.parse(query)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        payload = {"query": query, "variables": variables}
        response = requests.post(self.url, json=payload, headers=headers)

        # Check for HTTP errors
        response.raise_for_status()

        result = response.json()

        # Check for GraphQL errors
        if raise_on_error and "errors" in result:
            raise GraphQLQueryError(
                f"GraphQL query failed with errors: {result['errors']}"
            )

        return result

    def me_query(self) -> dict:
        query = """
        query {
            me {
                id
                email
                firstName
                lastName
                organization {
                    id
                    name
                }
            }
        }
        """
        return self.run_query(query)


if __name__ == "__main__":
    context = GraphQLContext()
    user_info = context.me_query()
    print(json.dumps(user_info, indent=2))
