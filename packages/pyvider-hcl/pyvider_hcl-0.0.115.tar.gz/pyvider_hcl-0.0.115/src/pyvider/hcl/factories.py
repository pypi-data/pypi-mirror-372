# pyvider-hcl/src/pyvider/hcl/factories.py
"""
Factory functions for creating CtyType objects from HCL type strings
and other HCL-specific constructions.
"""

import logging
import re
from typing import Any

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyType,
    CtyValue,
)
from pyvider.cty.exceptions import CtyError
from pyvider.hcl.parser import auto_infer_cty_type

logger = logging.getLogger(__name__)


class HclTypeParsingError(ValueError):
    """Custom exception for errors during HCL type string parsing."""


class HclFactoryError(ValueError):
    """Custom exception for errors during HCL factory operations."""


PRIMITIVE_TYPE_MAP: dict[str, CtyType[Any]] = {
    "string": CtyString(),
    "number": CtyNumber(),
    "bool": CtyBool(),
    "any": CtyDynamic(),
}

COMPLEX_TYPE_REGEX = re.compile(
    r"^(list|object|map)\((.*)\)$", re.IGNORECASE | re.DOTALL
)


def _parse_hcl_type_string(type_str: str) -> CtyType[Any]:
    type_str = type_str.strip()

    if type_str.lower() in PRIMITIVE_TYPE_MAP:
        return PRIMITIVE_TYPE_MAP[type_str.lower()]

    match = COMPLEX_TYPE_REGEX.match(type_str)
    if not match:
        raise HclTypeParsingError(f"Unknown or malformed type string: '{type_str}'")

    type_keyword = match.group(1).lower()
    inner_content = match.group(2).strip()

    if type_keyword == "list":
        if not inner_content:
            raise HclTypeParsingError("List type string is empty, e.g., 'list()'")
        element_type = _parse_hcl_type_string(inner_content)
        return CtyList(element_type=element_type)

    if type_keyword == "map":
        if not inner_content:
            raise HclTypeParsingError("Map type string is empty, e.g., 'map()'")
        element_type = _parse_hcl_type_string(inner_content)
        return CtyMap(element_type=element_type)

    if type_keyword == "object":
        if not inner_content.startswith("{") or not inner_content.endswith("}"):
            raise HclTypeParsingError(
                f"Object type string content must be enclosed in {{}}, got: '{inner_content}'"
            )
        if inner_content == "{}":
            return CtyObject({})

        attrs_str = inner_content[1:-1].strip()
        if not attrs_str:
            return CtyObject({})

        attributes = _parse_object_attributes_str(attrs_str)
        return CtyObject(attributes)

    raise HclTypeParsingError(f"Unhandled type keyword: '{type_keyword}'")


def _parse_object_attributes_str(attrs_str: str) -> dict[str, CtyType[Any]]:
    attributes: dict[str, CtyType[Any]] = {}
    balance = 0
    last_break = 0
    for i, char in enumerate(attrs_str):
        if char in "({":
            balance += 1
        elif char in ")}":
            balance -= 1
        elif char == "," and balance == 0:
            part = attrs_str[last_break:i].strip()
            if not part:
                raise HclTypeParsingError(
                    f"Empty attribute part found in '{attrs_str}'"
                )
            name, type_str = _split_attr_part(part)
            attributes[name] = _parse_hcl_type_string(type_str)
            last_break = i + 1
    last_part = attrs_str[last_break:].strip()
    if last_part:
        name, type_str = _split_attr_part(last_part)
        attributes[name] = _parse_hcl_type_string(type_str)
    elif attrs_str.strip().endswith(","):
        raise HclTypeParsingError(
            f"Trailing comma found in attribute string: '{attrs_str}'"
        )
    return attributes


def _split_attr_part(part: str) -> tuple[str, str]:
    equal_sign_pos = part.find("=")
    if equal_sign_pos == -1:
        raise HclTypeParsingError(f"Malformed attribute part (missing '='): '{part}'")
    name = part[:equal_sign_pos].strip()
    type_str = part[equal_sign_pos + 1 :].strip()
    if not name or not type_str:
        raise HclTypeParsingError(f"Invalid attribute name or type in part: '{part}'")
    return name, type_str


