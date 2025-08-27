import typing as t
from random import choice

from gdtms.data_types.data_type import DataType


class ListItem(DataType):
    def __init__(self, items: t.List[t.Any]) -> None:
        self.items = items

    @property
    def value(self):
        return choice(self.items)
