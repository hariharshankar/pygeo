
class Select():

    def __init__(self, db):
        """
        Query the database.
        :param db: a valid database connection.
        """
        self.db = db


    def read(self, table_name, columns=[], where=[], order_by=[], limit=[]):
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

        if table_name == "":
            return

        sql = ["SELECT"]

        if len(columns) == 0:
            sql.append("*")
            #cols = self.read_column_names(table_name)
            #columns = [c[0] for c in cols]
        else:
            sql.append(",".join(columns))

        sql.extend(["FROM", table_name])

        if len(where) > 0 and len(where) % 2 == 1:
            sql.append("WHERE")
            for i, w in enumerate(where):
                if i % 2 == 0 and len(w) == 3:
                    sql.extend([str(q) for q in w])
                elif i % 2 == 1 and len(w) == 1:
                    sql.append(w[0])
                else:
                    sql.pop()

        if len(order_by) > 0:
            sql.append("ORDER BY")
            sql.extend(order_by)

        if len(limit) > 0:
            sql.append("LIMIT")
            sql.append(",".join(limit))
        #return self.db.session.query(*columns)\
        #        .from_statement(" ".join(sql)).all()
        return self.db.session.execute(" ".join(sql))


    def read_column_names(self, table_name):
        """
        Read the columns of a table. Helps build queries dynamically
        without knowing the table columns.
        """

        return self.db.session.query("Field", "Type")\
                .from_statement("SHOW COLUMNS FROM %s" % (table_name)).all()

    def process_result_set(self, result):
        """
        Convert the returned values from result obj into lists for
        easy json serizlization.
        """

        keys = result.keys()
        values = []
        if not result.returns_rows:
            print("No rows in db.")
            return keys, values

        rows = result.fetchall()
        values = [r.values() for r in rows]
        values.sort()
        return keys, values
