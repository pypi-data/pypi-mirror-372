import datetime as dt
from collections import UserDict
from typing import Any


class SessionState(UserDict):
    def __init__(self, ident: str):
        super().__init__()
        self.ident = ident
        self.last_access = dt.datetime.now()

    def __getattribute__(self, __name: str) -> Any:
        if __name != "last_access":
            self.last_access = dt.datetime.now()
        return super().__getattribute__(__name)

    def __setitem__(self, key: Any, item: Any) -> None:
        return super().__setitem__(key, item)

    def __del__(self):
        self.clear()

    def clear(self):
        while self.data:
            self.popitem()
