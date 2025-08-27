#!/usr/bin/env python3
# pyvider/hcl/parser.py

from decimal import Decimal
import logging
from pathlib import Path
from typing import Any

import hcl2

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyType,
    CtyValue,
)
from pyvider.cty.exceptions import CtyError as CtySchemaError
from pyvider.hcl.exceptions import HclParsingError

logger = logging.getLogger(__name__)


def _auto_infer_value_to_cty(raw_value: Any) -> CtyValue:
    """Recursively infers a Python value to its corresponding CtyValue."""
    if raw_value is None:
        return CtyDynamic().validate(None)
    if isinstance(raw_value, str):
        return CtyString().validate(raw_value)
    if isinstance(raw_value, bool):
        return CtyBool().validate(raw_value)
    if isinstance(raw_value, int | float | Decimal):
        return CtyNumber().validate(raw_value)
    if isinstance(raw_value, list):
        return CtyList(element_type=CtyDynamic()).validate(raw_value)
    if isinstance(raw_value, dict):
        inferred_attrs = {k: _auto_infer_value_to_cty(v) for k, v in raw_value.items()}
        inferred_attr_types = {k: v.type for k, v in inferred_attrs.items()}
        obj_type = CtyObject(inferred_attr_types)
        return CtyValue(vtype=obj_type, value=inferred_attrs)

    logger.warning(
        f"🔌🤖❓ Could not auto-infer CtyType for value: {raw_value} of type {type(raw_value)}. "
        f"Returning as CtyDynamic unknown."
    )
    return CtyValue.unknown(CtyDynamic())


def auto_infer_cty_type(raw_data: Any) -> CtyValue:
    """
    Automatically infers CtyType from raw Python data parsed by hcl2
    and wraps it in a CtyValue.
    """
    logger.debug(f"🔌🤖⏳ Auto-inferring CtyType for data of type: {type(raw_data)}")
    return _auto_infer_value_to_cty(raw_data)


def parse_hcl_to_cty(hcl_content: str, schema: CtyType | None = None) -> CtyValue:
    """Parse HCL directly into validated CtyValues using pyvider.cty types."""
    logger.debug(
        f"🔌🔍⏳ Parsing HCL content. Schema provided: {'Yes' if schema else 'No'}"
    )

    try:
        raw_data = hcl2.loads(hcl_content)
    except Exception as e:
        logger.error(f"🔌❗❌ HCL parsing itself failed: {e}")
        raise HclParsingError(message=f"Failed to parse HCL: {e}") from e

    if schema:
        logger.debug(
            f"🔌✔️⏳ Validating parsed HCL data against provided schema: {schema!r}"
        )
        try:
            validated_value = schema.validate(raw_data)
            logger.debug("🔌✔️✅ Schema validation successful.")
            return validated_value
        except CtySchemaError as e:
            logger.error(f"🔌❗❌ Schema validation failed: {e}")
            raise HclParsingError(
                message=f"Schema validation failed after HCL parsing: {e}"
            ) from e
    else:
        logger.debug(
            "🔌🤖⏳ No schema provided, auto-inferring CtyType from parsed data."
        )
        inferred_value = auto_infer_cty_type(raw_data)
        logger.debug("🔌🤖✅ CtyType auto-inference complete.")
        return inferred_value


def parse_with_context(content: str, source_file: Path | None = None) -> Any:
    """
    Parses HCL content and provides richer error context if parsing fails.
    Returns raw parsed data (typically dict/list), not CtyValue directly.
    """
    logger.debug(
        f"🔌📄⏳ Parsing HCL content. Source: {source_file if source_file else 'string input'}"
    )
    try:
        return hcl2.loads(content)
    except Exception as e:
        logger.error(
            f"🔌❗❌ HCL parsing error encountered. Source: {source_file}, Error: {e}"
        )
        raise HclParsingError(
            message=str(e), source_file=str(source_file) if source_file else None
        ) from e
