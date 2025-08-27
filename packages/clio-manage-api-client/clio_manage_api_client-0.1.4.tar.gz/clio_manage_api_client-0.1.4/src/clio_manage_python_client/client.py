import requests
import aiohttp
from urllib.parse import urljoin
   
from .configs import *
from .classes.requests import Get, Put, Post, Patch, Delete, Download, All
from .db.response_handler import ResponseHandler
from .classes.responses import ResponseWrapper
from .utils import RateMonitor

class Client:
    if TYPE_CHECKING:
        get: "GetRequest"
        post: "PostRequest"
        create: "PostRequest"
        update: "PatchRequest"
        patch: "PatchRequest"
        delete: "DeleteRequest"
        download: "DownloadRequest"
        all: "AllRequests"

    request_methods = {
        "get": Get,
        "post": Post,
        "create": Post,
        "patch": Patch,
        "delete": Delete,
        "download": Download,
        "all": All,  # For auto paginating record retrieval 
        "put": Put # Unused
    }
        
    def __init__(self,
                 access_token: str,
                 region: str = "US",
                 api_version: int = 4,
                 default_rate_limit: int | None = None,
                 store_responses: bool = False,
                 db_path: str | None = None,
                 async_requests: bool = False):
            
        base_path = BASE_URL.get(region.lower(), BASE_URL['us'])  
        version_path = API_VERSION_PATH.get(api_version)
        
        if not version_path:
            raise ValueError(f"Unsupported API version: {api_version}. Supported versions: {list(API_VERSION_PATH.keys())}")

        self.base_url = urljoin(f"{base_path}/", f"{version_path}")

        # Set client to run as syncronous/async
        if async_requests:
            self.request_handler = self._async_request_handler
        else:
            self.request_handler = self._request_handler
            
        # Assign shutdown method dynamically
        self.shutdown = self.async_shutdown if async_requests else self.sync_shutdown
        self.session = None 
            
        self.response_handler = None
        
        self.set_bearer_token(access_token)
        self.set_response_handler(store_responses, db_path)
        
        # Initialize RateMonitor with optional default_limit
        self.rate_limiter = RateMonitor(**({"default_limit": default_rate_limit} if default_rate_limit is not None else {}))

        # Dynamically initialize and set request handlers as attributes
        for method in self.request_methods.keys():
            handler_class = self.request_methods[method]
            setattr(self, method, handler_class(self.base_url, self.request_handler))

    def __getattr__(self, item: str):
        """
        Forward attribute access to the appropriate request type.
        """
        for method in self.request_methods:
            handler = getattr(self, method, None)
            if handler and hasattr(handler, item):
                return getattr(handler, item)
        raise AttributeError(f"'Client' object has no attribute '{item}'")
    
    # Synchronous Requests
    def _make_request(self, api_url: str, method: str, params: dict = None, payload: dict = None, return_all=False):
        """
        Makes the actual HTTP request based on the method.
        Handles empty or non-JSON responses safely.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        params = params or {}

        try:
            # Make the request
            response = requests.request(
                method=method.upper(),
                url=api_url,
                headers=headers,
                params=params,
                json=payload,
            )
            response.raise_for_status()

            # Safely handle JSON or empty responses
            if response.content:
                try:
                    data = response.json()
                except ValueError:
                    # Response is not JSON
                    data = response.text
            else:
                data = None  # No content

            return data, response

        except requests.exceptions.RequestException as e:
            # Provide more info including raw response text if available
            resp_text = getattr(e.response, "text", "") if hasattr(e, "response") else ""
            raise RuntimeError(f"HTTP request failed: {e}. Response body: {resp_text}") from e


    def _request_handler(self, api_url: str, method: str, params: dict = None, payload: dict = None, return_all=False, **kwargs):
        """
        Handles requests, including support for paginated responses when return_all=True.
        """
        endpoint = api_url.split(self.base_url)[-1].split("?")[0]  # Extract endpoint from URL
        params = params or {}

        @self.rate_limiter(endpoint)
        def make_request():
            try:
                if method == "DOWNLOAD":
                    response_obj = self._download_content(api_url, params)
                    self.rate_limiter.update_rate_limits(endpoint, response_obj.headers)
                    return response_obj

                if return_all is False:
                    # Single request
                    response_json, response_obj = self._make_request(api_url, method, params, payload)
                    self.rate_limiter.update_rate_limits(endpoint, response_obj.headers)
                    if self.response_handler:
                        self.response_handler.add_response(response_obj, kwargs.get('call_metadata'))
                    return response_json

                # Paginated request
                all_results = []
                next_page_token = None
                current_url = api_url 
                
                while True:

                    if next_page_token:
                        current_url = next_page_token 
                        
                    response_json, response_obj = self._make_request(current_url, method, params, payload)

                    self.rate_limiter.update_rate_limits(endpoint, response_obj.headers)
                    if self.response_handler:
                        self.response_handler.add_response(response_obj, kwargs.get('call_metadata'))

                    all_results.extend(response_json.get("data", []))

                    next_page_token = response_json.get("meta", {}).get("paging", {}).get("next")
                    # print(next_page_token)
                    if not next_page_token:
                        break

                return {"data": all_results}

            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"API request failed: {e}")

        return make_request()
    
    def _download_content(self, url: str, params: dict = None):
        """
        Makes the actual HTTP request based on the method.
        """

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/pdf",
            }
        try:
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                raise requests.exceptions.RequestException(
                    f"Rate limited. Retry after {retry_after} seconds."
                )

            if response.status_code != 200:
                raise requests.exceptions.RequestException(f"HTTP {response.status_code}: {response.text}")

            return response
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}") from e

    #Asyncronous Requests         
    async def _make_async_request(self, url: str, method: str, params: dict = None, payload: dict = None):
        """
        Asynchronous HTTP request function using a persistent session.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        params = params or {}

        try:
            async with self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params or {},
                json=payload
            ) as response:
                response_json = await response.json(content_type=None)  # Extract JSON data
                response_text = await response.text()  # Extract raw text response
                response_content = await response.read()  # Extract binary content
                
                # Wrap response object
                response_obj = ResponseWrapper(
                    status_code=response.status,
                    headers=dict(response.headers),
                    json_data=response_json,
                    text=response_text,
                    content=response_content,
                    url=str(response.url),
                    reason=response.reason
                )

                return response_json, response_obj  # Return ResponseWrapper object
            
        except aiohttp.ClientError as e:
            raise RuntimeError(f"HTTP request failed: {e}") from e

    async def _async_request_handler(self, url: str, method: str, params: dict = None, payload: dict = None, return_all=False, **kwargs):
        """
        Handles requests, including paginated responses when return_all=True.
        """
        
        """Asynchronous HTTP request function."""
        if not self.session:  # Ensure session is initialized
            self.session = aiohttp.ClientSession()
            
        endpoint = url.split(self.base_url)[-1].split("?")[0]  # Extract endpoint from URL
        params = params or {}
        # print(f'Return All: {return_all}')

        @self.rate_limiter(endpoint)
        async def make_request():
            try:
                if method == "DOWNLOAD":
                    response_obj = await self._download_content_async(url, params)
                    self.rate_limiter.update_rate_limits(endpoint, response_obj.headers)
                    return response_obj

                if not return_all:
                    # Single request
                    response_json, response_obj = await self._make_async_request(url, method, params, payload)
                    self.rate_limiter.update_rate_limits(endpoint, response_obj.headers)

                    if self.response_handler:
                        self.response_handler.add_response(response_obj, kwargs.get('call_metadata'))  # No await needed

                    return response_json

                # Paginated request
                all_results = []
                next_page_token = None
                current_url = url
                
                while True:
                    if next_page_token:
                        current_url = next_page_token
                        
                    response_json, response_obj = await self._make_async_request(current_url, method, params, payload)

                    self.rate_limiter.update_rate_limits(endpoint, response_obj.headers)
                    if self.response_handler:
                        self.response_handler.add_response(response_obj, kwargs.get('call_metadata'))  # No await needed

                    all_results.extend(response_json.get("data", []))

                    next_page_token = response_json.get("meta", {}).get("paging", {}).get("next")
                    # print(next_page_token)
                    if not next_page_token:
                        break

                return {"data": all_results}

            except aiohttp.ClientError as e:
                raise RuntimeError(f"API request failed: {e}")

        return await make_request()
    
    async def _download_content_async(self, url: str, params: dict = None):
        """
        Asynchronously downloads content using a persistent session.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/pdf",
        }

        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 1))
                    raise RuntimeError(f"Rate limited. Retry after {retry_after} seconds.")

                if response.status != 200:
                    response_text = await response.text()
                    raise RuntimeError(f"HTTP {response.status}: {response_text}")

                return await response.read()  # Returns binary content (PDF)

        except aiohttp.ClientError as e:
            raise RuntimeError(f"HTTP request failed: {e}") from e
    
    def set_bearer_token(self, new_token: str):
        self.access_token = new_token
        
    def set_response_handler(self, store_responses: bool, db_path: str | None = None):
        """Dynamically sets or updates the response handler during runtime."""
        if db_path or store_responses:
            self.response_handler = ResponseHandler(db_path or "database.sqlite")
        else:
            self.response_handler = None
    
    def export_database(self, save_path="database_export.xlsx"):
        if self.response_handler:
            return self.response_handler.export_to_excel(save_path)

    async def async_shutdown(self):
        """Handles async shutdown tasks properly (response processing + session closure)."""
        if self.response_handler:
            print("Waiting for all responses to be processed...")
            self.response_handler.wait_for_completion()
            self.response_handler.stop_processing()

        # Close async session if it's open
        if self.session and not self.session.closed:
            print("Closing async session...")
            await self.session.close()
            print("Async session closed.")

        print("Client shutdown completed.")
        
    def sync_shutdown(self):
        """Handles sync shutdown tasks (response processing only)."""
        if self.response_handler:
            print("Waiting for all responses to be processed...")
            self.response_handler.wait_for_completion()
            self.response_handler.stop_processing()

        print("Client shutdown completed.")
        