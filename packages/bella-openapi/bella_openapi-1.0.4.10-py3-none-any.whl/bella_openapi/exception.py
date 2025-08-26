class AuthorizationException(Exception):
    def __init__(self, message, http_status_code=None):
        self.message = message
        self.http_stauts_code = http_status_code

    def __repr__(self):
        return f"AuthorizationError(message={self.message}, http_status_code={self.http_stauts_code})"
