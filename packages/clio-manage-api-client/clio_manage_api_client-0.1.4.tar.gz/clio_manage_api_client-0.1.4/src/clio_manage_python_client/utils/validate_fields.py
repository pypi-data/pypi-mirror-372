
from typing import get_origin, get_args, Optional, Union
from dataclasses import is_dataclass

def build_field_list(dataclass_obj, prefix=""):
    """
    Constructs a list of fields by inspecting the fields and types
    of the provided dataclass object using __annotations__.
    """
    field_list = []

    # Loop through fields and their types using __annotations__
    for field_name, field_type in dataclass_obj.__annotations__.items():
        # Unwrap Optional or Union to get the actual type
        origin = get_origin(field_type)
        args = get_args(field_type)
        actual_type = args[0] if origin is Optional or origin is Union else field_type

        # Build the field name with the prefix
        full_field_name = f"{prefix}{field_name}" if prefix else field_name

        # Check if the actual type is a dataclass
        if is_dataclass(actual_type):
            # Treat as a nested resource and expand its fields recursively
            field_list.extend(build_field_list(actual_type, prefix=f"{full_field_name}."))
        else:
            field_list.append(full_field_name)

    return field_list

def expand_all_fields(dataclass_obj, provided_field_string):
    """
    Expands the 'all' keyword in the provided field string by replacing it with
    all non-nested fields of the corresponding dataclass.

    Args:
        dataclass_obj: The target dataclass object to validate against.
        provided_field_string: A string containing the fields to validate.

    Returns:
        str: A string with 'all' replaced by actual field names.
    """
    def get_non_nested_fields(dataclass_obj):
        """Returns a list of non-nested fields (non-dataclass fields)."""
        non_nested_fields = []
        for field_name, field_type in dataclass_obj.__annotations__.items():
            origin = get_origin(field_type)
            args = get_args(field_type)
            actual_type = args[0] if origin is Optional or origin is Union else field_type

            if not is_dataclass(actual_type):
                non_nested_fields.append(field_name)

        return non_nested_fields

    def process_nested_fields(dataclass_obj, field_string):
        """Process nested 'all' occurrences within curly braces."""
        result = []
        stack = []
        current_field = ""
        inside_braces = False

        for char in field_string:
            if char == '{':
                stack.append(current_field.strip())
                result.append(f"{current_field.strip()}{{")
                current_field = ""
                inside_braces = True
            elif char == '}':
                inside_braces = False
                parent = stack.pop()
                parent_class = dataclass_obj.__annotations__.get(parent)

                if parent_class:
                    origin = get_origin(parent_class)
                    args = get_args(parent_class)
                    actual_type = args[0] if origin is Optional or origin is Union else parent_class

                    if is_dataclass(actual_type):
                        if "all" in current_field:
                            nested_fields = get_non_nested_fields(actual_type)
                            result.append(",".join(nested_fields) + "}")
                        else:
                            result.append(current_field.strip() + "}")
                current_field = ""
            elif char == ',':
                if not inside_braces:
                    if current_field.strip() == "all":
                        result.append(",".join(get_non_nested_fields(dataclass_obj)))
                    else:
                        result.append(current_field.strip())
                    current_field = ""
                else:
                    current_field += char
            else:
                current_field += char

        if current_field.strip() == "all":
            result.append(",".join(get_non_nested_fields(dataclass_obj)))
        elif current_field:
            result.append(current_field.strip())

        return ",".join(result)

    return process_nested_fields(dataclass_obj, provided_field_string)

def validate_field_string(dataclass_obj, provided_field_string: str):
    """
    Validates whether all provided fields exist in the given dataclass.
    Removes invalid fields and returns a dictionary with the updated string and removed fields.

    Args:
        dataclass_obj: The target dataclass object to validate against.
        provided_field_string: A string containing the fields to validate.

    Returns:
        dict: {
            "valid_string": str,   # String with all invalid fields removed and proper format maintained
            "removed_fields": list # List of invalid fields that were removed
        }
    """
    provided_field_string = provided_field_string.strip()

    if 'all' in provided_field_string:
        provided_field_string = expand_all_fields(dataclass_obj, provided_field_string)

    valid_fields = set(build_field_list(dataclass_obj))
    provided_fields = parse_field_string(provided_field_string)

    removed_fields = [field for field in provided_fields if field not in valid_fields]
    
    valid_fields_only = [field for field in provided_fields if field in valid_fields]

    def rebuild_field_string(fields):
        nested_dict = {}
        for field in fields:
            parts = field.split('.')
            d = nested_dict
            for part in parts[:-1]:
                d = d.setdefault(part, {})
            d[parts[-1]] = None
        
        def build_string(d):
            result = []
            for key, value in d.items():
                if isinstance(value, dict) and value:
                    result.append(f"{key}{{{build_string(value)}}}")
                else:
                    result.append(key)
            return ",".join(result)

        return build_string(nested_dict)

    valid_string = rebuild_field_string(valid_fields_only)

    return {
        "valid_string": valid_string,
        "removed_fields": removed_fields
    }

def parse_field_string(field_string):
    """
    Parses the provided field string into a list of field paths.

    Args:
        field_string (str): The field string to parse.

    Returns:
        list: A list of parsed field paths.
    """
    field_list = []
    stack = []
    current_field = ""

    for char in field_string:
        if char == '{':
            stack.append(current_field)
            current_field = ""
        elif char == '}':
            if stack:
                parent = stack.pop()
                nested_fields = current_field.split(',')
                field_list.extend([f"{parent}.{field.strip()}" for field in nested_fields])
            current_field = ""
        elif char == ',':
            if not stack:
                field_list.append(current_field.strip())
                current_field = ""
            else:
                current_field += char
        else:
            current_field += char

    if current_field:
        field_list.append(current_field.strip())

    return field_list

def build_id_field_string(dataclass_obj):
    """
    Constructs a string of all resources that contain an 'id' or 'etag' field,
    including nested resources. Limits nesting to one level to match API constraints.

    Args:
        dataclass_obj: The target dataclass object to inspect.

    Returns:
        str: A formatted string with all resources containing 'id' or 'etag' fields,
             limited to immediate nested resources only.
    """

    def extract_id_fields(dataclass_obj, allow_nesting=True):
        fields_with_id_or_etag = []
        has_id = False
        has_etag = False

        for field_name, field_type in dataclass_obj.__annotations__.items():
            origin = get_origin(field_type)
            args = get_args(field_type)
            actual_type = args[0] if origin is Optional or origin is Union else field_type

            # Track presence of 'id' and 'etag' fields
            if field_name == "id":
                has_id = True
            if field_name == "etag":
                has_etag = True

            # Check if the field is a nested dataclass
            if is_dataclass(actual_type) and allow_nesting:
                nested_fields = extract_id_fields(actual_type, allow_nesting=False)  # Disable further nesting
                nested_fields = [f for f in nested_fields if f in ["id", "etag"]]  # Only include id and etag
                if nested_fields:
                    fields_with_id_or_etag.append(f"{field_name}{{{','.join(nested_fields)}}}")

        # Add top-level 'id' and 'etag' fields if present
        if has_id:
            fields_with_id_or_etag.insert(0, "id")
        if has_etag:
            fields_with_id_or_etag.insert(1, "etag")

        return fields_with_id_or_etag

    id_fields_list = extract_id_fields(dataclass_obj)
    return ",".join(id_fields_list)