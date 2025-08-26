OpenAPI网关服务客户端
=======================

## 功能列表

1. 校验token，获取用户信息
2. 统一上报操作日志至网关侧

## 使用指南

### 安装

```shell
pip install bella-openapi
```

### 配置网关域名

通过环境变量设置网关域名

```python
OPENAPI_HOST = "https://***.com"
# 需要调用console类接口获得元信息时候会默认取全局的此key，使用者也可根据场景选择不使用默认的KEY，更细粒度的传递指定key
OPENAPI_CONSOLE_KEY = "************"  
```

### 配置校验

```python
from bella_openapi import check_configuration
# 该函数判断是否所有配置ok，只有所有配置ok的情况下，才能调用鉴权计费等接口
config_is_ok = check_configuration()
```
### token校验

```python
from bella_openapi import validate_token, support_model, account_balance_enough

token = "****"
# 根据token，解析用户身份
user_name = validate_token(token)
# 查询当前登陆用户，是否具有指定模型的权限
supported = support_model(token, 'model_name')
# 账户余额判断，支持传入指定判断阈值，服务方可以在每次用户请求前，根据本次预估花费，对用户余额进行校验，若余额不足，则可拒绝请求

balance = account_balance_enough(token, cost=1.0)
```

如果token无效，抛出`AuthorizationException`异常

### 上报操作日志

为了追踪用户调用中间处理流程，建议在必要处理操作处，进行操作日志记录上报。操作日志记录分别在操作入口处
（操作前）和操作出口处（操作后）进行记录上报。

#### 1. 上报模式

为降低上报操作日志延迟对业务逻辑的影响，上报操作日志采用异步上报模式

##### async异步上报

日志上报，将采用异步io的方式，上报操作日志，这种方式，可以在单线程中，同时处理多个并发非阻塞IO操作

```python
from bella_openapi import operation_log


@operation_log()
def safety_check(request, *, validate_output: bool):
    pass
```

#### 2. 上报参数更新

操作日志记录，需要传递一些动态参数，需导入预定义的contextvar，在请求起始处进行设置, 请求结束时清空contextvar

```python
from bella_openapi import trace_id_context, caller_id_context, request_url_context

# 整个链路处理前，设置
t_token = trace_id_context.set("*********")  # trace_id 当前请求链路唯一标识
c_token = caller_id_context.set("*********")  # caller_id 调用方标识, 通过user_info.username获取
r_token = request_url_context.set("*********")  # request_url 当前请求url
# #
# 请求处理
# 清空contextvar
trace_id_context.reset(t_token)
caller_id_context.reset(c_token)
request_url_context.reset(r_token)
```

##### 2.1 使用middleware设置contextvar, 将自动进行token解析，以及上下文设置

如果当前url不需要进行拦截，可以配置exclude_path进行过滤

```python
from bella_openapi.middleware import HttpContextMiddleware, WebSocketHttpContextMiddleware
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(HttpContextMiddleware, exclude_path=["/v1/actuator/health/<pattern>"])
```

##### 2.2 跨线程上下文复制

由于上下文变量是线程隔离的，因此如果需要在独立于设置上下文变量的其他线程中，进行日志记录操作，需要将上下文变量复制到新的线程中

```python
# 使用contextvars.copy_context(), 复制上下文，并在复制上下文中，执行方法
import contextvars
from functools import partial
from threading import Thread


class ThreadCopyContext(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        context = contextvars.copy_context()
        super().__init__(group, context.run, name,
                         [partial(target, *args, **kwargs if kwargs else {})],
                         None, daemon=daemon)


request_url_context = contextvars.ContextVar('request_url', default='empty')
r_token = request_url_context.set('http://localhost:8000')


def run():
    print(request_url_context.get())


# 未复制contextvar，新的线程中，上下文变量为默认值空
t = Thread(target=run)
t.start()
t.join()
# > empty
# 复制contextvar，可以获取到复制的上下文变量
t = ThreadCopyContext(target=run)
t.start()
t.join()
# > http://localhost:8000
```

#### 3. 日志记录配置

