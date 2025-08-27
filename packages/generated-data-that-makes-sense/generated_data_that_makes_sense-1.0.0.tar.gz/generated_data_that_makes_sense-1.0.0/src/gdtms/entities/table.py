import time
import typing as t
from random import randint

from gdtms.data_types.reference import Reference
from gdtms.entities.field import Field
from gdtms.entities.record import Record
from gdtms.entities.unique_key import UniqueKey
from gdtms.exceptions.timout_exceeded import TimeoutExceeded
from gdtms.views.view import View

TIMEOUT = 10


class Table:
    def __init__(self, name: str, num_records_to_generate: int = 1) -> None:
        self.name: str = name
        self.num_records_to_generate: int = num_records_to_generate
        self.last_inserted_id: int = 0
        self.fields: t.List[Field] = []
        self.references: t.List[Reference] = []
        self.unique_keys: t.List[UniqueKey] = []
        self.records: t.List[Record] = []

    def set_schema(self, schema: "Schema"):
        self.schema: "Schema" = schema

    def add_field(self, field: Field) -> "Table":
        field.set_table(self)
        self.fields.append(field)
        return self

    def add_fields(self, fields: t.List[Field]) -> "Table":
        for field in fields:
            self.add_field(field)
        return self

    def add_unique_key(self, unique_key: UniqueKey) -> "Table":
        unique_key.set_table(self)
        self.unique_keys.append(unique_key)
        return self

    def get_fields(self):
        return self.fields

    def get_records(self):
        return self.records

    def get_last_inserted_id(self):
        return self.last_inserted_id

    def _generate(self, num: int):
        time_started = time.time()
        while self.last_inserted_id < num:
            if (time.time() - time_started) > TIMEOUT:
                raise TimeoutExceeded(
                    f"Number of records ({self.num_records_to_generate}) set to "
                    f"generate table '{self.name}' excced the limit the unique keys provide. "
                    "Either reduce the number of records to generate or relax the unique keys constraints."
                )
            record = Record(table=self)
            record.generate()
            if self.is_record_unique(record):
                self.records.append(record)
                self._increment()
                for unique_key in self.unique_keys:
                    unique_key.add_value(record)

    def dump(self, view: View) -> str:
        self._generate(self.num_records_to_generate)
        return view.dump_table(self)

    def get_schema(self) -> "Schema":
        return self.schema

    def _increment(self) -> None:
        self.last_inserted_id += 1

    def get_random_record_id(self) -> t.Optional[int]:
        if not self.last_inserted_id:
            return None
        return randint(1, self.last_inserted_id)

    def clean(self) -> None:
        self.records = []

    def is_record_unique(self, record: Record) -> bool:
        for unique_key in self.unique_keys:
            is_duplicate = unique_key.is_duplicate(record)
            if is_duplicate:
                return False
        return True

    def _add_value_to_unique_keys(self, record: Record):
        for unique_key in self.unique_keys:
            unique_key.add_value(record)
