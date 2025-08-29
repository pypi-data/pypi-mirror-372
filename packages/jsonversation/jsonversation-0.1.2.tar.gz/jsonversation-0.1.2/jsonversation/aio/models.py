from __future__ import annotations
import asyncio
import typing
import io
from typing import Any, Awaitable, Callable


class StreamingObject[T]:
    _on_complete_funcs: list[Callable[[T], Awaitable[None]]]

    def __init__(self) -> None:
        self._on_complete_funcs = []

    async def update(self, value: T) -> None:
        return None

    async def _complete(self) -> None: ...

    def on_complete(self, func: Callable[[T], Awaitable[None]]) -> None:
        self._on_complete_funcs.append(func)


class Object(StreamingObject[dict[str, Any]]):
    _keys: list[str]
    _parsed_keys: list[str]
    _value: dict[str, Any]

    def __init__(self) -> None:
        super().__init__()
        self._keys = []
        self._parsed_keys = []
        self._value = {}

        for key, type_hint in type(self).__annotations__.items():
            self._keys.append(key)

            # Handle List[T]
            if hasattr(type_hint, "__origin__"):
                item_cls = typing.get_args(type_hint)[0]
                setattr(self, key, type_hint.__origin__(item_cls))
            else:
                setattr(self, key, type_hint())

    async def _complete(self) -> None:
        tasks = []
        if self._parsed_keys:
            last_key = self._parsed_keys[-1]
            object_to_complete: StreamingObject[Any] = self.__getattribute__(last_key)
            await object_to_complete._complete()

        for func in self._on_complete_funcs:
            tasks.append(func(self._value))

        await asyncio.gather(*tasks)

    def _last_parsed_key(self, default: str) -> str:
        if self._parsed_keys:
            return self._parsed_keys[-1]

        return default

    async def update(self, value: dict[str, Any]) -> None:
        model_keys = self._keys
        for key in value.keys():
            if key not in model_keys:
                continue

            model_value: StreamingObject[Any] = self.__getattribute__(key)
            await model_value.update(value[key])

            if len(self._parsed_keys) == 0:
                # this is the first key we're parsing
                self._parsed_keys.append(key)
            else:
                if key not in self._parsed_keys:
                    # this is the new key, we need to complete the previous object
                    object_to_complete: StreamingObject[Any] = self.__getattribute__(self._last_parsed_key(key))
                    await object_to_complete._complete()
                    self._parsed_keys.append(key)

            self._value[self._last_parsed_key(key)] = self.__getattribute__(self._last_parsed_key(key)).get_value()

        return None

    def get_value(self) -> dict[str, Any]:
        return self._value


type OnAppendFunc[T] = Callable[[T], Awaitable[None]]


class String(StreamingObject[str]):
    _value: io.StringIO
    _on_append_funcs: list[OnAppendFunc[str]]

    def __init__(self) -> None:
        super().__init__()
        self._on_append_funcs = []
        self._value = io.StringIO()

    async def update(self, value: str) -> None:
        current_buffer_value = self._value.getvalue()
        current_buffer_length = len(current_buffer_value)
        new_chunk = None

        if current_buffer_length == 0:
            new_chunk = value
        elif len(value) == current_buffer_length:
            return
        elif len(value) > current_buffer_length:
            new_chunk = value.replace(current_buffer_value, "")

        if new_chunk:
            self._value.write(new_chunk)
            tasks = [f(new_chunk) for f in self._on_append_funcs]
            await asyncio.gather(*tasks)

        return None

    async def _complete(self) -> None:
        tasks = []
        for func in self._on_complete_funcs:
            tasks.append(func(self.get_value()))

        await asyncio.gather(*tasks)

    def on_append(self, func: OnAppendFunc[str]) -> None:
        self._on_append_funcs.append(func)

    def get_value(self) -> str:
        return self._value.getvalue()


class List[T: StreamingObject[Any]](StreamingObject[list[Any]]):
    _item_type: type[T]
    _values: list[T]
    _on_append_funcs: list[OnAppendFunc[T]]

    def __init__(self, item_type: type[T]) -> None:
        super().__init__()
        self._values = []
        self._on_append_funcs = []
        self._item_type = item_type

    async def update(self, value: list[Any]) -> None:
        if not value:
            return

        # NOTE this is not very efficient, but it will do for now
        for idx, item in enumerate(value):
            if idx >= len(self._values):
                if idx > 0:
                    await self._values[-1]._complete()
                new_value = self._item_type()
                await new_value.update(item)
                self._values.append(new_value)

                tasks = [func(new_value) for func in self._on_append_funcs]
                await asyncio.gather(*tasks)
            else:
                existing_value = self._values[idx]
                await existing_value.update(item)

        return None

    def on_append(self, func: OnAppendFunc[T]) -> None:
        self._on_append_funcs.append(func)

    async def _complete(self) -> None:
        tasks = []
        for func in self._on_complete_funcs:
            tasks.append(func(self._values))

        await asyncio.gather(*tasks)

    def get_value(self) -> list[T]:
        return self._values


class Atomic[T](StreamingObject[T | None]):
    _is_empty: bool
    _value: T | None

    def __init__(self, item_cls: type[T]) -> None:
        super().__init__()
        self._is_empty = True
        self._value = None

    async def update(self, value: T | None) -> None:
        self._value = value
        self._is_empty = False

    async def _complete(self) -> None:
        tasks = []
        if not self._is_empty:
            for func in self._on_complete_funcs:
                tasks.append(func(self._value))

        await asyncio.gather(*tasks)

    def get_value(self) -> T | None:
        return self._value
