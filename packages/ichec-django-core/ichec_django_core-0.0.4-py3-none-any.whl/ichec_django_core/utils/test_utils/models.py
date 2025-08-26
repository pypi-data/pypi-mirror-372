from pydantic import BaseModel


class Resource(BaseModel):

    id: int | None = None


_TYPE_TO_PATH: dict = {}

_PATH_TO_TYPE: dict = {}


def register_type(label: str, t):
    _PATH_TO_TYPE[label] = t
    _TYPE_TO_PATH[t.__name__] = label


def get_path_from_item(resource: Resource) -> str:
    return _TYPE_TO_PATH[type(resource).__name__]


def get_path_from_type(item_t) -> str:
    return _TYPE_TO_PATH[item_t.__name__]


def get_type(path: str):
    return _PATH_TO_TYPE[path]
