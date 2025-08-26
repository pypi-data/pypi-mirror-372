import uuid

import werkzeug
from werkzeug.routing import Map, Rule
from starlette.datastructures import URL
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from bella_openapi import caller_id_context, request_url_context, trace_id_context
from bella_openapi import validate_token
from bella_openapi.exception import AuthorizationException
from urllib.parse import parse_qs


class WebSocketHttpContextMiddleware:
    def __init__(self, app, *, exclude_url: list[str] = None):
        self.app = app
        self.exclude_url = exclude_url or []

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            return await self.app(scope, receive, send)

        url = URL(scope=scope)
        if match_url(self.exclude_url, url.path):
            return await self.app(scope, receive, send)

        query_params = parse_qs(url.query)
        if not (query_params.get('token')) or query_params.get('token') == '':
            # send  token required error
            await send({
                "type": "websocket.close",
                "code": 1006,
                "reason": "token required",
            })
            return
        try:
            token = query_params.get('token')
            caller = validate_token(token[0])
        except AuthorizationException:
            await send({
                "type": "websocket.close",
                "code": 1006,
                "reason": "token invalid",
            })
            return
        else:
            caller_context_token = caller_id_context.set(caller)
            trace_id_context_token = trace_id_context.set(str(uuid.uuid4()))
            request_url_context_token = request_url_context.set(url.path)
            await self.app(scope, receive, send)
            caller_id_context.reset(caller_context_token)
            trace_id_context.reset(trace_id_context_token)
            request_url_context.reset(request_url_context_token)


def match_url(patterns, url):
    if patterns is None:
        return False
    # 创建 URL 规则
    rules = [Rule(pattern) for pattern in patterns]
    # 匹配 URL
    adapter = Map(rules).bind('')
    try:
        adapter.match(url)
        return True
    except werkzeug.exceptions.NotFound:
        return False


class HttpContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, exclude_url: list[str] = None, ):
        """
        :param app
        :param exclude_url: 不需要验证token的url,
        根据https://werkzeug.palletsprojects.com/en/2.2.x/routing/  规则进行配置
        """
        super().__init__(app)
        self.exclude_url = exclude_url

    async def dispatch(self, request, call_next):
        if match_url(self.exclude_url, request.url.path):
            return await call_next(request)

        if request.url.path.startswith("/v1/actuator/health"):
            return await call_next(request)
        authorization = request.headers.get("Authorization")
        if authorization is None:
            return JSONResponse(status_code=401, content={"message": "empty Authorization header"})

        try:
            caller = validate_token(authorization)
        except AuthorizationException as e:
            return JSONResponse(status_code=401, content={"message": e.message})

        caller_context_token = caller_id_context.set(caller)
        trace_id_context_token = trace_id_context.set(str(uuid.uuid4()))
        request_url_context_token = request_url_context.set(request.url.path)

        # 继续处理请求
        response = await call_next(request)

        # 重置contextvars上下文
        caller_id_context.reset(caller_context_token)
        trace_id_context.reset(trace_id_context_token)
        request_url_context.reset(request_url_context_token)

        return response
