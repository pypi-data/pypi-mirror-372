import textwrap

import pytest
from pyvider.cty import CtyString, CtyValue, CtyNumber, CtyBool, CtyList, CtyMap, CtyObject, CtyTuple, CtyDynamic
from pyvider.hcl.printer import pretty_print_cty
import io
import sys

def test_pretty_print_cty_string(capsys):
    """
    Tests that pretty_print_cty correctly prints a CtyString.
    """
    cty_val = CtyValue(value="hello", vtype=CtyString())
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    assert captured.out.strip() == '"hello"'

def test_pretty_print_cty_number(capsys):
    """
    Tests that pretty_print_cty correctly prints a CtyNumber.
    """
    cty_val = CtyValue(value=123, vtype=CtyNumber())
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    assert captured.out.strip() == "123"

def test_pretty_print_cty_bool(capsys):
    """
    Tests that pretty_print_cty correctly prints a CtyBool.
    """
    cty_val = CtyValue(value=True, vtype=CtyBool())
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    assert captured.out.strip() == "true"

def test_pretty_print_cty_list(capsys):
    """
    Tests that pretty_print_cty correctly prints a CtyList.
    """
    cty_val = CtyValue(value=["a", "b", "c"], vtype=CtyList(element_type=CtyString()))
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    expected = textwrap.dedent("""    [
      "a",
      "b",
      "c"
    ]""").strip()
    assert captured.out.strip() == expected

def test_pretty_print_cty_map(capsys):
    """
    Tests that pretty_print_cty correctly prints a CtyMap.
    """
    cty_val = CtyValue(value={"a": 1, "b": 2}, vtype=CtyMap(element_type=CtyNumber()))
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    expected = textwrap.dedent("""    {
      "a": 1,
      "b": 2
    }""").strip()
    assert captured.out.strip() == expected

def test_pretty_print_cty_object(capsys):
    """
    Tests that pretty_print_cty correctly prints a CtyObject.
    """
    cty_val = CtyValue(value={"name": "John", "age": 30}, vtype=CtyObject({"name": CtyString(), "age": CtyNumber()}))
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    expected = textwrap.dedent("""    {
      "name": "John",
      "age": 30
    }""").strip()
    assert captured.out.strip() == expected

def test_pretty_print_cty_tuple(capsys):
    """
    Tests that pretty_print_cty correctly prints a CtyTuple.
    """
    cty_val = CtyValue(value=["hello", 123], vtype=CtyTuple(tuple([CtyString(), CtyNumber()])))
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    expected = textwrap.dedent("""    [
      "hello",
      123
    ]""").strip()
    assert captured.out.strip() == expected

def test_pretty_print_cty_dynamic(capsys):
    """
    Tests that pretty_print_cty correctly prints a CtyDynamic.
    """
    cty_val = CtyValue(value="dynamic", vtype=CtyDynamic())
    pretty_print_cty(cty_val)
    captured = capsys.readouterr()
    assert captured.out.strip() == "dynamic"