from urllib.parse import urlencode
from typing import Dict, Any, Optional, Type, List, Union, Tuple, get_origin, get_args, Literal
from datetime import datetime
import typing_inspect
import logging

from dataclasses import fields, is_dataclass

from ..configs import *
from ..utils.validate_fields import validate_field_string, build_id_field_string

if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO,  # default level
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

logger = logging.getLogger(__name__)

def is_optional_type(field_type):
    """
    Check if a given type is Optional.
    """
    return get_origin(field_type) is Union and type(None) in get_args(field_type)

class BaseRequest:
    """
    Base class for handling API requests.
    """
    def __init__(self, base_url: str, base_path=""):
        self.base_url = base_url
        self.base_path = base_path
        self.logger = logging.getLogger(self.__class__.__name__)

    def format_url(self, path: str, query_params: Dict[str, Any] = None) -> str:
        return f"{self.base_url}{path}"
    
    @staticmethod
    def convert_array_field(field_name: str, value: Any, item_type: Type) -> Any:
        """
        Convert and validate array query parameters based on API requirements.
        
        :param field_name: The name of the field being processed.
        :param value: The input value for the array.
        :param item_type: The expected type of the array elements.
        :return: A validated and converted value based on array size and field name.
        """
        logger = logging.getLogger("BaseRequest.convert_array_field")
        try:
            # Ensure the value is treated as a list
            if not isinstance(value, list):
                if isinstance(value, str):
                    # Split string values by commas (common in query params)
                    value = value.split(",")
                else:
                    value = [value]

            # Validate and convert each item in the array
            converted_array = []
            for v in value:
                # Attempt to convert individual items to the expected type
                if item_type == int:
                    converted_array.append(int(v))
                elif item_type == float:
                    converted_array.append(float(v))
                elif item_type == str:
                    converted_array.append(str(v))
                else:
                    return {"error": f"Unsupported item type for field '{field_name}': {item_type}"}

            # Additional logic for array fields
            if "__" in field_name:
                # Split the field name into parts
                parts = field_name.split("__")
                
                # If text exists after the double underscore, apply special logic
                if len(parts) > 1 and parts[1]:
                    if len(converted_array) == 1:
                        # Convert single-element lists to a single integer
                        return converted_array[0]
                    else:
                        # Join multiple elements into a comma-delimited string
                        return ",".join(map(str, converted_array))
                else:
                    # No text after double underscore, return as a list
                    return converted_array

            # Default behavior for fields without double underscores
            return converted_array
        
        except (ValueError, TypeError) as e:
            
            logger.error("Invalid value for array field '%s': %s", field_name, e)
            return {"error": f"Invalid value for array field '{field_name}': {e}"}
    
    def validate_and_convert(self, field_name: str, field_type: Type, value: Any, required: bool) -> Any:
        """
        Enhanced validation and conversion method for handling filters, literals, and arrays.
        """
        # print(field_name,field_type,value,required)
        # Handle required fields
        if required and value is None:
            return None  # Validation fails for required fields that are None

        # Skip validation for optional fields with None value
        if not required and value is None:
            print("Required field '%s' not provided", field_name)
            self.logger.error("Required field '%s' not provided", field_name)
            return None

        if value is not None:
            origin = get_origin(field_type)
            args = get_args(field_type)

            # Handle datetime objects
            if isinstance(value, datetime):
                return value.isoformat()  # Convert datetime to ISO 8601 string
            
            # Handle array-like fields based on the field name
            if "__" in field_name:
                
                # Determine if the field is a list and process accordingly
                if origin is list:
                    item_type = args[0] if args else Any
                    if isinstance(value, str):
                        # Convert a single comma-delimited string into a list
                        value = value.split(",")
                    # Validate and format each filter in the list
                    validated_filters = [
                        self.validate_and_convert(field_name, item_type, v, required=False)
                        for v in value
                    ]
                    # Check for errors in validation
                    errors = [v for v in validated_filters if isinstance(v, dict) and "error" in v]
                    if errors:
                        return {"error": f"Invalid value for field '{field_name}': {errors}"}
                    # Return as a comma-separated string
                    return ",".join(map(str, validated_filters))

                # Fix for integer <int64> arrays
                if origin is Union and any(arg is int for arg in args):
                    for i, v in enumerate(value):
                        if not isinstance(v, int):
                            try:
                                # Try to convert the value to an integer
                                value[i] = int(v)
                            except (ValueError, TypeError):
                                return None
                    return value
                
                # Fallback for single-element fields
                if origin is None:
                    return self.validate_and_convert(field_name, args[0] if args else Any, value, required)

            # Handle Literal types explicitly
            # https://github.com/unigrated-solutions/clio-matters-customfield-order-management/blob/b5d9a44798e1bba593958f4708fa4d80979de1b2/api.py
            if typing_inspect.is_literal_type(field_type):
                valid_values = get_args(field_type)
                if "date" not in field_name:
                    # Try to find a case-insensitive match and return the correctly cased version
                    if isinstance(value, str):
                        for valid in valid_values:
                            if isinstance(valid, str) and valid.lower() == value.lower():
                                return valid  # Return corrected casing
                    if value not in valid_values:
                        return {
                            "error": f"Invalid value for field '{field_name}': Expected one of {valid_values}, got '{value}'."
                        }
                return value

            # Handle Union types (including Optional)
            if origin is Union:
                if type(None) in args and value is None:
                    return None
                for sub_type in args:
                    converted_value = self.validate_and_convert(field_name, sub_type, value, required)
                    if converted_value is not None:
                        return converted_value
                return {"error": f"Invalid value for field '{field_name}': {value} does not match any type in {args}."}
            
            if origin is list:
                item_type = args[0] if args else Any

                # Ensure the value is a list
                if not isinstance(value, list):
                    print(f"ERROR: Field '{field_name}' must be a list, got {type(value).__name__}")
                    return None

                # If expecting a list of dictionaries, return as-is
                if item_type == dict and all(isinstance(v, dict) for v in value):
                    return value 

                # Convert each item to the expected type
                validated_list = [self.validate_and_convert(field_name, item_type, v, required=False) for v in value]

                # Ensure no validation errors exist
                errors = [v for v in validated_list if isinstance(v, dict) and "error" in v]
                if errors:
                    print(f"Validation error for '{field_name}': {errors}")
                    return None

                return validated_list

            # Handle primitive types
            try:
                if field_type == int:
                    return int(value)
                elif field_type == float:
                    return float(value)
                elif field_type == bool:
                    if isinstance(value, str):
                        return value.lower() in ["true", "1"]
                    return bool(value)
                elif field_type == str:
                    return str(value)
                
            except (ValueError, TypeError) as e:
                self.logger.error("Validation error for field '%s': %s", field_name, e)
                return {"error": f"Invalid value for field '{field_name}': Expected {field_type}, got {type(value).__name__}."}

        return None


    def build_payload(self, request_body_model: Type, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the payload for a request body
        """

        def process_model(model: Type, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
            """
            Process a model recursively, validating and converting fields as needed.
            """
            payload = {}
            errors = {}

            for field_name, field_type in model.__annotations__.items():
                # print(field_name, field_type)
                # Use the provided field name for validation; apply mappings after validation
                original_field_name = field_name
                mapped_field_name = MAPPINGS.get(field_name, field_name)
                value = data.get(original_field_name)

                # Handle missing required fields
                origin = get_origin(field_type)
                args = get_args(field_type)
                is_optional = origin is Union and type(None) in args

                if value is None:
                    if not is_optional:
                        msg = f"'{original_field_name}' is required but not provided."
                        self.logger.error(msg)
                        errors[original_field_name] = msg
                        # raise ValueError(msg)
                    
                    continue

                # Process nested models
                if hasattr(field_type, "__annotations__"):
                    nested_payload, nested_errors = process_model(field_type, value)
                    if nested_errors:
                        errors[original_field_name] = nested_errors
                    else:
                        payload[mapped_field_name] = nested_payload
                else:
                    # Validate and convert field values
                    try:
                        if isinstance(value, datetime):
                            payload[mapped_field_name] = value.isoformat()  # Convert datetime to ISO format
                        else:
                            payload[mapped_field_name] = self.validate_and_convert(
                                original_field_name, field_type, value, required=True
                            )
                    except ValueError as e:
                        errors[original_field_name] = str(e)

            return payload, errors

        # Default to nest all kwargs under "data" if not explicitly provided
        payload_data = kwargs.get("data", {"data": kwargs})

        # Process the request body model
        payload, errors = process_model(request_body_model, payload_data)

        # Return the final payload and errors
        if errors:
            return {"payload": None, "errors": errors}
        return {"payload": payload, "errors": {}}

class EndpointBase:
    """
    Class for grouping and managing endpoints by base paths.
    """
    def __init__(self, base_url: str, base_path: str, endpoints: List[Dict[str, Any]], request_handler):
        self.base_url = base_url
        self.base_path = base_path
        self.endpoints = endpoints
        self.request_handler = request_handler

        self.index_method = None
        self.show_method = None
        self.post_method = None
        self.patch_method = None
        self.delete_method = None
        self.relations = []

        self._initialize_methods()

    def _initialize_methods(self):
        """
        Initialize methods for index, show, post, patch, delete, and relation endpoints.
        """
        for endpoint in self.endpoints:
            method = endpoint["method"].upper()
            segments = endpoint["path"].lstrip('/').split('/')

            if method == "GET":
                if len(segments) == 1 and segments[0].endswith('.json'):
                    self.index_method = endpoint
                elif len(segments) == 2 and ('{' in segments[1] or '}' in segments[1]):
                    self.show_method = endpoint
                else:
                    # Extract relation name from the last segment of the path
                    relation_name = segments[-1].replace(".json", "")
                    endpoint["relation_name"] = relation_name
                    self.relations.append(endpoint)
            elif method == "POST" and len(segments) == 1 and segments[0].endswith('.json'):
                self.post_method = endpoint
            elif method == "PATCH" and len(segments) == 2 and ('{' in segments[1] or '}' in segments[1]):
                self.patch_method = endpoint
            elif method == "DELETE" and len(segments) == 2 and ('{' in segments[1] or '}' in segments[1]):
                self.delete_method = endpoint
        
    def _format_path(self, path: str, kwargs: Dict[str, Any]) -> str:
        """
        Replace placeholders in the path with provided arguments.
        """
        
        while "{" in path and "}" in path:
            start = path.index("{")
            end = path.index("}") + 1
            placeholder = path[start + 1:end - 1]
            replacement = kwargs.pop(placeholder, kwargs.pop("id", None))  # Use "id" as a fallback
            if replacement is not None:
                path = path[:start] + str(replacement) + path[end:]
            else:
                raise ValueError(f"Missing required path parameter: '{placeholder}'")
        return path

    def _call_endpoint(self, metadata: dict, **kwargs):
        # Add models to kwargs for retrieve at the time of API call
        kwargs["call_metadata"] = metadata
        
        path = metadata["path"]
        query_model = metadata.get("query_model")
        request_body_model = metadata.get("request_body_model")
        field_model = metadata.get("field_model")
        method = metadata["method"].upper()
        
        use_field_model_for_fields = True  # default

        # If request_body_model exists, check if it has a field named 'fields'
        if request_body_model and "fields" in kwargs:
            for f in fields(request_body_model):
                # Check top-level
                if f.name == "fields":
                    use_field_model_for_fields = False
                    break

                # Check nested dataclass
                if is_dataclass(f.type):
                    nested_names = [sub_f.name for sub_f in fields(f.type)]
                    if "fields" in nested_names:
                        use_field_model_for_fields = False
                        break

        print("Use field model for 'fields'? ->", use_field_model_for_fields)
                    
        path = self._format_path(path, kwargs)

        query_params = {}
        validation_errors = {"query": {}, "data": {}}

        if field_model and "fields" in kwargs and use_field_model_for_fields:
            field_string = kwargs["fields"]
            if field_string == "all_ids":
                kwargs["fields"] = build_id_field_string(field_model)
            else:
                response = validate_field_string(field_model, field_string)
                kwargs["fields"] = response.get("valid_string")            
            
        # Validate 'response_fields' if provided, but only if we are NOT using the field model
        if "response_fields" in kwargs and not use_field_model_for_fields:
            field_string = kwargs["response_fields"]
            response = validate_field_string(field_model, field_string)
            kwargs["response_fields"] = response.get("valid_string")
            
        # Validate query parameters
        if query_model:
            for field, field_type in query_model.__annotations__.items():
                if field == "fields" and not use_field_model_for_fields:
                    continue
        
                mapped_field = MAPPINGS.get(field, field)

                value = kwargs.pop(mapped_field, kwargs.pop(field, None))

                if value is None and is_optional_type(field_type):
                    continue

                validated_value = BaseRequest(self.base_path).validate_and_convert(
                    field, field_type, value, required=not is_optional_type(field_type)
                )

                if isinstance(validated_value, dict) and "error" in validated_value:
                    validation_errors["query"][field] = validated_value["error"]
                elif validated_value is not None:
                    query_params[mapped_field] = validated_value

        # Validate request body
        payload = None
        if request_body_model:
            payload_result = BaseRequest.build_payload(BaseRequest(self.base_path), request_body_model, kwargs)
            payload = payload_result.get("payload")
            if payload_result.get("errors"):
                validation_errors["data"].update(payload_result["errors"])
                
        # Reinject response_fields into query_params if present as "fields"
        response_fields = kwargs.get("response_fields")
        if response_fields:
            query_params["fields"] = response_fields
            
        # If there are validation errors, return them
        if validation_errors["query"] or validation_errors["data"]:
            return {
                "url": BaseRequest.format_url(BaseRequest(self.base_url, self.base_path), path, query_params),
                "method": method,
                "params": query_params,
                "payload": payload,
                "errors": validation_errors,
            }

        api_url = BaseRequest.format_url(BaseRequest(self.base_url, self.base_path), path, query_params)

        return self.request_handler(api_url, method, query_params, payload, **kwargs)

    def __getattr__(self, method_type: str):
        """
        Dynamically handle method calls to EndpointBase.
        """
    
        if method_type in [relation["relation_name"] for relation in self.relations]:
            relation = next(r for r in self.relations if r["relation_name"] == method_type)
            return lambda **kwargs: self._call_endpoint(relation, **kwargs)
        elif method_type == "show" and self.show_method:
            return lambda **kwargs: self._call_endpoint(self.show_method, **kwargs)
        elif method_type == "index" and self.index_method:
            return lambda **kwargs: self._call_endpoint(self.index_method, **kwargs)
        elif method_type == "post" and self.post_method:
            return lambda **kwargs: self._call_endpoint(self.post_method, **kwargs)
        elif method_type == "patch" and self.patch_method:
            return lambda **kwargs: self._call_endpoint(self.patch_method, **kwargs)
        elif method_type == "delete" and self.delete_method:
            return lambda **kwargs: self._call_endpoint(self.delete_method, **kwargs)
        else:
            raise AttributeError(f"Method '{method_type}' not found for base endpoint '{self.base_path}'.")

    def __call__(self, **kwargs):
        """
        Default logic when the base endpoint is called directly.
        """

        if "id" in kwargs:
            # Prioritize 'show' for GET, or fallback to other methods if 'show' is not available
            if self.show_method and self.show_method["method"].upper() == "GET":
                return self._call_endpoint(self.show_method, **kwargs)
            elif self.post_method and self.post_method["method"].upper() == "POST":
                return self._call_endpoint(self.post_method, **kwargs)
            elif self.patch_method and self.patch_method["method"].upper() == "PATCH":
                return self._call_endpoint(self.patch_method, **kwargs)
            elif self.delete_method and self.delete_method["method"].upper() == "DELETE":
                return self._call_endpoint(self.delete_method, **kwargs)
            else:
                raise AttributeError(f"Show or compatible method not available for base endpoint '{self.base_path}'.")
        elif self.index_method and self.index_method["method"].upper() == "GET":
            return self._call_endpoint(self.index_method, **kwargs)
        elif self.post_method and self.post_method["method"].upper() == "POST":
            return self._call_endpoint(self.post_method, **kwargs)
        raise AttributeError(f"Index or compatible method not available for base endpoint '{self.base_path}'.")

    def get_request_body_params(self, model: Type) -> List[str]:
        """
        Recursively retrieve all parameters from the request body model.
        :param model: The top-level model class to traverse.
        :return: A flattened list of all parameters (including nested ones).
        """
        params = []

        # Check if the model has annotations (dataclass or Pydantic model)
        if hasattr(model, "__annotations__"):
            for field_name, field_type in model.__annotations__.items():
                # Add the current field name to the list
                params.append(field_name)

                # If the field type has annotations (nested model), recurse into it
                if hasattr(field_type, "__annotations__"):
                    nested_params = self.get_request_body_params(field_type)
                    # Prepend the field name to nested fields to retain the hierarchy
                    params.extend([f"{field_name}.{nested}" for nested in nested_params])

        return params

    def get_nested_required_params(self, model: Type) -> List[str]:
        """
        Recursively retrieve all required parameters from the request body model.
        :param model: The top-level model class to traverse.
        :return: A flattened list of all required parameters (including nested ones).
        """
        required_params = []

        # Check if the model has annotations (dataclass or Pydantic model)
        if hasattr(model, "__annotations__"):
            for field_name, field_type in model.__annotations__.items():
                # Determine if the field is required
                is_optional = is_optional_type(field_type)

                if not is_optional:
                    # Add the current field name to the list
                    required_params.append(field_name)

                    # If the field type has annotations (nested model), recurse into it
                    if hasattr(field_type, "__annotations__"):
                        nested_required = self.get_nested_required_params(field_type)
                        # Prepend the field name to nested fields to retain the hierarchy
                        required_params.extend([f"{field_name}.{nested}" for nested in nested_required])

        return required_params

    def get_required_params(self) -> Dict[str, List[str]]:
        """
        Retrieve the required parameters for each endpoint (query and body), including nested parameters.
        :return: A dictionary with 'query' and 'body' keys containing lists of required fields.
        """
        required_params = {"query": [], "body": []}

        # Check required query parameters
        if self.index_method and "query_model" in self.index_method:
            query_model = self.index_method["query_model"]
            if query_model:
                required_params["query"].extend(
                    [
                        field_name
                        for field_name, field_type in query_model.__annotations__.items()
                        if not is_optional_type(field_type)
                    ]
                )

        # Check required body parameters (including nested ones)
        if self.post_method and "request_body_model" in self.post_method:
            body_model = self.post_method["request_body_model"]
            if body_model:
                required_params["body"].extend(self.get_nested_required_params(body_model))

        return required_params

    def get_available_params(self) -> Dict[str, List[str]]:
        """
        Retrieve all available parameters for each endpoint (query and body), including nested parameters.
        :return: A dictionary with 'query' and 'body' keys containing lists of fields.
        """
        available_params = {"query": [], "body": []}

        # Get all query parameters
        if self.index_method and "query_model" in self.index_method:
            query_model = self.index_method["query_model"]
            if query_model:
                available_params["query"].extend(query_model.__annotations__.keys())

        # Get all body parameters (including nested ones)
        if self.post_method and "request_body_model" in self.post_method:
            body_model = self.post_method["request_body_model"]
            if body_model:
                available_params["body"].extend(self.get_request_body_params(body_model))

        return available_params

    def describe_endpoint(self, method: str) -> Dict[str, Any]:
        """
        Provide a detailed description of an endpoint, including required and available parameters.
        :param method: The HTTP method to describe (e.g., 'GET', 'POST').
        :return: A dictionary with metadata about the endpoint.
        """
        endpoint = getattr(self, f"{method.lower()}_method", None)
        if not endpoint:
            return {"error": f"No {method.upper()} endpoint available for this base path."}

        return {
            "path": endpoint["path"],
            "method": endpoint["method"],
            "required_params": self.get_required_params(),
            "available_params": self.get_available_params(),
        }
    
    def list_relations(self) -> List[str]:
        """
        List all available relational endpoints for this base path.
        :return: A list of relation names.
        """
        return [relation["relation_name"] for relation in self.relations]

    def describe_relation(self, relation_name: str) -> Dict[str, Any]:
        """
        Provide a detailed description of a relational endpoint.
        :param relation_name: The name of the relational endpoint to describe.
        :return: A dictionary with metadata about the relational endpoint.
        """
        relation = next((r for r in self.relations if r["relation_name"] == relation_name), None)
        if not relation:
            return {"error": f"No relation named '{relation_name}' found for this base path."}

        return {
            "relation_name": relation_name,
            "path": relation["path"],
            "method": relation["method"],
            "query_model": getattr(relation.get("query_model"), "__annotations__", {}),
            "required_query_params": [
                field_name
                for field_name, field_type in getattr(relation.get("query_model"), "__annotations__", {}).items()
                if not is_optional_type(field_type)
            ],
            "available_query_params": list(
                getattr(relation.get("query_model"), "__annotations__", {}).keys()
            ),
        }
        
class DownloadEndpointBase:
    """
    Class for grouping and managing download endpoints.
    """
    def __init__(self, base_url: str, base_path: str, endpoints: List[Dict[str, Any]], request_handler):
        self.base_url = base_url
        self.base_path = base_path
        self.index_method = None
        self.request_handler = request_handler
        self.relations = []
        self._initialize_methods(endpoints)

    def _initialize_methods(self, endpoints: List[Dict[str, Any]]):
        for endpoint in endpoints:
            self.index_method = endpoint

    def __call__(self, **kwargs):
        """
        Call the default download endpoint if it exists.
        """
        if not self.index_method:
            raise ValueError("No default download endpoint is defined.")
        return self._call_endpoint(self.index_method, **kwargs)

    def _format_path(self, path: str, kwargs: Dict[str, Any]) -> str:
        """
        Replace placeholders in the path with provided arguments.
        """
        while "{" in path and "}" in path:
            start = path.index("{")
            end = path.index("}") + 1
            placeholder = path[start + 1:end - 1]
            replacement = kwargs.pop(placeholder, kwargs.pop("id", None))  # Use "id" as a fallback
            if replacement is not None:
                path = path[:start] + str(replacement) + path[end:]
            else:
                raise ValueError(f"Missing required path parameter: '{placeholder}'")
        return path

    def _call_endpoint(self, metadata: dict, **kwargs):
        path = metadata["path"]
        query_model = metadata.get("query_model")
        request_body_model = metadata.get("request_body_model")
        method = metadata["method"].upper()
        
        # Format the path with provided arguments
        path = self._format_path(path, kwargs)

        # Extract and validate query parameters
        query_params = {}
        if query_model:
            for field, field_type in query_model.__annotations__.items():
                mapped_field = MAPPINGS.get(field, field)
                value = kwargs.pop(mapped_field, None)
                if value is not None:
                    query_params[field] = BaseRequest.validate_and_convert(
                        BaseRequest(self.base_path),
                        field,
                        field_type,
                        value,
                        required=(field in query_model.__annotations__),
                    )

        # Extract and validate request body parameters
        payload = None
        if request_body_model:
            payload_result = BaseRequest.build_payload(
                BaseRequest(self.base_path), request_body_model, kwargs
            )
            payload = payload_result.get("payload")
            if payload_result.get("errors"):
                return {
                    "url": BaseRequest.format_url(BaseRequest(self.base_url, self.base_path), path, query_params),
                    "method": metadata["method"].upper(),
                    "params": query_params,
                    "payload": None,
                    "errors": payload_result["errors"],
                }

        # Build the full URL
        url = BaseRequest.format_url(BaseRequest(self.base_url, self.base_path), path, query_params)
        
        return self.request_handler(url, method, query_params, payload)
      