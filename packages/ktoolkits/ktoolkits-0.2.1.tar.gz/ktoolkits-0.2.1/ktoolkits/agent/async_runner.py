from ktoolkits.client.base_api import BaseAsyncTaskApi
from ktoolkits.api_entities.ktool_response import RunnerResponse

class AsyncRunner(BaseAsyncTaskApi):

    @classmethod
    def async_call(
        cls,
        tool_name: str,
        tool_input: str,
        **kwargs
        ):
        response = super().async_call(tool_name,tool_input,**kwargs)
        return RunnerResponse.from_api_response(response)
    
    @classmethod
    def call(
        cls,
        tool_name: str,
        tool_input: str,
        **kwargs
        ):
        response = super().call(tool_name,tool_input,**kwargs)
        return RunnerResponse.from_api_response(response)

        