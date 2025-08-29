from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskData(_message.Message):
    __slots__ = ("chat_completion", "embedding")
    CHAT_COMPLETION_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_FIELD_NUMBER: _ClassVar[int]
    chat_completion: bytes
    embedding: bytes
    def __init__(self, chat_completion: _Optional[bytes] = ..., embedding: _Optional[bytes] = ...) -> None: ...

class TaskResponseData(_message.Message):
    __slots__ = ("chat_completion_response", "embedding_response")
    CHAT_COMPLETION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    chat_completion_response: bytes
    embedding_response: bytes
    def __init__(self, chat_completion_response: _Optional[bytes] = ..., embedding_response: _Optional[bytes] = ...) -> None: ...

class RpcError(_message.Message):
    __slots__ = ("data", "message", "code")
    DATA_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    data: _struct_pb2.Struct
    message: str
    code: str
    def __init__(self, data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., message: _Optional[str] = ..., code: _Optional[str] = ...) -> None: ...

class RpcTask(_message.Message):
    __slots__ = ("id", "method", "meta", "data")
    ID_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    method: str
    meta: str
    data: TaskData
    def __init__(self, id: _Optional[str] = ..., method: _Optional[str] = ..., meta: _Optional[str] = ..., data: _Optional[_Union[TaskData, _Mapping]] = ...) -> None: ...

class RpcTaskResponse(_message.Message):
    __slots__ = ("id", "status", "result", "error")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: str
    result: TaskResponseData
    error: RpcError
    def __init__(self, id: _Optional[str] = ..., status: _Optional[str] = ..., result: _Optional[_Union[TaskResponseData, _Mapping]] = ..., error: _Optional[_Union[RpcError, _Mapping]] = ...) -> None: ...

class RpcTaskStream(_message.Message):
    __slots__ = ("task", "task_response")
    TASK_FIELD_NUMBER: _ClassVar[int]
    TASK_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    task: RpcTask
    task_response: RpcTaskResponse
    def __init__(self, task: _Optional[_Union[RpcTask, _Mapping]] = ..., task_response: _Optional[_Union[RpcTaskResponse, _Mapping]] = ...) -> None: ...
