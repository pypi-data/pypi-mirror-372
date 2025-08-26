# -*- coding: utf-8 -*-
# ======================
# Date    : 2024/12/30
# Author  : Liu Yuchen
# Content : 
# 
# ======================
import functools
import json
import logging
import time
import traceback

from ._context import TraceContext

__all__ = ["trace", "BellaTraceHandler"]


def trace(logger=logging):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            data = {
                "trace_info": {
                    "bellaTraceId": TraceContext.trace_id,
                    "serviceId": TraceContext.service_id,
                    "start": time.time()
                },
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            try:
                result = func(*args, **kwargs)
                data["result"] = result
                data["trace_info"]["end"] = time.time()
                logger.info(json.dumps(data, ensure_ascii=False))
                return result
            except Exception as e:
                try:
                    data["error_msg"] = traceback.format_exception(e)
                    logger.error(json.dumps(data, ensure_ascii=False))
                except Exception as i_e:
                    logger.error(traceback.format_exception(i_e))
                raise e
        return wrapper
    return decorator


class BellaTraceHandler(logging.Handler):
    
    def __init__(self, fmt: str = "{name}={value}"):
        super().__init__()
        self.format = fmt
    
    def emit(self, record):
        if trace_id := TraceContext.trace_id:
            record.msg = f"{self.format.format(name='trace_id', value=trace_id)} {record.msg}"
