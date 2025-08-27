from .config import *

REQUEST_BODY_PATH = TEMP_DIR_PATH / "request_body.py"

HEADER = """from dataclasses import dataclass
from typing import Optional, List, Literal
import datetime

"""

def sanitize_name(name: str) -> str:
    """Sanitize field names to make them valid Python identifiers."""
    return name.replace("-", "_").replace(".", "_").replace(" ", "_").replace("[", "_").replace("]", "_")

def map_param_type(field_schema: dict) -> str:
    """Map OpenAPI parameter types to Python types."""
    param_type = field_schema.get("type", "any")
    format_type = field_schema.get("format", None)

    if param_type == "integer":
        return "int"
    elif param_type == "number":
        return "float"
    elif param_type == "boolean":
        return "bool"
    elif param_type == "string":
        if format_type == "date-time":
            return "datetime.datetime"
        elif format_type == "date":
            return "datetime.date"
        elif "enum" in field_schema:
            return f"Literal[{', '.join(repr(e) for e in field_schema['enum'])}]"
        return "str"
    elif param_type == "array":
        items = field_schema.get("items", {})
        item_type = map_param_type(items)
        return f"List[{item_type}]"
    elif param_type == "object":
        return "dict"
    return "Any"

def generate_request_body_dataclass(class_name: str, request_body: dict) -> None:
    """
    Generate request body dataclass with proper type mappings, handling nested objects.
    """
    REQUEST_BODY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not REQUEST_BODY_PATH.exists():
        with open(REQUEST_BODY_PATH, "w") as f:
            f.write(HEADER)

    schema = request_body["content"]["application/json"]["schema"]

    def process_schema(name: str, schema: dict, generated_classes: set) -> None:
        """
        Recursively process schema for nested objects, ensuring required fields
        are listed before optional fields.
        """
        if name in generated_classes:
            return  # Avoid duplicate generation
        generated_classes.add(name)

        dataclass_code = f"@dataclass\nclass {name}:\n"
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        # Separate required and optional fields
        required_fields = {k: v for k, v in properties.items() if k in required}
        optional_fields = {k: v for k, v in properties.items() if k not in required}

        # Add required fields
        for field_name, field_schema in required_fields.items():
            if field_schema.get("type") == "object":
                nested_class_name = f"{name}_{sanitize_name(field_name).capitalize()}"
                process_schema(nested_class_name, field_schema, generated_classes)
                python_type = nested_class_name
            else:
                python_type = map_param_type(field_schema)

            sanitized_name = sanitize_name(field_name)
            dataclass_code += f"    {sanitized_name}: {python_type}\n"

        # Add optional fields
        for field_name, field_schema in optional_fields.items():
            if field_schema.get("type") == "object":
                nested_class_name = f"{name}_{sanitize_name(field_name).capitalize()}"
                process_schema(nested_class_name, field_schema, generated_classes)
                python_type = nested_class_name
            else:
                python_type = map_param_type(field_schema)

            sanitized_name = sanitize_name(field_name)
            dataclass_code += f"    {sanitized_name}: Optional[{python_type}] = None\n"

        if not properties:
            dataclass_code += "    pass\n"  # Handle empty classes

        dataclass_code += "\n"
        with open(REQUEST_BODY_PATH, "a") as f:
            f.write(dataclass_code)

    formatted_class_name = f"{class_name}"
    process_schema(formatted_class_name, schema, set())
    