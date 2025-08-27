#!/usr/bin/env python3
# pyvider-hcl/tests/test_parser.py

from pathlib import Path
import unittest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValue,
)
from pyvider.cty.exceptions import CtyValidationError
from pyvider.hcl import HclParsingError, parse_hcl_to_cty
from pyvider.hcl.parser import auto_infer_cty_type

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class TestHclParser(unittest.TestCase):
    def load_fixture(self, name: str) -> str:
        return (FIXTURE_DIR / name).read_text()

    def test_parse_simple_hcl_no_schema_inferred(self) -> None:
        hcl_content = self.load_fixture("simple_valid.hcl")
        result = parse_hcl_to_cty(hcl_content)
        self.assertIsInstance(result, CtyValue)
        self.assertIsInstance(result.type, CtyObject)
        default_val = result.value["variable"].value[0].value["name"].value["default"]
        self.assertEqual(default_val.value, "example_from_file")

    def test_parse_invalid_hcl_syntax_error(self) -> None:
        hcl_content = self.load_fixture("invalid_syntax.hcl")
        with self.assertRaisesRegex(HclParsingError, "Failed to parse HCL"):
            parse_hcl_to_cty(hcl_content)

    def test_parse_with_string_schema_validation_pass(self) -> None:
        hcl_content = 'my_attr = "A raw HCL string"'
        schema = CtyObject({"my_attr": CtyString()})
        result = parse_hcl_to_cty(hcl_content, schema=schema)
        self.assertEqual(result.value["my_attr"].value, "A raw HCL string")

    def test_parse_with_nested_object_schema_pass(self) -> None:
        hcl_content = self.load_fixture("nested_object_valid.hcl")
        schema = CtyObject(
            {"config": CtyList(element_type=CtyObject(
                {
                    "name": CtyString(),
                    "owner": CtyObject(
                        {
                            "name": CtyString(),
                            "contact": CtyObject({"email": CtyString(), "phone": CtyString()}),
                        }
                    ),
                    "threshold": CtyNumber(),
                    "enabled": CtyBool(),
                    "tags": CtyList(element_type=CtyString()),
                }
            ))}
        )
        result = parse_hcl_to_cty(hcl_content, schema=schema)
        config_val = result.value["config"].value[0]
        self.assertEqual(config_val.value["owner"].value["contact"].value["email"].value, "admin@example.com")

    def test_parse_with_list_of_nested_objects_schema_pass(self) -> None:
        hcl_content = self.load_fixture("list_of_nested_objects_valid.hcl")
        item_spec_schema = CtyObject({"feature_a": CtyString(), "feature_b": CtyBool()})
        item_schema = CtyObject({"id": CtyString(), "value": CtyNumber(), "spec": item_spec_schema})
        schema = CtyObject(
            {"item_group": CtyList(element_type=CtyObject(
                {"items": CtyList(element_type=item_schema), "group_name": CtyString()}
            ))}
        )
        result = parse_hcl_to_cty(hcl_content, schema=schema)
        items_list_val = result.value["item_group"].value[0].value["items"]
        self.assertEqual(len(items_list_val.value), 2)
        self.assertEqual(items_list_val.value[0].value["id"].value, "item1")

    def test_parse_with_list_of_nested_objects_schema_fail(self) -> None:
        hcl_content = self.load_fixture("list_of_nested_objects_invalid.hcl")
        item_spec_schema = CtyObject({"feature_a": CtyString(), "feature_b": CtyBool()})
        item_schema = CtyObject({"id": CtyString(), "value": CtyNumber(), "spec": item_spec_schema})
        schema = CtyObject(
            {"item_group": CtyList(element_type=CtyObject(
                {"items": CtyList(element_type=item_schema), "group_name": CtyString()}
            ))}
        )
        with self.assertRaises(HclParsingError) as cm:
            parse_hcl_to_cty(hcl_content, schema=schema)
        self.assertIn("Schema validation failed", str(cm.exception))
        self.assertIsInstance(cm.exception.__cause__, CtyValidationError)

    def test_auto_infer_cty_type_basic_types(self) -> None:
        raw_data = {"a_string": "hello", "a_bool": True, "a_number": 123.45, "a_null": None}
        result_val = auto_infer_cty_type(raw_data)
        self.assertIsInstance(result_val.value["a_string"].type, CtyString)
        self.assertIsInstance(result_val.value["a_bool"].type, CtyBool)
        self.assertIsInstance(result_val.value["a_number"].type, CtyNumber)
        self.assertTrue(result_val.value["a_null"].is_null)

    def test_auto_infer_cty_type_nested_structures(self) -> None:
        raw_data = {"a_list": ["x", False, 2], "an_object": {"nested_str": "world"}}
        result_val = auto_infer_cty_type(raw_data)
        self.assertIsInstance(result_val.value["a_list"].type, CtyList)
        self.assertIsInstance(result_val.value["an_object"].type, CtyObject)
        self.assertIsInstance(result_val.value["an_object"].value["nested_str"].type, CtyString)

    def test_auto_infer_cty_type_empty_structures(self) -> None:
        raw_data = {"empty_list": [], "empty_object": {}}
        result_val = auto_infer_cty_type(raw_data)
        self.assertIsInstance(result_val.value["empty_list"].type, CtyList)
        self.assertIsInstance(result_val.value["empty_object"].type, CtyObject)
        self.assertEqual(len(result_val.value["empty_list"].value), 0)
        self.assertEqual(len(result_val.value["empty_object"].value), 0)
