import os
import unittest
from veri_agents_aiware.tools import AiWareExecuteOperationTool, AiWareIntrospectSchemaTool


class TestAiWareTool(unittest.TestCase):
    def setUp(self):
        # Initialize the AiWareTool instance before each test
        self.aiware_api_key = os.getenv("AIWARE_API_KEY")
        self.aiware_url = f"{os.getenv('AIWARE_BASE_URL')}/v3/graphql"

        self.aiware_schema_tool = AiWareIntrospectSchemaTool(
            aiware_api_key=self.aiware_api_key,
            aiware_url=self.aiware_url
        )

        self.aiware_tool = AiWareExecuteOperationTool(
            aiware_api_key=self.aiware_api_key,
            aiware_url=self.aiware_url
        )

    def test_get_schema(self):
        # Test the get_schema method
        schema_sdl, _schema = self.aiware_schema_tool.get_schema()
        print(schema_sdl)
        self.assertIsNotNone(schema_sdl)
        # self.assertTrue("temporalDataObjects" in str(schema))

    def test_operation(self):
        me_res = self.aiware_tool.execute_query(gql_query="""query me {
                                                me {
                                                    id
                                                }
                                            }""")
        print(me_res)
        self.assertIsNotNone(me_res["data"]["me"]["id"])


if __name__ == "__main__":
    unittest.main()
