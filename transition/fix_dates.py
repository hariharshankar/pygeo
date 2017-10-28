"""
going through all tables and columns to fix python invalid dates
like 1999-00-00
"""

import mysql.connector as pymysql

__author__ = 'Harihar Shankar'

cxn = pymysql.connect(user='geo', password='0p3nM0d3!',
                      database='geoDev')

cur_table = cxn.cursor(buffered=True)
cur_describe = cxn.cursor(buffered=True)
cur_select = cxn.cursor(buffered=True, raw=True)
cur_update = cxn.cursor(buffered=True)
cur_alter = cxn.cursor(buffered=True)

query = "SHOW TABLES"
cur_table.execute(query)
for tables in cur_table:
    #table = tables[0].decode("utf-8")
    table = tables[0]
    query_desc = "SHOW COLUMNS FROM `%s`" % table
    cur_describe.execute(query_desc)
    for cols in cur_describe:
        column_name = cols[0]
        column_type = cols[1]
        if column_type.lower().find("date") >= 0:
            query_select = "SELECT `Description_ID`,`%s` FROM `%s`" % (column_name, table)
            conn_id = False
            try:
                cur_select.execute(query_select)
            except Exception:
                # pipelines, rail links have connection_id instead of desc_id
                query_select = "SELECT `Connection_ID`,`%s` FROM `%s`" % (column_name, table)
                conn_id = True

            col_year = column_name.replace("_dt", "_dt_year")
            col_month = column_name.replace("_dt", "_dt_month")
            col_day = column_name.replace("_dt", "_dt_day")

            query_alter = "ALTER TABLE `%s` ADD COLUMN " \
                          "(`%s` YEAR, `%s` TINYINT(2), `%s` TINYINT(2))" %\
                          (table, col_year, col_month, col_day)
            try:
                cur_alter.execute(query_alter)
            except:
                pass

            for data in cur_select:
                new_date = None
                if not data[1]:
                    continue
                date = data[1].decode("utf8")
                dates = date.split("-")
                year = None
                month = None
                day = None
                if dates[0] != "0000":
                    year = dates[0]
                if int(dates[1]) != 0:
                    # month
                    month = int(dates[1])
                if int(dates[2]) != 0:
                    # day
                    day = int(dates[2])
                query_update = "UPDATE `%s` SET `%s`='%s', `%s`='%s', `%s`='%s' " \
                               "WHERE Description_ID=%s" \
                               % (table, col_year or 0, year or 0,
                                  col_month or 0, month or 0,
                                  col_day or 0, day or 0, data[0].decode("utf8"))
                if conn_id:
                    query_update = "UPDATE `%s` SET `%s`='%s', `%s`='%s', `%s`='%s'" \
                                           " WHERE Connection_ID=%s" \
                    % (table, col_year or 0, year or 0,
                       col_month or 0, month or 0,
                       col_day or 0, day or 0, data[0].decode("utf8"))
                try:
                    cur_update.execute(query_update)
                except pymysql.DataError:
                    pass

            query_alter = "ALTER TABLE `%s` DROP COLUMN `%s`" %\
                          (table, column_name)
            cur_alter.execute(query_alter)
cxn.commit()
cxn.close()
