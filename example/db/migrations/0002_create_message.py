from MIWOS.migration import Migration


class CreateMessage(Migration):
    def migrate(self):
        with self.create_tables("messages") as x:
            x.primary_key("id", auto_increment=True)
            x.string("content", null=False)
            x.references("user", on_delete="CASCADE")
            x.datetime("created_at", default="CURRENT_TIMESTAMP")
            x.datetime("updated_at", default="CURRENT_TIMESTAMP",
                       on_update="CURRENT_TIMESTAMP")

    def rollback(self):
        self.drop_tables("messages")
