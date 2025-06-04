from MIWOS.migration import Migration


class CreateChannel(Migration):
    def migrate(self):
        with self.create_tables("channels") as x:
            x.primary_key("id", auto_increment=True)
            x.string("name", unique=True, null=False)
            x.datetime("created_at", default="CURRENT_TIMESTAMP")
            x.datetime("updated_at", default="CURRENT_TIMESTAMP",
                       on_update="CURRENT_TIMESTAMP")

        self.create_join_table("channels", "users")

    def rollback(self):
        self.drop_join_table("channels", "users")
        self.drop_tables("channels")
