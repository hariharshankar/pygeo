"""
Builds and executes all select sql statements.
"""


class Select(object):
    """
    Builds and executes all select sql statements.
    """

    def __init__(self, db):
        """
        Query the database.
        :param db: a valid database connection.
        """
        self.db_conn = db

    def read(self, table_name,
             columns=None,
             where=None,
             order_by=None,
             limit=None):
        """
        Fetch rows from database.

        :param table_name: <string> name of the table
        :param columns: <list<string>> column names to fetch
        :param where: list<<list<string>>> where clause as a list of strings.
                      [["field_name", "operator", "value"], ["and|or"],
                      ["field_name", "operator", "value"]]
        :param order_by: list<<string>,<string>> order_by clause
                        ["field_name", "asc|desc"]
        :param limit: list<<int>,<int>> start stop limits like [0,1]
        """

        if table_name == "" or table_name.find(" ") >= 0:
            return

        sql = ["SELECT"]

        if not columns or len(columns) == 0:
            sql.append("*")
        else:
            sql.append(",".join([c for c in columns if c.find(" ") < 0]))

        sql.extend(["FROM", table_name])

        if where and len(where) > 0 and len(where) % 2 == 1:
            sql.append("WHERE")
            for i, whe in enumerate(where):
                if i % 2 == 0 and len(whe) == 3:
                    sql.extend([str(q) for q in whe])
                elif i % 2 == 1 and len(whe) == 1:
                    sql.append(whe[0])
                else:
                    sql.pop()

        if order_by and len(order_by) > 0:
            sql.append("ORDER BY")
            sql.extend(order_by)

        if limit and len(limit) > 0:
            sql.append("LIMIT")
            sql.append(",".join(limit))
        return self.db_conn.session.execute(" ".join(sql))

    def read_column_names(self, table_name, where=None):
        """
        Read the columns of a table. Helps build queries dynamically
        without knowing the table columns.
        """

        sql = "SHOW COLUMNS FROM %s" % table_name
        if where:
            sql = sql + " LIKE '%s'" % where

        return self.db_conn.session.query("Field", "Type")\
            .from_statement(sql).all()

    def process_result_set(self, result):
        """
        Convert the returned values from result obj into lists for
        easy json serizlization.
        """

        keys = result.keys()
        values = []
        if not result.returns_rows:
            return keys, values

        rows = result.fetchall()
        values = [r.values() for r in rows]
        values.sort()

        return keys, values
