from MIWOS.libs.sql.select import executor_select
from MIWOS.libs.sql.querygenerator.mariadb import MariaDBQueryGenerator


class MariaDBQuery(MariaDBQueryGenerator):
    def __init__(self, table_name):
        super().__init__(table_name=table_name)
        self._query = executor_select()
        self.initialized = True

    def execute(self, many=False):
        result = self._query.execute(
            self.query, parameters=self.arguments, many=many)
        self.reset_query()
        return result

    def commit(self, many=False):
        result = self._query.commit(
            self.query, parameters=self.arguments, many=many)
        self.reset_query()
        return result
