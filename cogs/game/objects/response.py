from dataclasses import dataclass
from datetime import datetime

@dataclass
class Response(object):
    success: bool
    message: str = None
    data: dict = None
    date: datetime = datetime.now()
