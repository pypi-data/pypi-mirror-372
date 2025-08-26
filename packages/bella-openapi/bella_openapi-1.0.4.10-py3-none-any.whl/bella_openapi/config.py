from typing import Optional
import pydantic

if pydantic.version.VERSION.startswith('1.'):
    from pydantic import BaseSettings
else:
    from pydantic.v1 import BaseSettings


class OpenAPIConfig(BaseSettings):
    OPENAPI_HOST: Optional[str]
    OPENAPI_CONSOLE_KEY: Optional[str]


openapi_config = OpenAPIConfig()
