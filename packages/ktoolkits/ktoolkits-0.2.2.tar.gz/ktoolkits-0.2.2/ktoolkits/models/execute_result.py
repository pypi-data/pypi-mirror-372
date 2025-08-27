#coding=utf-8
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr

from typing import Any,Union,Dict,List,ClassVar,Optional
from ktoolkits.api_entities.ktool_response import KToolAPIResponse


class ExecuteResult(BaseModel):
    """
    ExecuteResponse, inner model for ExecuteResponse
    """ # noqa: E501
    exit_code: Union[StrictFloat, StrictInt, None] = Field(description="Exit code", alias="exit_code")
    result: StrictStr = Field(description="Command output")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["exit_code", "result"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    @staticmethod
    def from_api_response(api_response: KToolAPIResponse):
        if api_response.message != "success" or not api_response.output:
            return None
        try:
            result = ExecuteResult(**api_response.output)
            return result
        except Exception as e:
            print(f"转换失败: {e}")
            return None