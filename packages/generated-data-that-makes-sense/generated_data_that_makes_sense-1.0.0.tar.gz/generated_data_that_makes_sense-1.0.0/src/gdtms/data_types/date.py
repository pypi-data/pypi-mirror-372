import time
from datetime import datetime
from random import randint

from gdtms.data_types.data_type import DataType


class Date(DataType):
    @property
    def value(self):
        min_timestamp = int(datetime(1970, 1, 1, 0, 0).timestamp())
        max_timestamp = int(time.time())
        random_timestamp = randint(min_timestamp, max_timestamp)
        dt = datetime.fromtimestamp(random_timestamp)
        return f"{dt.year}-{dt.month:02}-{dt.day:02}"
