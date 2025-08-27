from random import randint
from datetime import datetime

from gdtms.data_types.data_type import DataType


class Timestamp(DataType):
    def __init__(self, format: str, max_date: datetime, min_date: datetime = datetime(1970, 1, 1)) -> None:
        self.format = format
        self.max_date = max_date
        self.min_date = min_date

    @property
    def value(self):
        min_date = int(self.min_date.timestamp())
        max_date = int(self.max_date.timestamp())
        if max_date < min_date:
            min_date = max_date
        random_timestamp = randint(min_date, max_date)
        new_date = datetime.fromtimestamp(random_timestamp) 
        return new_date.strftime(self.format)
