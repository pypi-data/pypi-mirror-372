import json

def load_and_sort_openapi_spec(file_path, output_path=None):
    # Load the OpenAPI spec JSON file
    with open(file_path, 'r') as file:
        openapi_spec = json.load(file)
    
    # Check if components.schemas exists
    if "components" in openapi_spec and "schemas" in openapi_spec["components"]:
        schemas = openapi_spec["components"]["schemas"]
        
        # Separate schemas into categories
        no_underscore = {k: v for k, v in schemas.items() if "_" not in k}
        ends_with_base = {k: v for k, v in schemas.items() if k.endswith("_base")}
        remaining = {k: v for k, v in schemas.items() if k not in no_underscore and not k.endswith("_base")}
        
        # Sort each category
        sorted_no_underscore = dict(sorted(no_underscore.items()))
        sorted_ends_with_base = dict(sorted(ends_with_base.items()))
        sorted_remaining = dict(sorted(remaining.items()))
        
        # Merge the sorted categories
        sorted_schemas = {
            **sorted_no_underscore,
            **sorted_ends_with_base,
            **sorted_remaining
        }
        
        # Update the spec
        openapi_spec["components"]["schemas"] = sorted_schemas
        print("Schemas sorted successfully!")
    else:
        print("No schemas found in the OpenAPI spec.")
        return openapi_spec  # Return the original spec if no schemas found

    # Save the updated spec to a new file if output_path is provided
    if output_path:
        with open(output_path, 'w') as file:
            json.dump(openapi_spec, file, indent=2)
        print(f"Updated OpenAPI spec saved to {output_path}")
    
    return openapi_spec

if __name__ == "__main__":
    input_file = 'openapi.json'  # Replace with your input OpenAPI spec file path
    output_file = 'openapi_sorted.json'  # Replace with your desired output file path
    sorted_spec = load_and_sort_openapi_spec(input_file, output_file)
