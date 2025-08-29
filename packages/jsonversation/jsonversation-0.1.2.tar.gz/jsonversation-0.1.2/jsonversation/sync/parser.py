from __future__ import annotations
from typing import Any
import jiter
import io

from jsonversation.sync.models import Object


class Parser:
    _buffer: io.BytesIO
    _object: Object

    def __init__(self, obj: Object) -> None:
        self._object = obj
        self._buffer = io.BytesIO()

    def __enter__(self) -> Parser:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, *args: list[Any]) -> None:
        if exc_type is None:
            self._object._complete()

    def push(self, chunk: str) -> None:
        if not chunk.strip():
            return None

        self._buffer.write(chunk.encode())
        parsed_dict = jiter.from_json(self._buffer.getvalue(), partial_mode="trailing-strings")
        self._object.update(parsed_dict)
