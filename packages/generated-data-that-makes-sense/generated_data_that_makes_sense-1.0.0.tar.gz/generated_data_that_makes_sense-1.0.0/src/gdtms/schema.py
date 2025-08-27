from gdtms.data_types.address import Address
from gdtms.data_types.adjective import Adjective
from gdtms.data_types.autoincrement import Autoincrement
from gdtms.data_types.city import City
from gdtms.data_types.composite import Composite
from gdtms.data_types.date import Date
from gdtms.data_types.domain_name import DomainName
from gdtms.data_types.email import Email
from gdtms.data_types.first_name import FirstName
from gdtms.data_types.hardcoded_value import HadrcodedValue
from gdtms.data_types.last_name import LastName
from gdtms.data_types.noun import Noun
from gdtms.data_types.number import Number
from gdtms.data_types.phone_number import PhoneNumber
from gdtms.data_types.reference import Reference
from gdtms.data_types.url import Url
from gdtms.data_types.zip_postal import ZipPostal
from gdtms.entities.field import Field
from gdtms.entities.schema import Schema
from gdtms.entities.table import Table
from gdtms.entities.unique_key import UniqueKey
from gdtms.views.mysql import Mysql


def get_schema() -> Schema:
    # # Table and deps:
    country_table = Table(name="countries", num_records_to_generate=2)
    # this is going to be at the edge of exhausting all possible unuque permutations:
    unique_field_1 = Field("bool1", Number(min_number=1, max_number=1))
    unique_field_2 = Field("bool2", Number(min_number=1, max_number=2))

    department_table = Table(name="departments", num_records_to_generate=2)

    applicant_table = Table(name="applicants", num_records_to_generate=10)

    link_table = Table(name="country_applicant_link", num_records_to_generate=4)

    parent_child_table = Table(name="tree", num_records_to_generate=10)

    # Fields
    country_table.add_fields(
        [
            Field("id", Autoincrement()),
            unique_field_1,
            unique_field_2,
            Field("cmpst", Composite([Adjective(), Noun()]), size=1),
            Field("cmpst", Composite([Adjective(), Noun()]), size=1),
            Field("cmpst_lmtd", Composite([Adjective(), Noun()]), size=9),
        ]
    )
    country_table.add_unique_key(UniqueKey([unique_field_1, unique_field_2]))

    department_table.add_fields(
        [
            Field("id", Autoincrement()),
            Field("country_id", Reference(country_table)),
            Field("department_id", Reference(department_table)),
            Field("adj", Adjective()),
            Field("name", Noun()),
            Field("country_id", Reference(country_table)),
            Field("phone", PhoneNumber()),
        ]
    )

    applicant_table.add_fields(
        [
            Field("id", Autoincrement()),
            Field("country_id", Reference(country_table)),
            Field("department_id", Reference(department_table)),
            Field("first_name", FirstName()),
            Field("last_name", LastName()),
        ]
    )

    field_country_id = Field("country_id", Reference(country_table))
    field_department_id = Field("department_id", Reference(department_table))
    link_table.add_fields([field_country_id, field_department_id])
    link_table.add_unique_key(UniqueKey([field_country_id, field_department_id]))

    parent_child_table.add_fields(
        [
            Field("id", Autoincrement()),
            Field("parent_id", Reference(parent_child_table), chance_of_null=50),
            Field("name", Noun()),
            Field("domain", DomainName()),
            Field("url", Url()),
            Field("email", Email()),
            Field("address", Address()),
            Field("zip_postal", ZipPostal()),
            Field("harcoded_value", HadrcodedValue("some-value")),
            Field("city", City()),
            Field("date", Date()),
        ]
    )

    schema = Schema()
    schema.add_tables(
        [
            country_table,
            department_table,
            applicant_table,
            link_table,
            parent_child_table,
        ]
    )
    return schema


def dump() -> str:
    schema = get_schema()
    view = Mysql()
    schema_dump = schema.dump(view)
    return schema_dump


if __name__ == "__main__":
    schema_dump = dump()
    print(schema_dump)
