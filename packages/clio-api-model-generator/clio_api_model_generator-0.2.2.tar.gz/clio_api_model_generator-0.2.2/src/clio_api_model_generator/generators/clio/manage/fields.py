import json
from pathlib import Path
from .config import TEMP_DIR_PATH

FIELDS_PATH = TEMP_DIR_PATH / "fields.py"

HEADER = """from dataclasses import dataclass
from typing import Optional
from .components import *

"""
pending_dataclasses = {}

def sanitize_name(name: str) -> str:
    """Sanitize field names to make them valid Python identifiers."""
    return name.replace("-", "_").replace(".", "_").replace(" ", "_").replace("[", "_").replace("]", "_")

#######
# I'm commenting this out until I can figure out whether the Schema references are a typo in the api specs or if it was on purpose
# It effects the most critical endpoints including: Matters, Documents, Contacts, Conversations, Tasks, and Customfields
# More details below
#######

# def topological_sort(pending_dataclasses):
#     # Step 1: Build dependency graph and in-degree count
#     graph = defaultdict(list)
#     in_degree = {key: 0 for key in pending_dataclasses}

#     for key, value in pending_dataclasses.items():
#         for dep in value.get("postponed_fields", []):
#             if dep in pending_dataclasses:  # Only consider existing dependencies
#                 graph[dep].append(key)
#                 in_degree[key] += 1

#     # Step 2: Find all keys with no dependencies (in-degree = 0)
#     zero_in_degree = deque([k for k in in_degree if in_degree[k] == 0])
#     sorted_keys = []

#     # Step 3: Process nodes with no dependencies
#     while zero_in_degree:
#         current = zero_in_degree.popleft()
#         sorted_keys.append(current)

#         for neighbor in graph[current]:
#             in_degree[neighbor] -= 1
#             if in_degree[neighbor] == 0:
#                 zero_in_degree.append(neighbor)

#     # Step 4: Check for cyclic dependencies
#     if len(sorted_keys) != len(pending_dataclasses):
#         raise ValueError("A cyclic dependency was detected in the pending classes.")

#     return sorted_keys

######
# In the API schema, some of the nested resources reference an "endpoint" component within another endpoint component
# Example: Lines 64,701 and 67,407 in the api_specs
# "$ref": "#/components/schemas/CustomFieldValue"
# I don't see a reason why "#/components/schemas/CustomFieldValue_base" would be an issue to reference instead
# Referencing an endpoint component when generating the dataclasses causes multiple 'referenced before assignment errors in the dynamically generated dataclasses
# The code that is commented out detects these discrepencies, saves them until the end, then reorders them to make sure all dependencies have been added prior to the class that depends on them
# Current version assumes its a typo and appends _base to the reference component
######

# def generate_field_dataclass_code(name: str, schema: dict, all_schemas: dict, generated_classes: set) -> str:
#     """
#     Generate dataclass for a specific schema by copying fields from the base class
#     and referencing nested resources.
#     """
#     global pending_dataclasses
    
#     if name in generated_classes:
#         return ""  # Avoid duplicate generation

#     name += "_Fields"
#     generated_classes.add(name)
#     dataclass_code = f"@dataclass\nclass {name}:\n"

#     # Process `allOf` to find the base schema and nested resources
#     all_of = schema.get("allOf", [])
#     if len(all_of) < 1:
#         dataclass_code += "    pass\n\n"
#         return dataclass_code

#     # First `allOf` item: base schema reference
#     base_schema_ref = all_of[0].get("$ref")
#     if base_schema_ref:
#         base_class_name = base_schema_ref.split("/")[-1]
#         dataclass_code += f"    # Fields directly copied from {base_class_name}\n"
#         base_schema = all_schemas.get(base_class_name)
#         if base_schema:
#             # Copy fields from the base schema
#             for field_name, field_details in base_schema.get("properties", {}).items():
#                 field_type = map_field_type(field_details)
#                 sanitized_name = sanitize_name(field_name)
#                 dataclass_code += f"    {sanitized_name}: Optional[{field_type}] = None\n"

#     # Second `allOf` item: nested resources
#     if len(all_of) > 1:
#         nested_properties = all_of[1].get("properties", {})
#         if nested_properties:
#             dataclass_code += f"\n    # Nested resource fields\n"
#             postponed_fields = []
#             for field_name, field_details in nested_properties.items():
#                 nested_ref = field_details.get("$ref")
#                 if not nested_ref:
#                     nested_ref = field_details.get("items", {}).get("$ref")
#                 if nested_ref:
#                     nested_class_name = nested_ref.split("/")[-1]
                    
#                     #Postpone adding dataclass until the end if a base class is not referenced
#                     #Append _Fields now since it's no longer referencing the schema object
#                     if "_base" not in nested_class_name:
#                         nested_class_name += "_Fields"
#                         postponed_fields.append(nested_class_name)
                        
#                     dataclass_code += f"    {field_name}: Optional[{nested_class_name}] = None\n"
                    
