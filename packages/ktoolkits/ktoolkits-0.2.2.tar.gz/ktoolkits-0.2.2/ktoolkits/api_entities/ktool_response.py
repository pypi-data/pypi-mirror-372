import json
from dataclasses import dataclass
from typing import Any
from pydantic import BaseModel,Field

@dataclass(init=False)
class DictMixin(dict):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __copy__(self):
        return type(self)(**self)

    def __deepcopy__(self, memo):
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(**self)
            memo[id_self] = _copy
        return _copy

    def __setitem__(self, key, value):
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        return super().__delitem__(key)

    def get(self, key, default=None):
        return super().get(key, default)

    def setdefault(self, key, default=None):
        return super().setdefault(key, default)

    def pop(self, key, default: Any):
        return super().pop(key, default)

    def update(self, **kwargs):
        super().update(**kwargs)

    def __contains__(self, key):
        return super().__contains__(key)

    def copy(self):
        return type(self)(self)

    def getattr(self, attr):
        return super().get(attr)

    def setattr(self, attr, value):
        return super().__setitem__(attr, value)

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, super().__repr__())

    def __str__(self):
        return json.dumps(self, ensure_ascii=False)
    


@dataclass(init=False)
class KToolAPIResponse(DictMixin):
    """The response content
    Args:
        request_id (str): The request id.
        status_code (int): HTTP status code, 200 indicates that the
            request was successful, and others indicate an error。
        code (str): Error code if error occurs, otherwise empty str.
        message (str): Set to error message on error.
        output (Any): The request output.
    """
    status_code: int
    request_id: str
    code: str
    message: str
    output: Any

    def __init__(self,
                 status_code: int,
                 request_id: str = '',
                 code: str = '',
                 message: str = '',
                 output: Any = None,
                 **kwargs):
        super().__init__(status_code=status_code,
                         request_id=request_id,
                         code=code,
                         message=message,
                         output=output,
                         **kwargs)
    

class RunnerResponse(KToolAPIResponse):
    @staticmethod
    def from_api_response(api_response: KToolAPIResponse):
        """Convert API response to RunnerResponse."""
        return RunnerResponse(
                status_code=api_response.status_code,
                request_id=api_response.request_id,
                code=api_response.code,
                message=api_response.message,
                output=api_response.output)


class SandboxResponse(KToolAPIResponse):

    @staticmethod
    def from_api_response(api_response: KToolAPIResponse):
        """Convert API response to SandboxResponse."""
        return SandboxResponse(
                status_code=api_response.status_code,
                request_id=api_response.request_id,
                code=api_response.code,
                message=api_response.message,
                output=api_response.output)