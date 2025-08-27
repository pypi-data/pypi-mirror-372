from gdtms.data_types.data_type import DataType
from gdtms.sources.sources import phone_numbers


class PhoneNumber(DataType):
    @property
    def value(self):
        return next(phone_numbers())
