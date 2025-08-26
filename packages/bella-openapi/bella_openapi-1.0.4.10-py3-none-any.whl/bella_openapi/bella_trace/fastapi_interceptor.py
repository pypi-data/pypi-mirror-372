# -*- coding: utf-8 -*-
# ======================
# Date    : 2024/12/30
# Author  : Liu Yuchen
# Content : 
# 
# ======================
from starlette.middleware.base import BaseHTTPMiddleware

from ._context import TraceContext, TRACE_ID, MOCK_REQUEST

__all__ = ["FastapiBellaTraceMiddleware"]


class FastapiBellaTraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 设置 trace_id
        if trace_id_h := request.headers.get(TRACE_ID):
            TraceContext.trace_id = trace_id_h
        else:
            TraceContext.trace_id = TraceContext.generate_trace_id()
        
        if mock_request_h := request.headers.get(MOCK_REQUEST):
            TraceContext.mock_request = mock_request_h
        
        # 继续处理请求
        return await call_next(request)

