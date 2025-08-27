from random import choice

from gdtms.data_types.adjective import Adjective
from gdtms.data_types.data_type import DataType
from gdtms.data_types.noun import Noun
from gdtms.data_types.number import Number


class Address(DataType):
    @property
    def value(self):
        streen_number = Number(10_000).value
        street_suffix = choice(["Str.", "Ave.", "Dr.", "Cres.", "Pkw."])
        noun = Noun().value.capitalize()
        adjective = Adjective().value.capitalize()
        addresses = [
            f"{streen_number} {noun} {street_suffix}",
            f"{streen_number} {adjective} {noun} {street_suffix}",
        ]
        return choice(addresses)
