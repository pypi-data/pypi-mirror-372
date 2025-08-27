from .config import *
COMPONENT_PATH = TEMP_DIR_PATH / "components.py"

HEADER = """from dataclasses import dataclass
from typing import Optional, List, Literal, Any
import datetime

"""

def sanitize_name(name: str) -> str:
    """Sanitize field names to make them valid Python identifiers."""
    return name.replace("-", "_").replace(".", "_").replace(" ", "_").replace("[", "_").replace("]", "_")

def map_property_type(field_component: dict) -> str:
    """Map OpenAPI property types to Python types."""
    prop_type = field_component.get("type", "any")
    format_type = field_component.get("format", None)

    if prop_type == "integer":
        return "int"
    elif prop_type == "number":
        return "float"
    elif prop_type == "boolean":
        return "bool"
    elif prop_type == "string":
        if format_type == "date-time":
            return "datetime.datetime"
        elif format_type == "date":
            return "datetime.date"
        elif "enum" in field_component:
            return f"Literal[{', '.join(repr(e) for e in field_component['enum'])}]"
        return "str"
    elif prop_type == "array":
        items = field_component.get("items", {})
        item_type = map_property_type(items)
        return f"List[{item_type}]"
    elif prop_type == "object":
        return "dict"
    return "Any"

def generate_component_dataclass_code(component_name: str, component: dict) -> None:
    """
    Generate component dataclass with proper type mappings, handling nested objects.
    """
    COMPONENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not COMPONENT_PATH.exists():
        with open(COMPONENT_PATH, "w") as f:
            f.write(HEADER)

    def process_component(name: str, component: dict, generated_classes: set) -> None:
        """
        Recursively process component for nested objects, ensuring required fields
        are listed before optional fields.
        """
        if name in generated_classes:
            return  # Avoid duplicate generation
        generated_classes.add(name)

        dataclass_code = f"@dataclass\nclass {name}:\n"
        properties = component.get("properties", {})
        required = set(component.get("required", []))

        # Separate required and optional fields
        required_fields = {k: v for k, v in properties.items() if k in required}
        optional_fields = {k: v for k, v in properties.items() if k not in required}

        # Add required fields
        for field_name, field_component in required_fields.items():
            if field_component.get("type") == "object":
                nested_class_name = f"{name}_{sanitize_name(field_name).capitalize()}"
                process_component(nested_class_name, field_component, generated_classes)
                python_type = nested_class_name
            else:
                python_type = map_property_type(field_component)

            sanitized_name = sanitize_name(field_name)
            dataclass_code += f"    {sanitized_name}: {python_type}\n"

        # Add optional fields
        for field_name, field_component in optional_fields.items():
            if field_component.get("type") == "object":
                nested_class_name = f"{name}_{sanitize_name(field_name).capitalize()}"
                process_component(nested_class_name, field_component, generated_classes)
                python_type = nested_class_name
            else:
                python_type = map_property_type(field_component)

            sanitized_name = sanitize_name(field_name)
            dataclass_code += f"    {sanitized_name}: Optional[{python_type}] = None\n"

        if not properties:
            dataclass_code += "    pass\n"  # Handle empty classes

        dataclass_code += "\n"
        with open(COMPONENT_PATH, "a") as f:
            f.write(dataclass_code)

    formatted_class_name = component_name
    process_component(formatted_class_name, component, set())

def generate_component_dataclasses(api_specs):
    """Generates dataclasses from OpenAPI component schemas."""

    components = api_specs.get("components", {}).get("schemas", {})

    if not components:
        print("No schemas found in the OpenAPI spec.")
        return

    # Prioritize components containing "_base", otherwise fallback to components without "_"
    filtered_components = [
        name for name in components if "_base" in name
    ] or [
        name for name in components if "_" not in name
    ]

    count = len(filtered_components)

    for component_name in filtered_components:
        generate_component_dataclass_code(component_name, components[component_name])

    print(f"Dataclasses generated in {COMPONENT_PATH}, Count: {count}")

    
if __name__ == "__main__":
    generate_component_dataclasses()
