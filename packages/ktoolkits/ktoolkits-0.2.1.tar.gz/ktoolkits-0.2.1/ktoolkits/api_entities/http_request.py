#coding=utf-8
import os
import json
import tempfile
import requests
# 禁用安全警告(忽略安全自签名证书)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from typing import Any
from http import HTTPStatus
from ktoolkits.api_entities.base_request import AioBaseRequest
from ktoolkits.api_entities.ktool_response import KToolAPIResponse

from ktoolkits.common.logging import logger
from ktoolkits.common.error import UnsupportedHTTPMethod
from ktoolkits.common.utils import (
                            _handle_http_failed_response,
                            _handle_stream)
from ktoolkits.common.constants import (
                            SSE_CONTENT_TYPE)

import ktoolkits

class HttpRequest(AioBaseRequest):

    def __init__(self,
                 url: str,
                 api_key: str,
                 http_method: str,
                 json: Any,
                 stream: bool = False,
                 timeout: int = 120) -> None:
        """HttpSSERequest, processing http server sent event stream.
        """
        super().__init__()
        
        self.url = url
        self.api_key = api_key
        self.http_method = http_method
        self.json = json
        self.stream = stream

        self.headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer %s' % api_key,
            **self.headers,
        }

        self.timeout = timeout

    def download_file(self)-> bytearray:
        if self.http_method == "GET":
            headers = {**self.headers}
            response = requests.get(
                url=self.url,
                headers=headers,
                stream=True,
                timeout=self.timeout
            )
        elif self.http_method == "POST":
            headers = {**self.headers}
            response = requests.post(
                url=self.url,
                headers=headers,
                stream=True,
                timeout=self.timeout
            )
        
        else:
            raise UnsupportedHTTPMethod('Unsupported http method: %s' %
                                                self.method)
        
        response.raise_for_status()  # 抛出 HTTP 错误（如果有）

        local_path = content = ""

        content = None

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            local_path = tmp.name
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # 忽略 keep-alive 空块
                    tmp.write(chunk)
            tmp.flush()

        with open(local_path, 'rb') as f:
            content = f.read()
        
        os.unlink(local_path)

        return content
        
    def call(self):
        
        response = self._handle_request()

        if self.stream:
            return (item for item in response)
        else:
            output = next(response)
            try:
                next(response)
            except StopIteration:
                pass
            return output

    def aio_call(self):
        """
        SSE流处理
        """
        pass

    def _handle_request(self):
        if ktoolkits.debug:
            from http.client import HTTPConnection
            HTTPConnection.debuglevel = 1
        
        with requests.Session() as session:

            if self.http_method == "GET":
                headers = {**self.headers}
                response = session.get(
                    url=self.url,
                    headers=headers,
                    timeout=self.timeout,
                    verify=False
                )
            
            elif self.http_method == "POST":
                headers = {**self.headers}
                response = session.post(
                    url=self.url,
                    stream=self.stream,
                    headers=headers,
                    json=self.json,
                    timeout=self.timeout,
                    verify=False
                )
                
            else:
                raise UnsupportedHTTPMethod('Unsupported http method: %s' %
                                                self.method)

            for rsp in self._handle_response(response):
                yield rsp

        
    def _handle_response(self, response: requests.Response):
        request_id = ''
        if (response.status_code == HTTPStatus.OK and self.stream
                and SSE_CONTENT_TYPE in response.headers.get(
                    'content-type', '')):

            for is_error, status_code, event in _handle_stream(response):
                    try:
                        data = event.data
                        output = None
                        msg = json.loads(data)
                        logger.debug('Stream message: %s' % msg)
                    except json.JSONDecodeError:
                        yield KToolAPIResponse(
                            request_id=request_id,
                            status_code=HTTPStatus.BAD_REQUEST,
                            output=None,
                            code='Unknown',
                            message=data)
                        continue

                    if is_error:
                        yield KToolAPIResponse(
                        request_id=request_id,
                        status_code=status_code,
                        output=None,
                        code=msg['code']
                        if 'code' in msg else None,  # noqa E501
                        message=msg['message']
                        if 'message' in msg else None)  # noqa E501
                    else:
                        yield msg

        elif response.status_code == HTTPStatus.OK:
            json_content = response.json()
            logger.debug('Response: %s' % json_content)

            output = None
            if 'task_id' in json_content:
                output = {'task_id': json_content['task_id']}
            if 'output' in json_content:
                output = json_content['output']
            if 'code' in json_content:
                code = json_content['code']
            if 'message' in json_content:
                message = json_content['message']
            if 'request_id' in json_content:
                request_id = json_content['request_id']

            yield KToolAPIResponse(request_id=request_id,
                                    status_code=HTTPStatus.OK,
                                    code=code,
                                    message=message,
                                    output=output)
        else:
            yield _handle_http_failed_response(response)
    