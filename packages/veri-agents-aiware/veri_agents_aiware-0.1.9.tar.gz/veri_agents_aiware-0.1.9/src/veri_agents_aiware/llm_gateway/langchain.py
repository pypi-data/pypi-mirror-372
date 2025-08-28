import os
from typing import Dict, Optional, Any, cast
from langchain_openai import ChatOpenAI
from pydantic import Field, model_validator
from pydantic.types import SecretStr
from langchain_core.utils.utils import secret_from_env


class AiwareGatewayLLM(ChatOpenAI):
    use_responses_api: Optional[bool] = False
    llm_gateway_api: str | None = Field(
        default_factory=lambda: os.environ.get("LLM_GATEWAY_API")
    )

    llm_gateway_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("LLM_GATEWAY_KEY", default=None)
    )
    aiware_session: Optional[SecretStr] = Field(
        default_factory=secret_from_env("AIWARE_SESSION", default=None)
    )
    aiware_api_key: Optional[SecretStr] = Field(
        default_factory=secret_from_env("AIWARE_API_KEY", default=None)
    )

    @model_validator(mode="before")
    @classmethod
    def transform_input(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if "aiware_session" in data:
            aiware_session = cast(SecretStr | None, data["aiware_session"])
            if aiware_session:
                default_headers = data.get("default_headers", {})
                default_headers["x-aiware-session"] = aiware_session.get_secret_value()
                data["default_headers"] = default_headers
        
        if "aiware_api_key" in data:
            aiware_api_key = cast(SecretStr | None, data["aiware_api_key"])
            if aiware_api_key:
                default_headers = data.get("default_headers", {})
                default_headers["x-aiware-api-token"] = aiware_api_key.get_secret_value()
                data["default_headers"] = default_headers

        data["openai_api_base"] = (
            data.get("openai_api_base")
            or data.get("llm_gateway_api")
            or "https://llm-gateway.aisglabs1.aiware.run"
        )

        if "llm_gateway_key" in data:
            data["api_key"] = data["llm_gateway_key"]

        return data
