import requests
import platform
from dataclasses import dataclass
from http import HTTPStatus
from typing import Union,Dict

from ktoolkits.api_entities.ktool_response import KToolAPIResponse
from ktoolkits.common.api_key import get_default_api_key
from ktoolkits.version import __version__

import hashlib

def calculate_md5(input_string):
    """
    计算并返回给定字符串的MD5哈希值。

    参数:
    input_string (str): 要计算其MD5哈希值的原始字符串。

    返回:
    str: 给定字符串的MD5哈希值。
    """
    # 创建一个md5哈希对象
    md5_hash = hashlib.md5()
    
    # 更新哈希对象，使用encode('utf-8')确保输入是字节类型
    md5_hash.update(input_string.encode('utf-8'))
    
    # 获取十六进制表示的哈希值，并返回
    return md5_hash.hexdigest()

def _handle_error_message(error, status_code, flattened_output:bool = False):
    code = None
    msg = ''
    request_id = ''
    if flattened_output:
        error['status_code'] = status_code
        return error
    if 'message' in error:
        msg = error['message']
    if 'msg' in error:
        msg = error['msg']
    if 'code' in error:
        code = error['code']
    if 'request_id' in error:
        request_id = error['request_id']
    return KToolAPIResponse(request_id=request_id,
                                status_code=status_code,
                                code=code,
                                message=msg)

def _handle_http_failed_response(
        response: requests.Response,
        flattened_output: bool = False) -> KToolAPIResponse:
    request_id = ''
    if 'application/json' in response.headers.get('content-type', ''):
        error = response.json()
        return _handle_error_message(error, response.status_code,
                                     flattened_output)
    else:
        msg = response.content.decode('utf-8')
        if flattened_output:
            return {'status_code': response.status_code, 'message': msg}
        return KToolAPIResponse(request_id=request_id,
                                    status_code=response.status_code,
                                    code='Unknown',
                                    message=msg)

def _handle_http_response(response: requests.Response) ->KToolAPIResponse:

    json_content = response.json()
    json_content['status_code'] = response.status_code
    
    if 'code' in json_content:
        code = json_content['code']
    if 'message' in json_content:
        msg = json_content['message']
    if 'output' in json_content:
        output = json_content['output']
    if 'request_id' in json_content:
        request_id = json_content['request_id']
        json_content.pop('request_id', None)

    return KToolAPIResponse(request_id=request_id,
                            status_code=response.status_code,
                            code=code,
                            message=msg,
                            output=output)
    

def default_headers(api_key: str = None) -> Dict[str, str]:
    ua = 'ktool/%s; python/%s; platform/%s; processor/%s' % (
        __version__,
        platform.python_version(),
        platform.platform(),
        platform.processor(),
    )
    headers = {'user-agent': ua}
    if api_key is None:
        api_key = get_default_api_key()
    headers['Authorization'] = 'Bearer %s' % api_key
    headers['Accept'] = 'application/json'
    return headers


def join_url(base_url, *args):
    if not base_url.endswith('/'):
        base_url = base_url + '/'
    url = base_url
    for arg in args:
        if arg is not None:
            url += arg + '/'
    return url[:-1]



@dataclass
class SSEEvent:
    id: str
    eventType: str
    data: str

    def __init__(self, id: str, type: str, data: str):
        self.id = id
        self.eventType = type
        self.data = data


def _handle_stream(response: requests.Response):
    # TODO define done message.
    is_error = False
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    event = SSEEvent(None, None, None)
    eventType = None
    for line in response.iter_lines():
        if line:
            line = line.decode('utf8')
            line = line.rstrip('\n').rstrip('\r')
            if line.startswith('id:'):
                id = line[len('id:'):]
                event.id = id.strip()
            elif line.startswith('event:'):
                eventType = line[len('event:'):]
                event.eventType = eventType.strip()
                if eventType == 'error':
                    is_error = True
            elif line.startswith('status:'):
                status_code = line[len('status:'):]
                status_code = int(status_code.strip())
            elif line.startswith('data:'):
                line = line[len('data:'):]
                event.data = line.strip()
                if eventType is not None and eventType == 'done':
                    continue
                yield (is_error, status_code, event)
                if is_error:
                    break
            else:
                continue  # ignore heartbeat...