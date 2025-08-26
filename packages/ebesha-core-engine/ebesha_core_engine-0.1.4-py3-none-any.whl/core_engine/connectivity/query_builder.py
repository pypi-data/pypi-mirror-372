# Author : Puji Anugrah Pangestu #
# Created : 31 July 2025 #

class QueryBuilder:
    def __init__(self):
        self._select = []
        self._from = None
        self._joins = []
        self._where = []
        self._group_by = []
        self._order_by = None
        self._limit = None
        self._offset = None

    def select(self, *fields):
        self._select.extend(fields)
        return self

    def from_table(self, table_schema, table_name):
        self._from = f"{table_schema}.\"{table_name}\" {table_name}"
        return self

    def join(self, condition):
        join_stmt = f"{condition}"
        self._joins.append(join_stmt)
        return self

    def where(self, condition):
        self._where.append(condition)
        return self

    def group_by(self, fields):
        if fields:
            self._group_by.append(fields)
        return self

    def order_by(self, field, direction='ASC'):
        self._order_by = f"{field} {direction.upper()}"
        return self

    def limit(self, count):
        self._limit = count
        return self

    def offset(self, count):
        self._offset = count
        return self

    def build(self, count=False, count_group=False):
        query = ""
        if not self._from:
            raise ValueError("FROM clause is missing.")
        
        if count_group and count:
            query += 'SELECT COUNT(*) from ( SELECT '
        elif count_group == False and count:
            query += "SELECT COUNT(*) "
        else:
            query += "SELECT " + (", ".join(self._select) if self._select else "*")
        query += f" FROM {self._from}"

        if self._joins:
            query += " " + " ".join(self._joins)

        if self._where:
            query += " WHERE " + " AND ".join(self._where)
        
        if self._group_by:
            query += " GROUP BY " + ", ".join(self._group_by)

        if self._order_by:
            query += " ORDER BY " + self._order_by

        if self._offset is not None:
            query += f" OFFSET {self._offset}"
			
        if self._limit is not None:
            query += f" LIMIT {self._limit}"

        if count_group and count:
            query += ')'
        
        return query + ";"