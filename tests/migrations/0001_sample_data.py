from MIWOS.migration import Migration


class SampleData(Migration):
    def migrate(self):
        def sample_table_column(x):
            x.int("id", primary_key=True, auto_increment=True)
            x.string("name")
            x.int("year")

        self.create_tables("cars", sample_table_column)

    def rollback(self):
        self.drop_tables("cars")
