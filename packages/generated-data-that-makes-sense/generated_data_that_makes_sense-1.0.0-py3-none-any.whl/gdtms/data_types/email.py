from random import choice, randint

from gdtms.data_types.adjective import Adjective
from gdtms.data_types.data_type import DataType
from gdtms.data_types.domain_name import DomainName
from gdtms.data_types.first_name import FirstName
from gdtms.data_types.last_name import LastName
from gdtms.data_types.noun import Noun


class Email(DataType):
    @property
    def value(self):
        return self._generate_email()

    def _generate_email(self):
        first_name = FirstName().value
        last_name = LastName().value
        domain_name = DomainName().value
        adjective = Adjective().value
        noun = Noun().value
        formats = [
            f"{first_name}.{last_name}@{domain_name}",
            f"{first_name.lower()[0:1]}.{last_name.lower()}@{domain_name}",
            f"{first_name.lower()[0:1]}_{last_name.lower()}_{randint(0, 2000)}@{domain_name}",
            f"{last_name.lower()}@{domain_name}",
            f"{adjective}_{noun}@{domain_name}",
            f"{adjective.capitalize()}_{first_name}@{domain_name}",
        ]
        return choice(formats)
