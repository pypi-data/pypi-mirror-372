# MObject: A Python Base Object for Nested Property Management and Type-Safe Object Handling

## Overview

`MObject` is an abstract base class designed to provide a robust framework for handling nested properties, translating keys, and managing types efficiently in Python projects. It offers utilities for working with complex object hierarchies, nested key mappings, and type-safe property assignment while supporting serialization to dictionaries. In addition, the base provides features for calculator interfaces.

### Naming Convention for Properties

`MObject` uses a specific naming convention for property annotations to aid in type handling and key translation:
- **`_k`**: Indicates a configuration key.
- **`_i`**: Indicates an input properties.
- **`_r`**: Indicates a result property.

This convention makes it easier to manage and validate properties dynamically while maintaining clear code semantics.

## Key Features

- **Nested Property Management**: Access and modify nested object properties dynamically using dot-notation.
- **Type-Safe Property Handling**: Automatically validate and set properties based on their type annotations.
- **Key Translation**: Translate camel-case keys to snake_case for internal use and vice versa for external representation.
- **Serialization**: Convert objects to dictionaries, supporting complex types like lists, dictionaries, NumPy arrays, and Enums.
- **Flexible Initialization**: Configure initialization using build orders and custom mappings.
- **Enum Management**: Seamlessly handle Enums with support for string and integer values.
- **Logging Support**: Provides a logging interface to track issues and warnings.

## Installation


```bash
pip install mobject-klixz
```

## Usage

### Defining a Subclass

Create a subclass of `MObject` to leverage its functionality. Annotate properties using Python's type hints for automatic type inference and validation.

```python
from typing import List, Dict
from enum import Enum

class Status(Enum):
    ACTIVE = 1
    INACTIVE = 0

class MyObject(MObject):
    _name_k: str
    _age_i: int
    _attributes_r: Dict[str, float]
    _status_k: Status

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
```

### Creating an Instance

You can create an instance of your subclass using camelcase keyword arguments:

```python
obj = MyObject(Name="Example", Age=25, Attributes={"height": 5.9}, Status=Status.ACTIVE)
```

### Accessing and Setting Nested Properties

Retrieve and modify nested properties dynamically:

```python
# Get a nested property
nested_value = obj.get_nested_property(["attributes", "height"])

# Set a nested property
obj.set_nested_property(["attributes", "weight"], 70.5)
```

### Serializing to a Dictionary

Convert the object to a dictionary representation:

```python
obj_dict = obj.to_dict()
print(obj_dict)
```

### Translating Keys

`MObject` automatically translates camel-case keys to snake_case for internal use and vice versa:

```python
# Input keys (external)
print(obj.InputKeys)

# Result keys (external)
print(obj.ResultKeys)
```

### Enum Handling

Set enum values dynamically:

```python
status = MyObject.set_enum("active", Status)
print(status)  # Output: Status.ACTIVE
```

## API Reference

### Methods

#### `get_nested_property(obj, props, serializable=False)`
Recursively retrieves a nested property from an object.

#### `set_nested_property(obj, props, val, translate=False)`
Recursively sets a nested property on an object.

#### `set_enum(val, enum)`
Converts a string, integer, or Enum instance into a valid Enum instance.

#### `set(cls, val)`
Creates an instance of the class from a dictionary or another instance of the same class.

#### `collect_annotations(cls)`
Collects type annotations from the class and its base classes.

#### `to_dict()`
Serializes the object into a dictionary, supporting various data types.

### Properties

#### `InputKeys`
List of translated input keys.

#### `ResultKeys`
List of translated result keys.

#### `ClassName`
Returns the name of the class.

## Logging

The framework uses Python's `logging` module. You can configure the logger named `mobject` to control the log level and output format:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mobject')
```

## Examples

### Example 1: Simple Object

```python
class SimpleObject(MObject):
    value_k: int
    description_i: str

obj = SimpleObject(value=42, description="A simple example.")
print(obj.to_dict())
```

### Example 2: Nested Properties

```python
class NestedObject(MObject):
    metadata_k: Dict[str, Any]

nested = NestedObject(metadata={"info": {"author": "John Doe", "version": 1.0}})
print(nested.get_nested_property(["metadata", "info", "author"]))  # Output: John Doe
```

## Contributing

Contributions are welcome! Please submit issues or pull requests to enhance the functionality or fix bugs.

## License

This project is licensed under the MIT License.

## Acknowledgments

Special thanks to the Python community for the powerful tools and libraries that make this possible.

