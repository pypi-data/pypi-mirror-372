from typing import Any, cast

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)


def _pretty_print_cty_recursive(value: CtyValue[Any], indent: int) -> str:
    """
    Recursive helper for pretty printing CtyValue objects.
    """
    if isinstance(value.type, CtyObject):
        s = "{\n"
        for i, (key, val) in enumerate(cast(dict[str, Any], value.value).items()):
            s += " " * (indent + 2) + f'"{key}": '
            s += _pretty_print_cty_recursive(
                CtyValue(vtype=value.type.attribute_types[key], value=val), indent + 2
            )
            if i < len(value.value) - 1:
                s += ",\n"
            else:
                s += "\n"
        s += " " * indent + "}"
        return s
    elif isinstance(value.type, CtyList):
        s = "[\n"
        for i, item in enumerate(cast(list[Any], value.value)):
            s += " " * (indent + 2)
            s += _pretty_print_cty_recursive(
                CtyValue(vtype=value.type.element_type, value=item), indent + 2
            )
            if i < len(value.value) - 1:
                s += ",\n"
            else:
                s += "\n"
        s += " " * indent + "]"
        return s
    elif isinstance(value.type, CtyMap):
        s = "{\n"
        for i, (key, val) in enumerate(cast(dict[str, Any], value.value).items()):
            s += " " * (indent + 2) + f'"{key}": '
            s += _pretty_print_cty_recursive(
                CtyValue(vtype=value.type.element_type, value=val), indent + 2
            )
            if i < len(value.value) - 1:
                s += ",\n"
            else:
                s += "\n"
        s += " " * indent + "}"
        return s
    elif isinstance(value.type, CtyTuple):
        s = "[\n"
        for i, item in enumerate(cast(list[Any], value.value)):
            s += " " * (indent + 2)
            s += _pretty_print_cty_recursive(
                CtyValue(vtype=value.type.element_types[i], value=item), indent + 2
            )
            if i < len(value.value) - 1:
                s += ",\n"
            else:
                s += "\n"
        s += " " * indent + "]"
        return s
    elif isinstance(value.type, CtyString):
        return f'"{value.value}"'
    elif isinstance(value.type, CtyNumber):
        return str(value.value)
    elif isinstance(value.type, CtyBool):
        return str(value.value).lower()
    elif isinstance(value.type, CtyDynamic):
        return str(value.value)
    else:
        return str(value.value)


def pretty_print_cty(value: CtyValue[Any]) -> None:
    """
    Pretty prints a CtyValue object.
    """
    print(_pretty_print_cty_recursive(value, 0))
