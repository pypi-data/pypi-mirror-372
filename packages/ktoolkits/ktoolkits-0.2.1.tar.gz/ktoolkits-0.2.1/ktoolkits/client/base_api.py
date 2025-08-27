import time
import requests
# 禁用安全警告(忽略安全自签名证书)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from typing import Any, Dict, List, Union,Generator
from ktoolkits.api_entities.http_request import HttpRequest
from ktoolkits.api_entities.ktool_response import KToolAPIResponse

from http import HTTPStatus
from ktoolkits.common.utils import (
                                join_url,
                                _handle_http_response,
                                default_headers
                            )

from ktoolkits.common.api_key import get_default_api_key

from ktoolkits.common.logging import logger
from ktoolkits.common.constants import (
                                REPEATABLE_STATUS,
                                TaskStatus,
                                KToolAPICode,
                            )

import ktoolkits

class BaseAioApi():
    """BaseApi, internal use only.

    """
    @classmethod
    def _validate_params(cls, api_key):
        if api_key is None:
            api_key = get_default_api_key()
        return api_key

    @classmethod
    async def call(cls,
                   message: str,
                   sender: str,
                   api_key: str = None,
                   stream: bool = False,
                   **kwargs):
        """
        Call service and get result.
        """
        api_key = BaseAioApi._validate_params(api_key)

        chat_url = f"{ktoolkits.base_http_api_url}/agent/chat/completion"

        json_data = {"query":message,"sender":sender}

        request = HttpRequest(
                    url=chat_url,
                    api_key=api_key,
                    http_method="POST",
                    json=json_data,
                    stream=stream)
        # call request service.
        return await request.aio_call()

class BaseApi():
    """
    BaseApi internal api call
    """    

    @classmethod
    def _validate_params(cls, api_key):
        if api_key is None:
            api_key = get_default_api_key()
        return api_key
    @classmethod
    def role(cls,
               role: str=None,
               api_key: str = None,
               **kwargs):
        
        prompt_url = f"{ktoolkits.base_http_api_url}/prompt"

        api_key = cls._validate_params(api_key)

        response = _get(prompt_url,params={"role":role},api_key=api_key)

        return response
    

    @classmethod
    def create_agent(cls,
                     agent_name: str,
                     api_key: str = None,
                     **kwargs):
        
        agent_url = f"{ktoolkits.base_http_api_url}/task/agent"

        json_data = {"agent_name":agent_name}
        
        api_key = cls._validate_params(api_key)
        
        request = HttpRequest(
                    url=agent_url,
                    api_key=api_key,
                    http_method="POST",
                    json=json_data,
                )
        # call request service.
        return request.call()

    @classmethod
    def create_agent_tool(cls,
                   agent_uuid: str =None,
                   tool_uuid: str =None,
                   api_key: str = None,
                   **kwargs) -> str:
        
        agent_tool_url = f"{ktoolkits.base_http_api_url}/task/agent/tool"

        json_data = {"agent_uuid":agent_uuid,"tool_uuid":tool_uuid}
        
        api_key = cls._validate_params(api_key)
        
        request = HttpRequest(
                    url=agent_tool_url,
                    api_key=api_key,
                    http_method="POST",
                    json=json_data,
                )
        # call request service.
        return request.call()


    @classmethod
    def chat(cls,
             message: str,
             recipient: str = None,
             api_key: str = None,
             stream: bool = True,
             **kwargs) -> Union[str, Generator]:
        
        chat_url = f"{ktoolkits.base_http_api_url}/agent/chat/message"

        json_data = {"query":message,"recipient":recipient}
        
        api_key = cls._validate_params(api_key)
        
        request = HttpRequest(
                    url=chat_url,
                    api_key=api_key,
                    http_method="POST",
                    json=json_data,
                    stream=stream
                )
        # call request service.
        return request.call()
    
    @classmethod
    def call(cls, 
            tool_name: str,
            tool_input: str,
            api_key: str = None,
            **kwargs):
        """
        同步任务请求底层API
        """
        pass

class AsyncTaskGetMixin():
    @classmethod
    def _get(cls,
             task_id: str,
             api_key: str = None,
             task_endpoint: str = "tool",
             **kwargs) -> KToolAPIResponse:
        base_url = kwargs.pop('base_address', None)

        if task_endpoint == "tool":
            task_status_endpoint = f"/task/async/tool/{task_id}"
        elif task_endpoint == "process":
            task_status_endpoint = f"/sandbox/process?task_id={task_id}"
        else:
            raise ValueError("Invalid task_endpoint value")

        if base_url is not None:
            status_url = join_url(base_url, task_status_endpoint)
        else:
            status_url = f"{ktoolkits.base_http_api_url}{task_status_endpoint}"  

        with requests.Session() as session:
            logger.debug('Starting request: %s' % status_url)
            response = session.get(status_url,
                                   headers={
                                       **default_headers(api_key)
                                   },
                                   verify=False)
            
            logger.debug('Starting processing response: %s' % status_url)
            return _handle_http_response(response)

