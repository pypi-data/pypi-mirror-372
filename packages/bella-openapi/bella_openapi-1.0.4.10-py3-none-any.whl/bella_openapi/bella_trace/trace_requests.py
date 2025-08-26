# -*- coding: utf-8 -*-
# ======================
# Date    : 2024/12/30
# Author  : Liu Yuchen
# Content : 
# 
# ======================
from requests import sessions
from requests.adapters import HTTPAdapter

from ._context import TraceContext


__all__ = ["BellaTraceAdapter"]


class BellaTraceAdapter(HTTPAdapter):
    
    def send(self, request, **kwargs):
        request.headers.update(TraceContext.headers)
        return super().send(request, **kwargs)


def request(method, url, **kwargs):
    with sessions.Session() as session:
        session.mount("http://", BellaTraceAdapter())
        session.mount("https://", BellaTraceAdapter())
        return session.request(method=method, url=url, **kwargs)


def get(url, params=None, **kwargs):
    return request("get", url, params=params, **kwargs)


def options(url, **kwargs):
    return request("options", url, **kwargs)


def head(url, **kwargs):
    kwargs.setdefault("allow_redirects", False)
    return request("head", url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    return request("post", url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    return request("put", url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    return request("patch", url, data=data, **kwargs)


def delete(url, **kwargs):
    return request("delete", url, **kwargs)

