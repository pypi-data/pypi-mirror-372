from collections.abc import MutableMapping
from typing import Any, Callable

from .states import _get_state


class StateProxyType(MutableMapping[str, Any]):
    pass


def get_proxy(get_ident: Callable[[], str]) -> StateProxyType:
    class StateProxy(MutableMapping[str, Any]):
        def __iter__(self):
            return iter(_get_state(get_ident()))

        def __getitem__(self, __key: str) -> Any:
            return _get_state(get_ident())[__key]

        def __setitem__(self, __key: str, __value: Any) -> None:
            return _get_state(get_ident()).__setitem__(__key, __value)

        def __delitem__(self, __key: str) -> None:
            return _get_state(get_ident()).__delitem__(__key)

        def __len__(self) -> int:
            return len(_get_state(get_ident()))

    return StateProxy()
