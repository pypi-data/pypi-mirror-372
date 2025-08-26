from contextvars import ContextVar
from typing import Optional

trace_id_context: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
caller_id_context: ContextVar[Optional[str]] = ContextVar("caller_id", default=None)
request_url_context: ContextVar[Optional[str]] = ContextVar("request_url", default=None)
