from typing import Dict, Type, Optional
from .endpoints import Endpoints as EndpointDefinitions

class Endpoints:
    """
    Registry for storing endpoint metadata, including paths,
    query models, and request body models.
    """

    registry: Dict[str, Dict[str, Optional[Type]]] = {}

    @classmethod
    def initialize_registry(cls):
        """
        Dynamically initialize the registry by parsing the `Endpoints` class
        from `models.endpoints`.
        """
        for name, metadata in EndpointDefinitions.registry.items():
            cls.registry[name] = {
                "path": metadata["path"],
                "method": metadata["method"],
                "query_model": metadata.get("query_model"),
                "request_body_model": metadata.get("request_body_model"),
                'field_model': metadata.get("field_model")
            }

    @classmethod
    def get_endpoint(cls, name: str) -> Optional[Dict[str, Type]]:
        """
        Retrieve endpoint metadata by name.

        :param name: The name of the endpoint to retrieve.
        :return: A dictionary containing endpoint metadata or None if not found.
        """
        return cls.registry.get(name)

# Initialize the registry dynamically from the models.endpoints
Endpoints.initialize_registry()
