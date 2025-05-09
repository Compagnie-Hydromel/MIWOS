from MIWOS.migration import Migration


class SecondSampleData(Migration):
    def migrate(self):
        def sample_table_column(x):
            x.int("id", primary_key=True, auto_increment=True)
            x.string("name", unique=True)
            x.boolean("is_human", null=False)
            x.float("height")
            x.int("age", default=0)
            x.boolean("is_alive")
            x.date("birth_date")
            x.datetime("created_at")
            x.datetime("updated_at")

        self.create_tables("humans", sample_table_column)

    def rollback(self):
        self.drop_tables("humans")
