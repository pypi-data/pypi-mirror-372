from .log import operation_log
from .authorize import validate_token, check_configuration, account_balance_enough
from .openapi_contexvar import trace_id_context, caller_id_context, request_url_context
from pydantic import BaseModel
import uuid
from fastapi import Request
import logging
# 创建一个日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # 设置日志级别为INFO

# 创建一个控制台处理器，并设置其级别和格式
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(console_handler)

class ErrorInfo(BaseModel):
    task_id: str = ""
    result: str = ""
    status: int = 40000001
    message: str = ""

def async_authenticate_decorator_args(end_point):
    def async_authenticate_decorator(func):
        async def wrapper(*args, **kwargs):
            request_arg = None
            for arg in args:
                if type(arg) == Request:
                    request_arg = arg
                    break
            if request_arg is not None:
                task_id = str(uuid.uuid4())
                supported, error_json, caller_id = authenticate_user(request_arg.headers.get("Authorization"), task_id)
                if not supported:
                    return error_json
                t_token, c_token, r_token = set_context(task_id, caller_id, end_point)
                result = await func(*args, **kwargs)
                clean_context(t_token, c_token, r_token)
                return result
            else:
                logger.warn("please check your request param,have not a param's type is Request of fastapi!")
            return func(*args, **kwargs)
        return wrapper
    return async_authenticate_decorator


def authenticate_user(token, task_id):
    if check_configuration():
        if token is None:
            return False, ErrorInfo(task_id=task_id, result="", status=40000001, message="token is missing").dict(), ""
        try:
            caller_id = validate_token(token)
            balance = account_balance_enough(token, cost=1.0)

        except Exception as e:
            return False, ErrorInfo(task_id=task_id, result="", status=40000001, message=str(e)[:100]).dict(), ""
        return balance, ErrorInfo(task_id=task_id, result="", status=40000001, message="Insufficient balance").dict(), caller_id
    else:
        return True, "", ""


@operation_log(op_type='upload_cost_log', is_cost_log=True, ucid_key="ucid")
def upload_cost_log(result_obejct, ucid):
    response = result_obejct.dict()
    return response

def print_context(log):
    logger.info(f"{log} trace_id:{trace_id_context.get()}, caller_id:{caller_id_context.get()}, end_point:{request_url_context.get()}")

def get_context():
    return trace_id_context.get(), caller_id_context.get(), request_url_context.get()

def set_context(trace_id, caller_id, end_point):
    t_token = trace_id_context.set(trace_id)
    c_token = caller_id_context.set(caller_id)
    r_token = request_url_context.set(end_point)
    return t_token, c_token, r_token

def clean_context(t_token, c_token, r_token):
    trace_id_context.reset(t_token)
    caller_id_context.reset(c_token)
    request_url_context.reset(r_token)

def report(result_obejct, ucid = ""):
    if not check_configuration():
        return
    upload_cost_log(result_obejct, ucid)
