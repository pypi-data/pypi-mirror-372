from typing import Optional, Dict, Any, Mapping

import httpx

from bella_openapi.config import openapi_config


def get_model_list(
        token: str = openapi_config.OPENAPI_CONSOLE_KEY,
        extra_headers: Optional[Mapping[str, str]] = None,
        extra_query: Optional[Mapping[str, object]] = None,
) -> Dict[str, Any]:
    """
    获取模型列表

    Args:
        token (str): 访问令牌
        extra_headers: 额外的请求头
        extra_query: 额外的查询参数，可以包含status、features等

    Returns:
        Dict[str, Any]: API响应的JSON数据

    Examples:
        >>> get_model_list(token='****',extra_query={"status": "active", "features": "vision"})
    """
    url = openapi_config.OPENAPI_HOST + '/console/model/list'
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
    }
    # 添加额外的请求头
    if extra_headers:
        headers.update(extra_headers)
    # 构建查询参数
    params = {}
    # 添加额外的查询参数
    if extra_query:
        params.update(extra_query)
    # 发送请求
    response = httpx.get(url, headers=headers, params=params)
    # 检查响应状态
    response.raise_for_status()
    # 返回JSON数据
    return response.json()