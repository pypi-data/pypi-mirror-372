from __future__ import annotations
import typing
import io
from typing import Any, Callable


class StreamingObject[T]:
    def update(self, value: T) -> None:
        return None

    def _complete(self) -> None: ...


class Object(StreamingObject[dict[str, Any]]):
    _keys: list[str]
    _parsed_keys: list[str]
    _on_complete_funcs: list[Callable[[dict[str, Any]], None]]
    _value: dict[str, Any]

    def __init__(self) -> None:
        super().__init__()
        self._keys = []
        self._parsed_keys = []
        self._value = {}
        self._on_complete_funcs = []

        for key, type_hint in type(self).__annotations__.items():
            self._keys.append(key)

            # Handle List[T]
            if hasattr(type_hint, "__origin__"):
                item_cls = typing.get_args(type_hint)[0]
                setattr(self, key, type_hint.__origin__(item_cls))
            else:
                setattr(self, key, type_hint())

    def _complete(self) -> None:
        if self._parsed_keys:
            last_key = self._parsed_keys[-1]
            self.__getattribute__(last_key)._complete()

        for func in self._on_complete_funcs:
            func(self._value)

    def _last_parsed_key(self, default: str) -> str:
        if self._parsed_keys:
            return self._parsed_keys[-1]

        return default

    def update(self, value: dict[str, Any]) -> None:
        model_keys = self._keys
        for key in value.keys():
            if key not in model_keys:
                continue

            model_value = self.__getattribute__(key)
            model_value.update(value[key])

            if len(self._parsed_keys) == 0:
                # this is the first key we're parsing
                self._parsed_keys.append(key)
            else:
                if key not in self._parsed_keys:
                    # this is the new key, we need to complete the previous object
                    self.__getattribute__(self._last_parsed_key(key))._complete()
                    self._parsed_keys.append(key)

            self._value[self._last_parsed_key(key)] = self.__getattribute__(self._last_parsed_key(key)).get_value()

        return None

    def on_complete(self, func: Callable[[dict[str, Any]], None]) -> None:
        self._on_complete_funcs.append(func)

    def get_value(self) -> dict[str, Any]:
        return self._value


class String(StreamingObject[str]):
    _value: io.StringIO
    _on_append_funcs: list[Callable[[str], None]]
    _on_complete_funcs: list[Callable[[str], None]]

    def __init__(self) -> None:
        super().__init__()
        self._on_append_funcs = []
        self._on_complete_funcs = []
        self._value = io.StringIO()

    def update(self, value: str) -> None:
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
            [f(new_chunk) for f in self._on_append_funcs]

        return None

    def _complete(self) -> None:
        for func in self._on_complete_funcs:
            func(self.get_value())

    def on_append(self, func: Callable[[str], None]) -> None:
        self._on_append_funcs.append(func)

    def on_complete(self, func: Callable[[str], None]) -> None:
        self._on_complete_funcs.append(func)

    def get_value(self) -> str:
        return self._value.getvalue()


class List[T: StreamingObject[Any]](StreamingObject[list[Any]]):
    _item_type: type[T]
    _values: list[T]
    _on_append_funcs: list[Callable[[T], None]]
    _on_complete_funcs: list[Callable[[list[T]], None]]

    def __init__(self, item_type: type[T]) -> None:
        super().__init__()
        self._values = []
        self._on_complete_funcs = []
        self._on_append_funcs = []
        self._item_type = item_type

    def update(self, value: list[Any]) -> None:
        if not value:
            return

        # NOTE this is not very efficient, but it will do for now
        for idx, item in enumerate(value):
            if idx >= len(self._values):
                if idx > 0:
                    self._values[-1]._complete()
                new_value = self._item_type()
                new_value.update(item)
                self._values.append(new_value)
                for func in self._on_append_funcs:
                    func(new_value)
            else:
                existing_value = self._values[idx]
                existing_value.update(item)

        return None

    def on_append(self, func: Callable[[T], None]) -> None:
        self._on_append_funcs.append(func)

    def on_complete(self, func: Callable[[list[T]], None]) -> None:
        self._on_complete_funcs.append(func)

    def _complete(self) -> None:
        for func in self._on_complete_funcs:
            func(self._values)

    def get_value(self) -> list[T]:
        return self._values


class Atomic[T](StreamingObject[T]):
    _is_empty: bool
    _value: T | None
    _on_complete_funcs: list[Callable[[T | None], None]]

    def __init__(self, item_cls: type[T]) -> None:
        self._is_empty = True
        self._value = None
        self._on_complete_funcs = []

    def update(self, value: T) -> None:
        self._value = value
        self._is_empty = False

    def on_complete(self, func: Callable[[T | None], None]) -> None:
        self._on_complete_funcs.append(func)

    def _complete(self) -> None:
        if not self._is_empty:
            for func in self._on_complete_funcs:
                func(self._value)

    def get_value(self) -> T | None:
        return self._value
