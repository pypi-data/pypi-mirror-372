from _typeshed import Incomplete
from typing import Any, Mapping, NotRequired, Protocol, Required, TypedDict

JSONFieldMode: Incomplete
TextFieldMode: Incomplete

class ResponseLike(Protocol):
    status_code: int
    headers: Mapping[str, str]
    cookies: Mapping[str, str]
    text: str
    def json(self) -> Any: ...

class TextFieldDict(TypedDict):
    name: NotRequired[str]
    value: Required[str]
    mode: NotRequired[TextFieldMode]
    msg: NotRequired[str]

class JSONFieldDict(TypedDict):
    name: NotRequired[str]
    value: Required[dict | str]
    mode: NotRequired[JSONFieldMode]
    msg: NotRequired[str]
SimpleKVLike = dict[str, str] | None
DetailedKVLike = dict[str, TextFieldDict] | None
SimpleStrLike = str | int | None
DetailedStrLike = TextFieldDict | None
SimpleJSONLike = Any | None
DetailedJSONLike = JSONFieldDict | None
