import inspect
import json
import requests
from pathlib import Path
import yaml

from .config import *

from .components import generate_component_dataclasses
from .fields import generate_field_dataclasses
from .query import generate_query_dataclass
from .request_body import generate_request_body_dataclass
from .endpoints import generate_endpoint_registry, generate_method_hints

def filter_kwargs(func, kwargs):
    """Filter kwargs to only those accepted by func."""
    sig = inspect.signature(func)
    return {k: v for k, v in kwargs.items() if k in sig.parameters}

def download_api_specs(dest_path=DOWNLOADED_SPEC_PATH) -> Path | None:
    try:
        response = requests.get(SPEC_FILE_URL)
        if response.status_code == 200:
            with open(dest_path, 'wb') as file:
                file.write(response.content)
            print(f'✅ OpenAPI spec downloaded to: {dest_path}')
            return dest_path
        else:
            print(f'❌ Failed to download spec file, status: {response.status_code}')
            return None
    except requests.RequestException as e:
        print(f'❌ Error downloading file: {e}')
        return None
        
def load_openapi_spec(file_path=None):
    """Loads an OpenAPI spec file (JSON or YAML) and returns it as a Python dictionary."""

    if file_path is None:
        file_path = download_api_specs()
        if file_path is None:
            raise RuntimeError("Failed to download OpenAPI spec.")

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Spec file does not exist: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        if file_path.suffix == ".json":
            return json.load(file)
        elif file_path.suffix in (".yaml", ".yml"):
            return yaml.safe_load(file)
        else:
            raise ValueError(f"Unsupported file extension: {file_path.suffix}")

def generate_models(file_path=None, output_dir=SCRIPT_DIR, **kwargs):
    """
    Generate all dataclass models from the OpenAPI spec.
    If no file_path is provided, the latest spec will be downloaded.
    """
    openapi_spec = load_openapi_spec(file_path)

    paths = openapi_spec.get("paths", {})
    endpoint_definitions = []

    generate_component_dataclasses(openapi_spec)
    field_mapping = generate_field_dataclasses(openapi_spec)
    # print(field_mapping)
    for path, methods in paths.items():
        for method, details in methods.items():
            # Format the class name
            class_name = details["operationId"].replace("#", "_").replace(".", "_").capitalize()

            # Generate query dataclass
            parameters = details.get("parameters", [])
            responses = details.get("responses", {})
            summary = details.get("summary")
            description = details.get("description")
            
            field_model = None
            field = responses.get("200",{}).get("content",{}).get("application/json; charset=utf-8",{}).get("schema",{}).get("$ref")
            if not field:
                field = responses.get("201",{}).get("content",{}).get("application/json; charset=utf-8",{}).get("schema",{}).get("$ref")
            if field:
                list_show_mapping_key = field.split("/")[-1]
                field_model = field_mapping.get(list_show_mapping_key)
                
            query_model_name = f"{class_name}_Query"
            if parameters:
                generate_query_dataclass(query_model_name, parameters)

            # Prepare endpoint metadata for registry
            endpoint = {
                "name": class_name,
                "path": path,
                "method": method.upper(),
                "query_model": query_model_name if parameters else None,
                "request_body_model": None,
                "field_model": field_model
                
            }

            # Generate request body dataclass if present
            if "requestBody" in details:
                request_body_model_name = f"{class_name}_RequestBody"
                generate_request_body_dataclass(request_body_model_name, details["requestBody"])
                endpoint["request_body_model"] = request_body_model_name

            if summary is not None:
                endpoint["summary"] = summary
            if description is not None:
                endpoint["description"] = description
                
            # Append to endpoint definitions
            endpoint_definitions.append(endpoint)

    # Generate endpoints dynamically in the registry
    generate_endpoint_registry(endpoint_definitions)
    generate_method_hints(endpoint_definitions)
    export_temp_contents(target_path=output_dir, **kwargs)
    
def update(**kwargs):
    # Filter kwargs for download_api_specs
    download_kwargs = filter_kwargs(download_api_specs, kwargs)
    dest_path = download_kwargs.get('dest_path', None)

    # Call download_api_specs with filtered kwargs
    file_path = download_api_specs(**download_kwargs)

    # Prepare kwargs for generate_models
    generate_kwargs = filter_kwargs(generate_models, kwargs)

    # Pass file_path from download_api_specs to generate_models if not provided
    if 'file_path' not in generate_kwargs or generate_kwargs['file_path'] is None:
        generate_kwargs['file_path'] = file_path

    generate_models(**generate_kwargs)