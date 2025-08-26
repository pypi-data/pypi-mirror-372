import httpx
import logging
from .config import openapi_config
from .exception import AuthorizationException


def check_configuration() -> bool:
    res = openapi_config.OPENAPI_HOST is not None
    return res


def validate_token(token: str) -> str:
    """
    根据传入token， 解析用户身份
    :param token:
    :return: 用户身份，返回账户id
    :raises: AuthorizationException 如果token无效， 抛出异常
    """
    return _validate_token_request(token)


def support_model(token: str, model: str) -> bool:
    """
    根据传入token，判断用户是否有对应的模型权限
    :param token: 用户token
    :param model: 模型名
    :return: bool
    """
    url = openapi_config.OPENAPI_HOST + "/v1/openapi/support/model"
    # 使用httpx发送get请求
    response = httpx.get(url, headers={"Authorization": token}, params={"model": model})
    if response.status_code == 200:
        return response.json()['data']
    else:
        raise AuthorizationException(response.text, response.status_code)


def account_balance_enough(token: str, cost: float = 0) -> bool:
    """
    账户余额判断，支持传入指定判断阈值，服务方可以在每次用户请求前，根据本次预估花费，对用户余额进行校验，若余额不足，则可拒绝请求
    :param token: 用户token
    :param cost: 消耗金额, 单位：元/RMB
    :return: bool
    """
    url = openapi_config.OPENAPI_HOST + "/v1/openapi/check/account/balance"
    # 使用httpx发送get请求
    response = httpx.get(url, headers={"Authorization": token}, params={"cost": cost})
    if response.status_code == 200:
        return response.json()['data']
    else:
        raise AuthorizationException(response.text, response.status_code)


def _validate_token_request(token: str) -> str:
    url = openapi_config.OPENAPI_HOST + "/v1/openapi/validate/tokens"
    # 使用httpx发送get请求
    response = httpx.get(url, headers={"Authorization": token})
    if response.status_code == 200:
        return response.json()['data']
    else:
        raise AuthorizationException(response.text, response.status_code)

def validate_token_by_whoami(token: str) -> bool:
    """
    根据传入token， 判断用户身份是否真的存在
    :param token:
    :return: bool, 如果用户身份存在，返回True，否则返回False
    """
    url = openapi_config.OPENAPI_HOST + "/v1/apikey/whoami"
    # 使用httpx发送get请求
    response = httpx.get(url, headers={"Authorization": token})
    if response.status_code == 200:
        return response.json()['code'] == 200
    return False
