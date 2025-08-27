from typing import Dict, Any, List
from ..models.models_registry import Endpoints

from .base import BaseRequest, EndpointBase, DownloadEndpointBase

class MethodHandler(BaseRequest):
    """
    Generalized class to handle HTTP requests by method.
    """
    def __init__(self, base_url: str, request_handler, method: str):
        super().__init__(base_url)
        self.request_handler = request_handler
        self.method = method.upper()
        self.base_endpoints = self._initialize_base_endpoints()

    def _initialize_base_endpoints(self) -> Dict[str, EndpointBase]:
        grouped = self._group_endpoints()
        return {
            base_path: EndpointBase(self.base_url, base_path, endpoints, self.request_handler)
            for base_path, endpoints in grouped.items()
        }

    def _group_endpoints(self) -> Dict[str, List[Dict[str, Any]]]:
        grouped = {}
        for name, metadata in Endpoints.registry.items():
            if metadata["method"].upper() == self.method:
                base_path = self._extract_base_path(metadata["path"])
                grouped.setdefault(base_path, []).append({"name": name, **metadata})
        return grouped

    def _extract_base_path(self, path: str) -> str:
        """Extract the base path."""
        return path.lstrip('/').split('/')[0].replace(".json", "")

    def __getattr__(self, item):
        if item in self.base_endpoints:
            return self.base_endpoints[item]
        raise AttributeError(f"Base endpoint '{item}' not found.")
    
class Get(MethodHandler):
    def __init__(self, base_url: str, request_handler):
        super().__init__(base_url, request_handler, method="GET")

class Post(MethodHandler):
    def __init__(self, base_url: str, request_handler):
        super().__init__(base_url, request_handler, method="POST")

class Patch(MethodHandler):
    def __init__(self, base_url: str, request_handler):
        super().__init__(base_url, request_handler, method="PATCH")

class Delete(MethodHandler):
    def __init__(self, base_url: str, request_handler):
        super().__init__(base_url, request_handler, method="DELETE")

class Put(MethodHandler):
    def __init__(self, base_url: str, request_handler):
        super().__init__(base_url, request_handler, method="PUT")

class All(Get):
    """
    Class to handle "All" requests, behaving like Get but always setting return_all=True for the index method.
    """
    def __init__(self, base_url: str, request_handler):
        super().__init__(base_url, request_handler)

    def __getattr__(self, item):
        """
        Override to inject return_all=True for the index method.
        """
        original_method = super().__getattr__(item)


        def index_with_return_all(*args, **kwargs):
            kwargs["return_all"] = True
            return original_method(*args, **kwargs)
        return index_with_return_all

    
class Download(BaseRequest):
    """
    Class to handle Download requests.
    """
    def __init__(self, base_url: str, request_handler):
        super().__init__(base_url)
        self.request_handler = request_handler
        self.base_endpoints = self._initialize_base_endpoints()

        # Automatically set a default endpoint if only one exists
        self.default_base_endpoint = (
            next(iter(self.base_endpoints.values())) if len(self.base_endpoints) == 1 else None
        )

    def _initialize_base_endpoints(self) -> Dict[str, DownloadEndpointBase]:
        """
        Initialize and group download endpoints into DownloadEndpointBase objects.
        """
        grouped = self._group_endpoints()
        return {
            base_path: DownloadEndpointBase(self.base_url, base_path, endpoints, self.request_handler)
            for base_path, endpoints in grouped.items()
        }

    def _group_endpoints(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group endpoints by their base paths for easier organization and access.
        """
        grouped = {}
        for name, metadata in Endpoints.registry.items():
            if metadata["method"].upper() == "DOWNLOAD":
                base_path = self._extract_base_path(metadata["path"])
                grouped.setdefault(base_path, []).append({"name": name, **metadata})
        return grouped

    def _extract_base_path(self, path: str) -> str:
        """
        Extract the base path from the API path, handling inconsistent .json placement.
        """
        segments = path.lstrip('/').split('/')
        return segments[0].replace(".json", "")

    def __getattr__(self, item: str) -> DownloadEndpointBase:
        """
        Access specific base endpoints by their name.
        """
        if item in self.base_endpoints:
            return self.base_endpoints[item]
        raise AttributeError(f"Base endpoint '{item}' not found.")

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Directly call the default download endpoint if only one exists.
        """
        if not self.default_base_endpoint:
            raise ValueError(
                "There is no default download endpoint because there are multiple base endpoints."
            )
        return self.default_base_endpoint(**kwargs)