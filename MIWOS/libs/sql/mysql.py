from MIWOS.libs.sql.select import executor_select
from MIWOS.libs.sql.querygenerator.mysql import MySQLQueryGenerator


class MysqlQuery(MySQLQueryGenerator):
    def __init__(self, table_name):
        super().__init__(table_name=table_name)
        self._query = executor_select()
        self.initialized = True

    def execute(self):
        result = self._query.execute(self.query)
        self.reset_query()
        return result

    def commit(self):
        result = self._query.commit(self.query)
        self.reset_query()
        return result