日志记录中，op_type字段默认取值为当前方法名称，可通过在装饰器中传入参数进行覆盖。该装饰器可同时用于同步方法以及异步协程的日志上报
为了进行调用计费，如果当前操作日志中的信息，需要用于回调计费，则需要在装饰器中传入is_cost_log=True

```python
from bella_openapi import operation_log


@operation_log(op_type='safety_check', is_cost_log=False, ucid="ucid")
def safety_check(request, *, validate_output: bool):
    pass


@operation_log(is_cost_log=False, ucid="ucid")
async def safety_check(request, *, validate_output: bool):
    pass
```

#### 4. 直接上报链路日志
##### 4.1 调用submit_log方法

```python
from bella_openapi import submit_log
# construct log
log = ...
submit_log(log)
```
##### 4.2 http上报

如果在特定场景下，通过装饰器进行链路日志上报不够灵活，您可直接通过调用对应的http 接口上传链路日志
POST接口url：/v1/openapi/report/log

接口参数：

##### Params

| Name            | Type    | Required | Title   | Description                              |
|-----------------|---------|----------|---------|------------------------------------------|
| uuid            | string  | yes      | 日志uuid  | 每条日志，使用不同uuid标识                          |
| requestId       | string  | yes      | 链路id    | 一次用户请求中，后台多条处理日志，应该使用同一requestId进行串联     |
| callerId        | string  | yes      | 调用房标识   | 调用token解析得到的当前调用方标识                      |
| requestUrl      | string  | yes      | 能力端点    | 用户请求，接口url地址                             |
| opLogType       | string  | yes      | 操作日志类型  | 如果日志在操作入口记录，则改                           |
| opType          | string  | yes      | 操作类型    | 日志记录对应的操作名称                              |
| isCostLog       | boolean | yes      | 是否计费日志  | 如果为true，且opLogType为out，该条日志将被用户计算用户调用的费用 |
| operationStatus | string  | yes      | 操作状态    | none                                     |
| startTimeMillis | integer | yes      | 操作起始时间戳 | none                                     |
| durationMillis  | integer | yes      | 操作结束时间戳 | none                                     |
| request         | object  | yes      | 操作入参    | none                                     |
| response        | object  | no       | 操作出参    | none                                     |
| errMsg          | string  | no       | 异常信息    | 如果操作失败，记录失败信息                            |
| extraInfo       | object  | no       |         | 其他透传信息                                   |

##### Enum

| Name            | Value   | Description  |
|-----------------|---------|--------------|
| opLogType       | in      | 日志记录为操作入口处记录 |
| opLogType       | out     | 日志记录为操作出口处记录 |
| operationStatus | success | 当前操作成功       |
| operationStatus | failed  | 当前操作失败       |
#### 5. 链路日志查询
get接口地址：/v1/openapi/log/{requestId}
传入链路id，可查询当前链路下的所有日志信息

### Trace SDK
使用方法见：[Trace README](src/bella_openapi/bella_trace/README.md)

## release log

* 0.0.1.2
    * 修复pydantic 2.x版本，BaseModel校验问题
* 0.0.1.3
    * 修复account_balance_enough调用异常
    * 操作日志中，时间戳记录单位改为毫秒
    * README文档，增加日志记录contextvar跨线程复制说明, 操作日志上报http接口介绍
* 0.0.1.4
    * 修复log日志记录中，对象无法序列化问题
* 0.0.1.5
    * 暴露submit_log，支持直接上报日志
* 0.0.1.8
    * 支持不配置openapi_host的情况下，鉴权计费可以正常调通  
* 0.0.1.16
    * 提供配置检测接口 
* 0.0.1.25
    * 新增 Bella Trace 链路日志
* 0.0.1.26
    - 新增 console 模块，实现元数据获取
* 1.0.0
    - 项目发到python中央仓库，请不要使用此版本，pipy仓库已删除
* 1.0.1
    * rename 包名
* 1.0.2
    * 修复bug
* 1.0.3 
    * 新增standard domtree
* 1.0.4
    * 新增validate_token_by_whoami