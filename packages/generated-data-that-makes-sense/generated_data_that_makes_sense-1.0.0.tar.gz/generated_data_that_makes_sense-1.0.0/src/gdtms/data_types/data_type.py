class DataType:
    def set_field(self, field: "Field"):
        self._field = field

    @property
    def value(self):
        raise NotADirectoryError()
