import asyncio
import functools
import inspect
import json
import logging
import traceback
from asyncio import AbstractEventLoop, CancelledError
from concurrent.futures import Future
from threading import Thread

import httpx

from .config import openapi_config
from .schema import OperationLog


class operation_log:
    """
    当前操作日志装饰器，同时支持同步和异步协程

    用法：
    @operation_log(op_type='safety_check', is_cost_log=True, ucid_key="ucid")
    def safety_check(request, *, validate_output: bool):
        pass

    @operation_log(op_type='safety_check', is_cost_log=True, ucid_key="ucid")
    async def safety_check(request, *, validate_output: bool):
        pass
    """

    def __init__(self, *, op_type: str = None, is_cost_log=False, ucid_key="ucid"):
        """
        :param op_type: 表示当前操作动作, 如果不传入则默认使用被装饰的函数名
        :param is_cost_log: 表示当前日志是否是计费相关日志, 默认为False

        """
        self.op_type = op_type
        self.is_cost_log = is_cost_log
        self.ucid_key = ucid_key

    def __call__(self, func):
        if inspect.iscoroutinefunction(func):
            return operation_log.async_log_decorator(func, op_type=self.op_type, is_cost_log=self.is_cost_log, ucid_key=self.ucid_key)
        return operation_log.log_decorator(func, op_type=self.op_type, is_cost_log=self.is_cost_log, ucid_key=self.ucid_key)

    @staticmethod
    def log_decorator(func, *, op_type, is_cost_log, ucid_key):
        """
        日志装饰器，在函数调用前后记录日志
        :param func:
        :param op_type:
        :param is_cost_log:
        :return:
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal op_type
            op_type = op_type if op_type else func.__name__
            ucid_value = operation_log._get_ucid(ucid_key, func, args, kwargs)
            opt_in_log = OperationLog(opLogType='in', opType=op_type,
                                      operationStatus='success',
                                      request=[args, kwargs],
                                      response=None,
                                      isCostLog=is_cost_log,
                                      ucid=ucid_value,
                                      )

            submit_log(opt_in_log)

            opt_out_log = None
            try:
                resp = func(*args, **kwargs)
                opt_out_log = OperationLog(opLogType='out', opType=op_type,
                                           operationStatus='success',
                                           request=[args, kwargs],
                                           response=resp,
                                           isCostLog=is_cost_log,
                                           ucid=ucid_value,
                                           )
                return resp
            except Exception as e:
                opt_out_log = OperationLog(opLogType='out', opType=op_type,
                                           operationStatus='failed',
                                           request=[args, kwargs],
                                           response=None,
                                           errMsg=traceback.format_exc()[:1024],
                                           isCostLog=is_cost_log,
                                           ucid=ucid_value,
                                           )
                raise e
            finally:
                submit_log(opt_out_log)

        return wrapper

    @staticmethod
    def async_log_decorator(func, *, op_type, is_cost_log, ucid_key):
        """
        日志装饰器，在函数调用前后记录日志
        :param func:
        :param op_type:
        :param is_cost_log:
        :return:
        """

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal op_type
            op_type = op_type if op_type else func.__name__
            ucid_value = operation_log._get_ucid(ucid_key, func, args, kwargs)
            opt_in_log = OperationLog(opLogType='in', opType=op_type,
                                      operationStatus='success',
                                      request=[args, kwargs],
                                      response=None,
                                      isCostLog=is_cost_log,
                                      ucid=ucid_value,
                                      )

            submit_log(opt_in_log)

            opt_out_log = None
            try:
                resp = await func(*args, **kwargs)
                opt_out_log = OperationLog(opLogType='out', opType=op_type,
                                           operationStatus='success',
                                           request=[args, kwargs],
                                           response=resp,
                                           isCostLog=is_cost_log,
                                           ucid=ucid_value,
                                           )
                return resp
            except Exception as e:
                opt_out_log = OperationLog(opLogType='out', opType=op_type,
                                           operationStatus='failed',
                                           request=[args, kwargs],
                                           response=None,
                                           errMsg=traceback.format_exc()[:1024],
                                           isCostLog=is_cost_log,
                                           ucid=ucid_value,
                                           )
                raise e
            finally:
                submit_log(opt_out_log)

        return wrapper
    @staticmethod
    def _get_ucid(ucid_key, func, args, kwargs):
        # 尝试从关键字参数中获取 UCID
        ucid = kwargs.get(ucid_key)
        if ucid is None:
            # 如果 UCID 不在关键字参数中，尝试从位置参数中获取
            func_params = func.__code__.co_varnames
            if ucid_key in func_params:
                ucid_index = func_params.index(ucid_key)
                if ucid_index < len(args):
                    ucid = args[ucid_index]
        return ucid

def submit_log(log: OperationLog):
    try:
        task = asyncio.create_task(_async_log(log))
        task.add_done_callback(log_callback)
    except RuntimeError:
        _submit_log_in_thread_event_log(log)


# 监控任务日志执行结果
def log_callback(future: Future):
    try:
        future.result()
    except CancelledError:
        logging.exception(f'openapi log report task cancelled')
    except Exception:
        logging.exception(f'openapi log report task failed')


class ThreadedEventLoop(Thread):
    """
    如果当前线程没有event loop, 则使用独立线程中的async_log_event_loop
    """

    def __init__(self, loop: AbstractEventLoop):
        super().__init__()
        self.loop = loop
        self.daemon = True

    def run(self) -> None:
        self.loop.run_forever()


# 启动asyncio event loop， 如果用户当前线程没有event loop，则使用独立线程中的async_log_event_loop
async_log_event_loop = asyncio.new_event_loop()
asyncio_thread = ThreadedEventLoop(async_log_event_loop)
asyncio_thread.start()


def _submit_log_in_thread_event_log(log):
    future = asyncio.run_coroutine_threadsafe(
        _async_log(log), async_log_event_loop)
    future.add_done_callback(log_callback)


# 异步上报日志
async_httpx_client = None


async def _async_log(log: OperationLog):
    global async_httpx_client
    if async_httpx_client is None:
        async_httpx_client = await httpx.AsyncClient(limits=httpx.Limits(max_connections=50)).__aenter__()
    # 异步写入日志
    url = openapi_config.OPENAPI_HOST + "/v1/openapi/report/log"
    log_data = json.loads(json.dumps(log.dict(by_alias=True), default=lambda x: None))
    logging.info(f'openapi链路日志上报:{log_data}')
    response = await async_httpx_client.post(url, json=log_data)
    if response.status_code != 200:
        logging.warning(f'log failed, status_code: {response.status_code}, response: {response.text}')
    return response.status_code


__all__ = ['operation_log', 'OperationLog', 'submit_log']