def create_variable_cty(
    name: str,
    type_str: str,
    default_py: Any | None = None,
    description: str | None = None,
    sensitive: bool | None = None,
    nullable: bool | None = None,
) -> CtyValue[Any]:
    if not name or not name.isidentifier():
        raise HclFactoryError(
            f"Invalid variable name: '{name}'. Must be a valid identifier."
        )
    try:
        parsed_variable_type = _parse_hcl_type_string(type_str)
    except HclTypeParsingError as e:
        raise HclFactoryError(f"Invalid type string for variable '{name}': {e}") from e
    variable_attrs_py: dict[str, Any] = {"type": type_str}
    if description is not None:
        variable_attrs_py["description"] = description
    if sensitive is not None:
        variable_attrs_py["sensitive"] = sensitive
    if nullable is not None:
        variable_attrs_py["nullable"] = nullable
    if default_py is not None:
        try:
            parsed_variable_type.validate(default_py)
        except CtyError as e:
            raise HclFactoryError(
                f"Default value for variable '{name}' is not compatible with type '{type_str}': {e}"
            ) from e
        variable_attrs_py["default"] = default_py
    variable_attrs_schema: dict[str, CtyType[Any]] = {"type": CtyString()}
    if "description" in variable_attrs_py:
        variable_attrs_schema["description"] = CtyString()
    if "sensitive" in variable_attrs_py:
        variable_attrs_schema["sensitive"] = CtyBool()
    if "nullable" in variable_attrs_py:
        variable_attrs_schema["nullable"] = CtyBool()
    if "default" in variable_attrs_py:
        variable_attrs_schema["default"] = parsed_variable_type
    root_py_struct = {"variable": [{name: variable_attrs_py}]}
    root_schema = CtyObject(
        {
            "variable": CtyList(
                element_type=CtyObject({name: CtyObject(variable_attrs_schema)})
            )
        }
    )
    try:
        return root_schema.validate(root_py_struct)
    except CtyError as e:
        raise HclFactoryError(f"Internal error creating variable CtyValue: {e}") from e


def create_resource_cty(
    r_type: str,
    r_name: str,
    attributes_py: dict[str, Any],
    attributes_schema_py: dict[str, str] | None = None,
) -> CtyValue[Any]:
    if not r_type or not r_type.strip():
        raise HclFactoryError("Resource type 'r_type' cannot be empty.")
    if not r_name or not r_name.strip():
        raise HclFactoryError("Resource name 'r_name' cannot be empty.")
    attributes_cty_schema: dict[str, CtyType[Any]] = {}
    if attributes_schema_py is not None:
        for attr_name, attr_type_str in attributes_schema_py.items():
            try:
                attributes_cty_schema[attr_name] = _parse_hcl_type_string(attr_type_str)
            except HclTypeParsingError as e:
                raise HclFactoryError(
                    f"Invalid type string for attribute '{attr_name}' ('{attr_type_str}') in resource '{r_type}.{r_name}': {e}"
                ) from e
        for attr_name in attributes_py:
            if attr_name not in attributes_cty_schema:
                raise HclFactoryError(
                    f"Missing type string in attributes_schema_py for attribute '{attr_name}' of resource '{r_type}.{r_name}'."
                )
        resource_attributes_obj_type = CtyObject(attributes_cty_schema)
        try:
            resource_attributes_obj_type.validate(attributes_py)
        except CtyError as e:
            raise HclFactoryError(
                f"One or more attributes for resource '{r_type}.{r_name}' are not compatible with the provided schema: {e}"
            ) from e
    else:
        inferred_attributes_cty = auto_infer_cty_type(attributes_py)
        if isinstance(inferred_attributes_cty.type, CtyObject):
            attributes_cty_schema = inferred_attributes_cty.type.attribute_types
        else:
            raise HclFactoryError("Could not infer object type from attributes.")
    root_py_struct = {"resource": [{r_type: [{r_name: attributes_py}]}]}
    root_schema = CtyObject(
        {
            "resource": CtyList(
                element_type=CtyObject(
                    {
                        r_type: CtyList(
                            element_type=CtyObject(
                                {r_name: CtyObject(attributes_cty_schema)}
                            )
                        )
                    }
                )
            )
        }
    )
    try:
        return root_schema.validate(root_py_struct)
    except CtyError as e:
        raise HclFactoryError(f"Internal error creating resource CtyValue: {e}") from e
