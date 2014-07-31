"""
going through all tables and columns to fix python invalid dates
like 1999-00-00
"""

__author__ = 'Harihar Shankar'


import mysql.connector
import time


cxn = mysql.connector.connect(user='geo', password='0p3nM0d3!', database='geoDev', raw=True)

cur_table = cxn.cursor(buffered=True)
cur_describe = cxn.cursor(buffered=True)
cur_select = cxn.cursor(buffered=True)
cur_update = cxn.cursor(buffered=True)

query = "SHOW TABLES"
cur_table.execute(query)
for tables in cur_table:
    table = tables[0].decode('utf-8')
    query_desc = "SHOW COLUMNS FROM `%s`" % table
    cur_describe.execute(query_desc)
    for cols in cur_describe:
        column_name = cols[0].decode('utf-8')
        column_type = cols[1].decode('utf-8')
        if column_type.lower().find("date") >= 0:
            query_select = "SELECT `Description_ID`,`%s` FROM `%s`" % (column_name, table)
            conn_id = False
            try:
                cur_select.execute(query_select)
            except Exception:
                # pipelines, rail links have connection_id instead of desc_id
                query_select = "SELECT `Connection_ID`,`%s` FROM `%s`" % (column_name, table)
                conn_id = True

            for data in cur_select:
                new_date = None
                if not data[1]:
                    continue
                date = data[1].decode('utf-8')
                try:
                    time.strptime(date, "%Y-%m-%d")
                except Exception as e:
                    dates = date.split("-")

                    if dates[0] == "0000":
                        continue
                    new_date = dates[0]
                    if int(dates[1]) == 0:
                        # month
                        new_date += "-01"
                    else:
                        new_date += "-" + dates[1]
                    if int(dates[2]) == 0:
                        # day
                        new_date += "-15"
                    else:
                        new_date += "-" + dates[2]
                    time.strptime(new_date, "%Y-%m-%d")
                if new_date:
                    query_update = "UPDATE `%s` SET `%s`='%s' WHERE Description_ID=%s" \
                                   % (table, column_name, new_date, data[0].decode('utf-8'))
                    if conn_id:
                        query_update = "UPDATE `%s` SET `%s`='%s' WHERE Connection_ID=%s" \
                                       % (table, column_name, new_date, data[0].decode('utf-8'))
                    cur_update.execute(query_update)

cxn.commit()
cxn.close()