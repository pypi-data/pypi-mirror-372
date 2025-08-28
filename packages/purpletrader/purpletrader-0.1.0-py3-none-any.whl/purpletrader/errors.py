class HTTPError(Exception):
    def __init__(self, status_code: int, message: str, body: str | None = None):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.body = body


