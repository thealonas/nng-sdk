import datetime

from pydantic import BaseModel


class Startup(BaseModel):
    service_name: str
    time_log: datetime.datetime
