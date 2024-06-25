from typing import List, Union, Any


def ensure_value_is_list(value: Union[List[Any], Any]) -> List[Any]:
    if isinstance(value, list):
        return value
    else:
        return [value]
