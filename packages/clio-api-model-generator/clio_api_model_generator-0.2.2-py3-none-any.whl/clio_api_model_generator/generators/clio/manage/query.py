import keyword

from .config import *
QUERY_PATH = TEMP_DIR_PATH / "query.py"

HEADER = """from dataclasses import dataclass
from typing import Optional, List, Literal
import datetime

"""

def format_class_name(name: str) -> str:
    """
    Convert a snake_case or other formatted name to PascalCase.
    Examples:
      - "activityrate_update" -> "ActivityRateUpdate"
      - "bankaccount_index" -> "BankAccountIndex"
      - "reportschedule_update" -> "ReportScheduleUpdate"
    """
    parts = name.replace("_", " ").split()
    return "".join(part.capitalize() for part in parts)

def transform_param_name(name: str) -> str:
    """
    Sanitize parameter names to make them valid Python identifiers.
    - Replaces invalid characters (e.g., `[`, `-`, etc.) with `_`.
    - Appends `_` to reserved Python keywords.
    """
    name = name.replace("[", "__").replace("]", "").replace(".", "_").replace("/", "_").replace("-", "_")
    if keyword.iskeyword(name):
        name += "_"
    return name

def map_param_type(param_schema: dict) -> str:
    """
    Map OpenAPI parameter schema types to Python types.
    """
    param_type = param_schema["type"]

    if param_type == "array":
        item_type = param_schema["items"]["type"]
        python_type = f"List[{item_type.capitalize()}]"
    elif param_type == "integer":
        python_type = "int"
    elif param_type == "number":
        python_type = "float"
    elif param_type == "boolean":
        python_type = "bool"
    elif param_type == "string" and "enum" in param_schema:
        # Handle enum values
        enum_values = param_schema["enum"]
        python_type = f"Literal[{', '.join([repr(e) for e in enum_values])}]"
    elif param_type == "string" and param_schema.get("format") == "date-time":
        python_type = "datetime.datetime"
    elif param_type == "string" and param_schema.get("format") == "date":
        python_type = "datetime.date"
    else:
        python_type = "str"  # Default for strings

    return python_type

def generate_query_dataclass(class_name: str, parameters: list):
    """
    Generate query dataclass with formatted class name.
    """
    QUERY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not QUERY_PATH.exists():
        with open(QUERY_PATH, "w") as f:
            f.write(HEADER)

    formatted_class_name = class_name

    with open(QUERY_PATH, "a") as f:
        f.write(f"@dataclass\nclass {formatted_class_name}:\n")

        # Separate required and optional fields
        required_fields = [
            param for param in parameters if param.get("required", False)
        ]
        optional_fields = [
            param for param in parameters if not param.get("required", False)
        ]

        # Add required fields first
        for param in required_fields:
            param_name = transform_param_name(param["name"])
            python_type = map_param_type(param["schema"])
            f.write(f"    {param_name}: {python_type}\n")

        # Add optional fields
        for param in optional_fields:
            param_name = transform_param_name(param["name"])
            python_type = map_param_type(param["schema"])
            f.write(f"    {param_name}: Optional[{python_type}] = None\n")

        f.write("\n")
