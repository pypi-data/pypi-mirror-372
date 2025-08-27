#coding=utf-8

from typing import Any, Dict, List, Union,Generator
from ktoolkits.api_entities.http_request import HttpRequest
from ktoolkits.api_entities.ktool_response import KToolAPIResponse
from ktoolkits.client.base_api import BaseAsyncTaskApi

import ktoolkits

class ToolboxApi(BaseAsyncTaskApi):

    @classmethod
    def _get_sandbox(cls,
                     api_key: str = None,
                     **kwargs):
        
        get_sandbox_by_name_endpoint = "/sandbox"

        url = f"{ktoolkits.base_http_api_url}{get_sandbox_by_name_endpoint}"

        api_key = cls._validate_params(api_key)

        request = HttpRequest(
                    url=url,
                    api_key=api_key,
                    http_method="GET",
                    json=None,
                )
        
        api_reponse =  request.call()
        #api_response =====>execute_command_response
        return api_reponse
        

    @classmethod
    def _get_sandbox_by_name(cls,
                            name: str,
                            api_key: str = None,
                            **kwargs):
        get_sandbox_by_name_endpoint = "/sandbox"

        url = f"{ktoolkits.base_http_api_url}{get_sandbox_by_name_endpoint}?name={name}"

        api_key = cls._validate_params(api_key)

        request = HttpRequest(
                    url=url,
                    api_key=api_key,
                    http_method="GET",
                    json=None,
                )
        
        api_reponse =  request.call()
        #api_response =====>execute_command_response
        return api_reponse

    @classmethod
    def _create_sandbox(cls,
                      name: str,
                      image: str,
                      version: str,
                      api_key: str = None,
                      **kwargs) -> Dict[str, Any]:
        
        #get sandbox id
        create_sandbox_endpoint = "/sandbox"

        url = f"{ktoolkits.base_http_api_url}{create_sandbox_endpoint}"

        api_key = cls._validate_params(api_key)

        json_data = {
            "name": name,
            "image":image,
            "version":version
        }

        request = HttpRequest(
                    url=url,
                    api_key=api_key,
                    http_method="POST",
                    json=json_data,
                )
        
        api_reponse =  request.call()

        #api_response =====>execute_command_response
        return api_reponse
    
    @classmethod
    def _start_sandbox(cls,
                      sandbox_id: str,
                      api_key: str = None,
                      **kwargs) -> Dict[str, Any]:
        
        #get sandbox id
        create_sandbox_endpoint = "/sandbox/start"

        url = f"{ktoolkits.base_http_api_url}{create_sandbox_endpoint}"

        api_key = cls._validate_params(api_key)

        json_data = {
            "sandbox_id": sandbox_id,
        }

        request = HttpRequest(
                    url=url,
                    api_key=api_key,
                    http_method="POST",
                    json=json_data,
                )
        api_reponse =  request.call()
        #api_response =====>execute_command_response
        return api_reponse
    
    @classmethod
    def _stop_sandbox(cls,
                      sandbox_id: str,
                      api_key: str = None,
                      **kwargs) -> Dict[str, Any]:
        
        #get sandbox id
        create_sandbox_endpoint = "/sandbox/stop"

        url = f"{ktoolkits.base_http_api_url}{create_sandbox_endpoint}"

        api_key = cls._validate_params(api_key)

        json_data = {
            "sandbox_id": sandbox_id,
        }

        request = HttpRequest(
                    url=url,
                    api_key=api_key,
                    http_method="POST",
                    json=json_data,
                )
        api_reponse =  request.call()
        #api_response =====>execute_command_response
        return api_reponse

    @classmethod
    def _remove_sandbox(cls,
                      sandbox_id: str,
                      api_key: str = None,
                      **kwargs) -> Dict[str, Any]:
        
        #get sandbox id
        create_sandbox_endpoint = "/sandbox/remove"

        url = f"{ktoolkits.base_http_api_url}{create_sandbox_endpoint}"

        api_key = cls._validate_params(api_key)

        json_data = {
            "sandbox_id": sandbox_id,
        }

        request = HttpRequest(
                    url=url,
                    api_key=api_key,
                    http_method="POST",
                    json=json_data,
                )
        api_reponse =  request.call()
        #api_response =====>execute_command_response
        return api_reponse

    @classmethod
    def _execute_command(cls, sandbox_id: str, 
                         command:str, 
                         cwd: str=None, 
                         api_key: str= None, 
                         is_deamon:bool=False,
                         **kwargs):

        #exec command
        execute_command_endpoint = "/sandbox/process"

        url = f"{ktoolkits.base_http_api_url}{execute_command_endpoint}"

        api_key = cls._validate_params(api_key)

        json_data = {
            "sandbox_id":sandbox_id,
            "command": command,
            "is_deamon":is_deamon,
        }

        if cwd:
            json_data["cwd"] = cwd

        request = HttpRequest(
                    url=url,
                    api_key=api_key,
                    http_method="POST",
                    json=json_data,
                )
        # call request service.
        api_reponse =  request.call()

        task_id = super()._get_task_id(api_reponse)

        api_reponse = super().wait(task_id, api_key, task_endpoint="process")

        return api_reponse


    
    """
    api.add_resource(SandboxFilesApi, '/sandbox/files')
    api.add_resource(SandboxFilesUploadApi, '/sandbox/files/upload')
    api.add_resource(SandboxFilesDownloadApi, '/sandbox/files/download')
    """

    @classmethod
    def _list_files(cls, sandbox_id: str, 
                    path: str, 
                    api_key: str= None,
                    **kwargs):
        
        list_files_endpoint = "/sandbox/files"

        url = f"{ktoolkits.base_http_api_url}{list_files_endpoint}?sandbox_id={sandbox_id}&path={path}"

        api_key = cls._validate_params(api_key)

        request = HttpRequest(
                    url=url,
                    api_key=api_key,
                    http_method="GET",
                    json=None,
                )
        # call request service.
        api_reponse =  request.call()
        return api_reponse

    @classmethod
    def _write_file(cls, sandbox_id: str, 
                    path: str, 
                    content: str, 
                    api_key: str= None,
                    **kwargs):
        file_write_endpoint = "/sandbox/files/upload"

        url = f"{ktoolkits.base_http_api_url}{file_write_endpoint}"

        api_key = cls._validate_params(api_key)

        json_data = {
            "sandbox_id":sandbox_id,
            "path": path,
            "content": content,
        }

        request = HttpRequest(
                    url=url,
                    api_key=api_key,
                    http_method="POST",
                    json=json_data,
                )
        # call request service.
        api_reponse =  request.call()
        return api_reponse
    
    @classmethod
    def _read_file(cls, sandbox_id: str, path: str, api_key: str= None)-> bytearray:
        file_read_endpoint = "/sandbox/files/download"

        url = f"{ktoolkits.base_http_api_url}{file_read_endpoint}?sandbox_id={sandbox_id}&path={path}"

        api_key = cls._validate_params(api_key)

        request = HttpRequest(
                    url=url,
                    api_key=api_key,
                    http_method="GET",
                    json=None,
                )
        # call request service.
        content =  request.download_file()
        return content