import time
import re
import threading
from functools import wraps

class RateMonitor:
    def __init__(self, default_limit=50, base_url="https://app.clio.com/api/v4"):

        self.base_url = base_url
        self.default_limit = default_limit
        self.limits = {} 
        self.lock = threading.Lock()
        self.call_times = {} 

    def extract_base_endpoint(self, url: str) -> str:
        """
        Extracts the base endpoint from a given URL or endpoint string.
        """
        if url.startswith(self.base_url):
            url = url[len(self.base_url):]

        url = url.lstrip('/').rstrip('/')

        url = re.sub(r"/\{[^/]*\}", "", url)  # Remove placeholders like /{id}
        url = re.sub(r"/\d+", "", url)       # Remove numeric IDs like /12345

        # Step 4: Normalize the endpoint to the base path
        base_endpoint = url.split('/')[0] if url else ""
        base_endpoint = base_endpoint.replace(".json","")
        return base_endpoint
    
    def update_rate_limits(self, endpoint, response_headers):
        """
        Update the rate limit details for an endpoint based on response headers.
        """
        with self.lock:
            endpoint = self.extract_base_endpoint(endpoint)
            
            if endpoint not in self.limits:
                self.limits[endpoint] = {
                    "limit": self.default_limit,
                    "remaining": self.default_limit,
                    "reset": time.time() + 60, 
                    "retry_after": None
                }
            reset_timestamp = time.time()
            
            # Update from headers if available
            if "X-RateLimit-Limit" in response_headers:
                self.limits[endpoint]["limit"] = int(response_headers["X-RateLimit-Limit"])
            if "X-RateLimit-Remaining" in response_headers:
                self.limits[endpoint]["remaining"] = int(response_headers["X-RateLimit-Remaining"])
            if "X-RateLimit-Reset" in response_headers:
                reset_timestamp = int(response_headers["X-RateLimit-Reset"])
                self.limits[endpoint]["reset"] = reset_timestamp
            if "Retry-After" in response_headers:
                self.limits[endpoint]["retry_after"] = int(response_headers["Retry-After"])
            
            print(f"Rate limit for {endpoint}: {self.limits[endpoint]}")
            print(f"Limit resets in {int(reset_timestamp - time.time())} seconds")
            
    def __call__(self, endpoint):
        """
        Decorator to enforce the rate limit on a function for a specific endpoint.
        """
        def decorator(func):
            base_endpoint = self.extract_base_endpoint(endpoint)
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.lock:
                    if base_endpoint not in self.limits:
                        self.limits[base_endpoint] = {
                            "limit": self.default_limit,
                            "remaining": self.default_limit,
                            "reset": time.time() + 60,
                            "retry_after": None
                        }

                    limit_details = self.limits[base_endpoint]
                    current_time = time.time()

                    # Remove timestamps older than 60 seconds
                    self.call_times[base_endpoint] = [
                        t for t in self.call_times.get(base_endpoint, []) if current_time - t < 60
                    ]

                    if len(self.call_times[base_endpoint]) >= limit_details["limit"]:
                        # Calculate wait time based on reset time or first call
                        if current_time < limit_details["reset"]:
                            wait_time = limit_details["reset"] - current_time
                        else:
                            wait_time = 60 - (current_time - self.call_times[base_endpoint][0])
                        print(f"Rate limit exceeded for {base_endpoint}. Waiting for {wait_time:.2f} seconds.")
                        time.sleep(wait_time)

                    # Record the current call's timestamp
                    self.call_times[base_endpoint].append(time.time())
                    limit_details["remaining"] = max(0, limit_details["remaining"] - 1)

                return func(*args, **kwargs)

            return wrapper
        return decorator