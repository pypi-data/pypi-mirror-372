# -*- coding: utf-8 -*-
# ======================
# Date    : 2024/12/30
# Author  : Liu Yuchen
# Content : 
# 
# ======================
import os
import uuid
from contextvars import ContextVar

__all__ = ["TraceContext", "TRACE_ID"]


_trace_id = ContextVar("bella_trace_id", default="")
_mock_request = ContextVar("mock_request", default="false")


TRACE_ID = "X-BELLA-TRACE-ID"
MOCK_REQUEST = "X-BELLA-MOCK-REQUEST"


class _TraceContext(object):
    @property
    def trace_id(self) -> str:
        return _trace_id.get()
    
    @trace_id.setter
    def trace_id(self, value):
        _trace_id.set(value)
    
    @property
    def service_id(self) -> str:
        return _get_service_id()
    
    @staticmethod
    def generate_trace_id() -> str:
        return f"{_get_service_id()}-{uuid.uuid4().hex}"
    
    @property
    def mock_request(self):
        return _mock_request.get()
    
    @mock_request.setter
    def mock_request(self, value: str):
        _mock_request.set(value)
    
    @property
    def is_mock_request(self) -> bool:
        return self.mock_request.lower() == "true"
    
    @property
    def headers(self) -> dict:
        return {TRACE_ID: self.trace_id, MOCK_REQUEST: self.mock_request}


TraceContext = _TraceContext()


def _get_service_id() -> str:
    return os.environ.get("SERVICE_ID", "")
