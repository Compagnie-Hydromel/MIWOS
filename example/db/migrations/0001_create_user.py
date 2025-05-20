from MIWOS.migration import Migration


class CreateUser(Migration):
    def migrate(self):
        with self.create_tables("users") as x:
            x.primary_key("id", auto_increment=True)
            x.string("username", unique=True)
            x.string("password", null=False)
            x.string("email", null=False)
            x.string("firstname", null=False)
            x.string("lastname", null=False)
            x.datetime("created_at", default="CURRENT_TIMESTAMP")
            x.datetime("updated_at", default="CURRENT_TIMESTAMP",
                       on_update="CURRENT_TIMESTAMP")

    def rollback(self):
        self.drop_tables("users")
