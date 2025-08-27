class ResponseWrapper:
    """Wrapper for aiohttp responses to ensure compatibility with Sqlite response handler """

    def __init__(self, status_code, headers, json_data, text, content, url, reason=None):
        self.status_code = status_code
        self.headers = headers
        self._json_data = json_data
        self.text = text
        self.content = content
        self.url = url
        self.reason = reason

    def json(self):
        return self._json_data

    def raise_for_status(self):
        """Raise an exception if the response contains an HTTP error."""
        if 400 <= self.status_code < 600:
            raise RuntimeError(f"HTTP {self.status_code}: {self.text}")  # Mimics `requests.HTTPError`