#             if len(postponed_fields) > 0:
#                 dataclass_code += "\n"
#                 pending_dataclasses[name] = {
#                     "postponed_fields": postponed_fields,
#                     "code": dataclass_code
#                 }
#                 print(name, postponed_fields)
#                 return ""
        
#     dataclass_code += "\n"
#     return dataclass_code

##
# Replaces endpoint references with base endpoint name
##
def generate_field_dataclass_code(name: str, schema: dict, all_schemas: dict, generated_classes: set) -> str:
    """
    Generate dataclass for a specific schema by copying fields from the base class
    and referencing nested resources.
    """
    global pending_dataclasses
    
    if name in generated_classes:
        return ""  # Avoid duplicate generation

    name += "_Fields"
    generated_classes.add(name)
    dataclass_code = f"@dataclass\nclass {name}:\n"

    # Process `allOf` to find the base schema and nested resources
    all_of = schema.get("allOf", [])
    if len(all_of) < 1:
        dataclass_code += "    pass\n\n"
        return dataclass_code

    # First `allOf` item: base schema reference
    base_schema_ref = all_of[0].get("$ref")
    if base_schema_ref:
        base_class_name = base_schema_ref.split("/")[-1]
        dataclass_code += f"    # Fields directly copied from {base_class_name}\n"
        base_schema = all_schemas.get(base_class_name)
        if base_schema:
            # Copy fields from the base schema
            for field_name, field_details in base_schema.get("properties", {}).items():
                field_type = map_field_type(field_details)
                sanitized_name = sanitize_name(field_name)
                dataclass_code += f"    {sanitized_name}: Optional[{field_type}] = None\n"

    # Second `allOf` item: nested resources
    if len(all_of) > 1:
        nested_properties = all_of[1].get("properties", {})
        if nested_properties:
            dataclass_code += f"\n    # Nested resource fields\n"
            for field_name, field_details in nested_properties.items():
                nested_ref = field_details.get("$ref")
                if not nested_ref:
                    nested_ref = field_details.get("items", {}).get("$ref")
                if nested_ref:
                    nested_class_name = nested_ref.split("/")[-1]
                    if "_base" not in nested_class_name:
                        nested_class_name += "_base"
 
                    dataclass_code += f"    {field_name}: Optional[{nested_class_name}] = {nested_class_name}\n"
                    
    dataclass_code += "\n"
    return dataclass_code

def map_field_type(field_schema: dict) -> str:
    """Map OpenAPI field types to Python types."""
    if "$ref" in field_schema:
        # Reference to another schema
        return field_schema["$ref"].split("/")[-1]
    prop_type = field_schema.get("type", "Any")
    if prop_type == "integer":
        return "int"
    elif prop_type == "number":
        return "float"
    elif prop_type == "boolean":
        return "bool"
    elif prop_type == "string":
        return "str"
    elif prop_type == "array":
        items = field_schema.get("items", {})
        item_type = map_field_type(items)
        return f"List[{item_type}]"
    elif prop_type == "object":
        return "dict"
    return "Any"

def generate_field_dataclasses(api_specs, export_mapping = False):
    global pending_dataclasses
    FIELDS_PATH.parent.mkdir(parents=True, exist_ok=True)

    if "components" not in api_specs or "schemas" not in api_specs["components"]:
        print("No schemas found in the OpenAPI spec.")
        return

    all_schemas = api_specs["components"]["schemas"]
    generated_classes = set()


    target_schemas = {k: v for k, v in all_schemas.items() if "_" not in k}

    with open(FIELDS_PATH, "w") as f:
        f.write(HEADER)
        for schema_name, schema in target_schemas.items():
            dataclass_code = generate_field_dataclass_code(schema_name, schema, all_schemas, generated_classes)
            f.write(dataclass_code)
        
        ########
        # This is when they get sorted
        ########
        # sorted_keys = topological_sort(pending_dataclasses)
        # for key in sorted_keys:
        #     if key in pending_dataclasses:
        #         code = pending_dataclasses[key].get("code", "")
        #         if code:
        #             f.write(code)
    
    # Mapping for "_list" or "_show" schemas to their referenced schemas
    list_show_mapping = {}

    for schema_name, schema in all_schemas.items():
        if "_list" in schema_name.lower() or "_show" in schema_name.lower():
            properties = schema.get("properties", {})
            data_property = properties.get("data")

            if data_property:
                if data_property.get("type") == "array":
                    # Handle the case where the schema is in an array
                    items = data_property.get("items", {})
                    ref = items.get("$ref")
                else:
                    # Handle the case where the schema is directly referenced
                    ref = data_property.get("$ref")

                if ref:
                    # Extract the schema name from the reference path
                    referenced_schema = ref.split("/")[-1]
                    referenced_schema += "_Fields"
                    list_show_mapping[schema_name] = referenced_schema


    if export_mapping:
        mapping_file_path = Path("endpoint_field_mapping.json")
        with open(mapping_file_path, "w") as json_file:
            json.dump(list_show_mapping, json_file, indent=4)

        print(f"Mapping saved to {mapping_file_path}")

    print(f"Dataclasses generated in {FIELDS_PATH}")
    return list_show_mapping

if __name__ == "__main__":
    generate_field_dataclasses()
