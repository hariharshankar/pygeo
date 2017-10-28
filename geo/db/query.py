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
        self.db_conn = db.session
        self.db_conn.get_warnings = True

    def __del__(self):
        """
        Close the open sessions.
        :return:
        """
        self.db_conn.close()

    def read(self, table_name,
             columns=None,
             where=None,
             order_by=None,
             limit=None, dict_cursor=True):
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
        :returns: {"keys": [keys], "values": [v]}
        """

        if table_name == "" or table_name.find(" ") >= 0:
            return

        if dict_cursor:
            db_cur = self.db_conn.cursor(dictionary=True)
        else:
            db_cur = self.db_conn.cursor(raw=True)
        sql = ["SELECT"]
        alt_sql = ["SELECT"]

        params = {}
        if not columns or len(columns) == 0:
            sql.append("*")
            alt_sql.append("*")
        else:
            sql.append(",".join([c for c in columns if c.find(" ") < 0]))
            alt_sql.append(",".join([c for c in columns if c.find(" ") < 0]))

        sql.extend(["FROM", table_name])
        alt_sql.extend(["FROM", table_name])

        if where and len(where) > 0 and len(where) % 2 == 1:
            sql.append("WHERE")
            alt_sql.append("WHERE")
            for i, whe in enumerate(where):
                if i % 2 == 0\
                        and len(whe) == 3\
                        and whe[1].lower() in\
                        ['<', '>', '<=', '>=', '=', 'like', 'in']:
                    if whe[1].lower() == 'in' and len(whe[2]) == 0:
                        return []
                    # the prepare stmt throws an error if "in" is used
                    # with only one value. converting it into "=" instead.
                    if whe[1].lower() == 'in' and len(whe[2]) == 1:
                        sql.extend([whe[0], "=", "':wh%s'" % str(i)])
                        alt_sql.extend([whe[0], "=", "%(wh"+str(i)+")s"])
                        params["wh"+str(i)] = whe[2][0]
                    elif whe[1].lower() == 'in':
                        sql.extend([whe[0], whe[1], "("])
                        alt_sql.extend([whe[0], whe[1], "("])
                        vals = []
                        alt_vals = []
                        for v, val in enumerate(whe[2]):
                            vals.append("':wh%s'" % str(v))
                            alt_vals.append("%(wh" + str(v)+")s")
                            params["wh"+str(v)] = str(val)
                        sql.append(",".join(vals))
                        sql.append(")")
                        alt_sql.append(",".join(alt_vals))
                        alt_sql.append(")")
                        #params["wh"+str(i)] = ",".join([str(val) for val in whe[2]])
                    else:
                        sql.extend([whe[0], whe[1], "':wh%s'" % str(i)])
                        alt_sql.extend([whe[0], whe[1], "%(wh"+str(i)+")s"])
                        params["wh"+str(i)] = whe[2]
                elif i % 2 == 1 and whe[0].lower() in ['and', 'or']:
                    sql.append(whe[0])
                    alt_sql.append(whe[0])
                else:
                    sql.pop()
                    alt_sql.pop()

        if order_by and len(order_by) > 0:
            sql.append("ORDER BY")
            sql.extend(order_by)
            alt_sql.append("ORDER BY")
            alt_sql.extend(order_by)

        if limit and len(limit) > 0:
            sql.append("LIMIT")
            sql.append(",".join(limit))
            alt_sql.append("LIMIT")
            alt_sql.append(",".join(limit))

        try:
            db_cur.execute(" ".join(alt_sql), params)
        except Exception:
            try:
                # may be there is a spl char in the sql stmt
                # using connection().execute will not quote the sql stmt
                # and some messy hack is needed to avoid param execution
                sql_stmt = " ".join(alt_sql)
                sql_stmt = sql_stmt.replace("(%)", "(##)")
                sql_stmt = sql_stmt % params
                sql_stmt = sql_stmt.replace("(##)", "(%)")
                db_cur.execute(sql_stmt)
            except Exception:
                raise

        #print(db_cur.statement)
        #print(db_cur.fetchwarnings())
        return db_cur

    def read_column_names(self, table_name, where=None):
        """
        Read the columns of a table. Helps build queries dynamically
        without knowing the table columns.
        """

        db_cur = self.db_conn.cursor(dictionary=True)

        sql = "SHOW COLUMNS FROM %s" % table_name
        if where:
            sql += " LIKE '%s'" % where

        db_cur.execute(sql)
        cols = [(dic["Field"], dic["Type"]) for dic in db_cur]
        return cols

    @staticmethod
    def process_result_set(result):
        """
        Convert the returned values from result obj into lists for
        easy json serialization.
        """

        if not result:
            return [], []
        keys = result.column_names
        values = []
        if not result.with_rows:
            return keys, values

        res = result.fetchall()
        for r in res:
            v = []
            for k in keys:
                v.append(r.get(k))
            values.append(v)
        #sorted(values)
        return keys, values

