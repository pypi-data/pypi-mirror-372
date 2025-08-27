# pyvider-hcl

`pyvider-hcl` is a Python library for parsing HCL (HashiCorp Configuration Language) into `pyvider.cty` types. It provides a simple and intuitive way to work with HCL data in your Python applications.

This library is mostly a wrapper around the excellent `python-hcl2` library. `pyvider-hcl` differentiates itself by providing:

- **Seamless `pyvider.cty` Integration:** `pyvider-hcl` is designed to work with `pyvider.cty` out of the box. It parses HCL directly into `CtyValue` objects, making it easy to integrate with other `pyvider` tools.
- **Simplified API:** `pyvider-hcl` provides a simplified API for parsing HCL and creating Terraform variables and resources.
- **Automatic Type Inference:** `pyvider-hcl` can automatically infer `CtyType` from HCL data, saving you the hassle of defining a schema for every HCL file.

## Features

- Parse HCL strings and files into `pyvider.cty` values.
- Automatically infer `CtyType` from HCL data.
- Validate HCL data against a `CtyType` schema.
- Create `CtyValue` objects for Terraform variables and resources.

## Installation

To install `pyvider-hcl`, you can use `uv`:

```bash
uv pip install pyvider-hcl
```

## Usage

Here's a simple example of how to use `pyvider-hcl` to parse an HCL string:

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyString

hcl_string = """
  name = "Jules"
  age = 30
"""

cty_value = parse_hcl_to_cty(hcl_string)

pretty_print_cty(cty_value)
```

You can also parse an HCL file:

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty

with open("my_config.hcl", "r") as f:
    hcl_content = f.read()
    cty_value = parse_hcl_to_cty(hcl_content)
    pretty_print_cty(cty_value)
```

### Schema Validation

You can validate HCL data against a `CtyType` schema:

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyObject, CtyString, CtyNumber

schema = CtyObject({
    "name": CtyString(),
    "age": CtyNumber(),
})

hcl_string = """
  name = "Jules"
  age = "thirty" # Invalid type
"""

try:
    cty_value = parse_hcl_to_cty(hcl_string, schema=schema)
except Exception as e:
    print(e)
```

### Complex Cty Integration Examples

Here are some more complex examples of how to use `pyvider-hcl` with `pyvider.cty`:

#### Parsing a list of objects

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyObject, CtyList, CtyString, CtyNumber

hcl_string = """
  users = [
    {
      name = "Jules"
      age  = 30
    },
    {
      name = "Vincent"
      age  = 40
    }
  ]
"""

schema = CtyObject({
    "users": CtyList(
        element_type=CtyObject({
            "name": CtyString(),
            "age": CtyNumber(),
        })
    )
})

cty_value = parse_hcl_to_cty(hcl_string, schema=schema)

pretty_print_cty(cty_value)
```

#### Parsing nested objects

```python
from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty
from pyvider.cty import CtyObject, CtyString, CtyNumber

hcl_string = """
  config = {
    server = {
      host = "localhost"
      port = 8080
    }
    database = {
      host = "localhost"
      port = 5432
    }
  }
"""

schema = CtyObject({
    "config": CtyObject({
        "server": CtyObject({
            "host": CtyString(),
            "port": CtyNumber(),
        }),
        "database": CtyObject({
            "host": CtyString(),
            "port": CtyNumber(),
        }),
    })
})

cty_value = parse_hcl_to_cty(hcl_string, schema=schema)

pretty_print_cty(cty_value)
```

### Creating Terraform Variables and Resources

You can use the factory functions to create `CtyValue` objects for Terraform variables and resources:

```python
from pyvider.hcl import (
    parse_hcl_to_cty,
    pretty_print_cty,
    create_variable_cty,
    create_resource_cty,
)

# Create a variable
variable_cty = create_variable_cty(
    name="my_variable",
    type_str="string",
    default_py="my_default_value",
)

pretty_print_cty(variable_cty)

# Create a resource
resource_cty = create_resource_cty(
    r_type="my_resource",
    r_name="my_instance",
    attributes_py={
        "name": "my_resource_name",
        "value": 123,
    },
)

pretty_print_cty(resource_cty)
```