class BaseAsyncTaskApi(AsyncTaskGetMixin):

    @classmethod
    def _validate_params(cls, api_key):
        if api_key is None:
            api_key = get_default_api_key()
        return api_key
    
    @classmethod
    def call(cls,
             tool_name: str,
             tool_input: str,
             api_key: str = None,
             **kwargs) -> KToolAPIResponse:
        """Call service and get result.
        """
        response = None
        task_response = cls.async_call(tool_name=tool_name,
                                       tool_input=tool_input,
                                       api_key=api_key,
                                       **kwargs)
        
        if task_response.status_code != 200 or task_response.code == KToolAPICode.FAILURE:
            #print(task_response.message)
            return task_response
        
        response = cls.wait(task_response,
                            api_key=api_key)
        return response
    
    
    @classmethod
    def _get_task_id(cls, task):
        if isinstance(task, str):
            task_id = task
        elif isinstance(task, KToolAPIResponse):
            if task.status_code == HTTPStatus.OK:
                task_id = task.output['task_id']
        return task_id
    
    @classmethod
    def _get_sandbox_id(cls, api_response):
        sandbox_id = None
        if isinstance(api_response, str):
            sandbox_id = api_response
        elif isinstance(api_response, KToolAPIResponse):
            if api_response.status_code == HTTPStatus.OK:
                if 'sandbox_id' in api_response.output:
                    sandbox_id = api_response.output['sandbox_id']
                else:
                    raise Exception(api_response.message)

        return sandbox_id

    @classmethod
    def wait(cls,
             task: Union[str, KToolAPIResponse],
             api_key: str = None,
             task_endpoint: str = "tool",
             **kwargs) -> KToolAPIResponse:
        """Wait for async task completion and return task result.

        Args:
            task (Union[str, KToolAPIResponse]): The task_id, or
                async_call response.
            api_key (str, optional): The api_key. Defaults to None.

        Returns:
            KToolAPIResponse: The async task information.
        """
        task_id = cls._get_task_id(task)
        wait_seconds = 5
        max_wait_seconds = 15
        increment_steps = 3
        step = 0
        while True:
            step += 1
            # we start by querying once every second, and double
            # the query interval after every 3(increment_steps)
            # intervals, until we hit the max waiting interval
            # of 5(seconds）
            # TODO: investigate if we can use long-poll
            # (server side return immediately when ready)
            if wait_seconds < max_wait_seconds and step % increment_steps == 0:
                wait_seconds = min(wait_seconds * 2, max_wait_seconds)
            rsp = cls._get(task_id, api_key, task_endpoint, **kwargs)
            if rsp.status_code == HTTPStatus.OK:
                if rsp.output is None:
                    return rsp

                task_status = rsp.output['task_status']
                    
                if task_status in [
                        TaskStatus.FAILED, TaskStatus.CANCELED,
                        TaskStatus.SUCCEEDED, TaskStatus.UNKNOWN
                ]:
                    return rsp
                else:
                    logger.debug('The task %s is  %s' % (task_id, task_status))
                    time.sleep(wait_seconds)
            elif rsp.status_code in REPEATABLE_STATUS:
                logger.warn(
                    ('Get task: %s temporary failure, \
                        status_code: %s, code: %s message: %s, will try again.'
                     ) % (task_id, rsp.status_code, rsp.code, rsp.message))
                time.sleep(wait_seconds)
            else:
                return rsp

    @classmethod
    def async_call(cls,
                   tool_name: str,
                   tool_input: str,
                   api_key: str = None,
                   **kwargs) -> KToolAPIResponse:
        """Call async service return async task information.
        """
        agent_uuid      =kwargs.pop('agent_uuid', None)
        enable_cache    =kwargs.pop('enable_cache', 1)
        tool_input_file =kwargs.pop('tool_input_file', [])
        command_name    =kwargs.pop('command_name', 'template')

        json_data = {}
        json_data["tool_name"]      = tool_name
        json_data["tool_input"]     = tool_input
        json_data["enable_cache"]   = enable_cache
        json_data["tool_input_file"]= tool_input_file
        json_data["command_name"]   = command_name

        if agent_uuid is not None:
            json_data["agent_uuid"] = agent_uuid
                  
        api_key = cls._validate_params(api_key)
        
        async_url = f"{ktoolkits.base_http_api_url}/task/async/tool"
        request = HttpRequest(url=async_url,
                              api_key=api_key,
                              http_method="POST",
                              json=json_data)
        return request.call()


def _get(url,
         params={},
         api_key=None,
         **kwargs) -> Union[KToolAPIResponse, Dict]:
    
    with requests.Session() as session:
        logger.debug('Starting request: %s' % url)
        response = session.get(url,
                               headers={
                                   **default_headers(api_key),
                                   **kwargs.pop('headers', {})
                               },
                               params=params)
        logger.debug('Starting processing response: %s' % url)
        return _handle_http_response(response)


class GetMixin():
    @classmethod
    def get(cls,
            path: str = None,
            api_key: str = None,
            params: dict = {},
            **kwargs) -> Union[KToolAPIResponse, Dict]:
        """Get object information.

        Args:
            api_key (str, optional): The api api_key, if not present,
                will get by default rule(TODO: api key doc). Defaults to None.

        Returns:
            KToolAPIResponse: The object information in output.
        """
        custom_base_url = kwargs.pop('base_address', None)
        if custom_base_url:
            base_url = custom_base_url
        else:
            base_url = ktoolkits.base_http_api_url

        if path is not None:
            url = join_url(base_url, path)
        else:
            url = base_url

        return _get(url,
                    api_key=api_key,
                    params=params,
                    **kwargs)