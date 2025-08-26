from datetime import datetime
from typing import Optional

import uuid

import pydantic
from pydantic import BaseModel, Field
from .openapi_contexvar import trace_id_context, caller_id_context, request_url_context


class BaseOperationLog(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: Optional[str] = Field(default_factory=lambda: trace_id_context.get(),
                                      alias='requestId')
    caller_id: Optional[str] = Field(default_factory=lambda: caller_id_context.get(),
                                     alias='callerId')
    request_url: Optional[str] = Field(default_factory=lambda: request_url_context.get(),
                                       alias='requestUrl')
    op_log_type: str = Field(alias='opLogType')
    op_type: str = Field(alias='opType')
    is_cost_log: bool = Field(default=False, alias='isCostLog')
    operation_status: str = Field(alias='operationStatus')
    start_time_millis: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000),
                                   alias='startTimeMillis')
    duration_millis: int = Field(default=0, alias='durationMillis')
    request: object
    response: object = Field(default=None)
    err_msg: Optional[str] = Field(default=None, alias='errMsg')
    extra_info: dict = Field(default={}, alias='extraInfo')
    ucid: str = Field(default='ucid')

    @staticmethod
    def validate(values):
        if 'request_id' not in values or values['request_id'] is None:
            raise ValueError('request_id is required, please set trace_id_context')
        if 'caller_id' not in values or values['caller_id'] is None:
            raise ValueError('caller_id is required, please set caller_id_context')
        if 'request_url' not in values or values['request_url'] is None:
            raise ValueError('request_url is required, please set request_url_context')
        return values


if pydantic.version.VERSION.startswith('1.'):
    from pydantic import root_validator


    class OperationLog(BaseOperationLog):
        @root_validator
        def validate_duration_millis(cls, values):
            super().validate(values)
            return values


else:
    from pydantic import model_validator


    class OperationLog(BaseOperationLog):

        @model_validator(mode='after')
        def validate_duration_millis(cls, values):
            super().validate(values.dict())
            return values
