from typing import Optional

from pydantic import BaseModel, field_validator


class LoggerType:
    INFO = "info"
    WARN = "warning"
    ERROR = "error"

    @classmethod
    def fetch_values(cls):
        return [
            value
            for name, value in vars(cls).items()
            if not name.startswith('_') and not callable(value) and name != 'fetch_values'
        ]

class BrowserLoggerRegisterParam(BaseModel):
    type:  str
    task_id: str
    window_id: str
    record: str
    error_reason: Optional[str] = None
    image_bytes: Optional[bytes] = None


    @field_validator("type", mode="before")
    def validate_type(cls, v):
        if v not in LoggerType.fetch_values():
            raise ValueError("Invalid type")
        return v
