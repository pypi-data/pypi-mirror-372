from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExecuteActionsRequest(_message.Message):
    __slots__ = ("path", "context")
    PATH_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    path: str
    context: Context
    def __init__(self, path: _Optional[str] = ..., context: _Optional[_Union[Context, _Mapping]] = ...) -> None: ...

class ExecuteActionsResponse(_message.Message):
    __slots__ = ("error", "run_data")
    class RunDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RUN_DATA_FIELD_NUMBER: _ClassVar[int]
    error: str
    run_data: _containers.ScalarMap[str, str]
    def __init__(self, error: _Optional[str] = ..., run_data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ExecuteFiltersRequest(_message.Message):
    __slots__ = ("context",)
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    context: Context
    def __init__(self, context: _Optional[_Union[Context, _Mapping]] = ...) -> None: ...

class ExecuteFiltersResponse(_message.Message):
    __slots__ = ("match", "error", "run_data")
    class RunDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    MATCH_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RUN_DATA_FIELD_NUMBER: _ClassVar[int]
    match: bool
    error: str
    run_data: _containers.ScalarMap[str, str]
    def __init__(self, match: bool = ..., error: _Optional[str] = ..., run_data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetPluginRequest(_message.Message):
    __slots__ = ("config",)
    class ConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _containers.ScalarMap[str, str]
    def __init__(self, config: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetPluginResponse(_message.Message):
    __slots__ = ("name", "priority", "error")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    name: str
    priority: int
    error: str
    def __init__(self, name: _Optional[str] = ..., priority: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...

class Context(_message.Message):
    __slots__ = ("repository", "pull_request", "run_data")
    class RunDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    PULL_REQUEST_FIELD_NUMBER: _ClassVar[int]
    RUN_DATA_FIELD_NUMBER: _ClassVar[int]
    repository: Repository
    pull_request: PullRequest
    run_data: _containers.ScalarMap[str, str]
    def __init__(self, repository: _Optional[_Union[Repository, _Mapping]] = ..., pull_request: _Optional[_Union[PullRequest, _Mapping]] = ..., run_data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class PullRequest(_message.Message):
    __slots__ = ("number", "web_url")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    WEB_URL_FIELD_NUMBER: _ClassVar[int]
    number: int
    web_url: str
    def __init__(self, number: _Optional[int] = ..., web_url: _Optional[str] = ...) -> None: ...

class Repository(_message.Message):
    __slots__ = ("full_name", "clone_url_http", "clone_url_ssh", "web_url")
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    CLONE_URL_HTTP_FIELD_NUMBER: _ClassVar[int]
    CLONE_URL_SSH_FIELD_NUMBER: _ClassVar[int]
    WEB_URL_FIELD_NUMBER: _ClassVar[int]
    full_name: str
    clone_url_http: str
    clone_url_ssh: str
    web_url: str
    def __init__(self, full_name: _Optional[str] = ..., clone_url_http: _Optional[str] = ..., clone_url_ssh: _Optional[str] = ..., web_url: _Optional[str] = ...) -> None: ...

class OnPrClosedRequest(_message.Message):
    __slots__ = ("context",)
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    context: Context
    def __init__(self, context: _Optional[_Union[Context, _Mapping]] = ...) -> None: ...

class OnPrClosedResponse(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...

class OnPrCreatedRequest(_message.Message):
    __slots__ = ("context",)
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    context: Context
    def __init__(self, context: _Optional[_Union[Context, _Mapping]] = ...) -> None: ...

class OnPrCreatedResponse(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...

class OnPrMergedRequest(_message.Message):
    __slots__ = ("context",)
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    context: Context
    def __init__(self, context: _Optional[_Union[Context, _Mapping]] = ...) -> None: ...

class OnPrMergedResponse(_message.Message):
    __slots__ = ("error",)
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: str
    def __init__(self, error: _Optional[str] = ...) -> None: ...

class ShutdownRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ShutdownResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
