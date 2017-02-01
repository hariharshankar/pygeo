"""
Handles all insert statements to the database.
"""

from geo.db.query import Select
import re


class InsertFactSheet(object):
    """
    Handling data insertion for the fact sheet.
    """

    def __init__(self, db):
        """
        Query the database.
        :param db: a valid database connection.
        """
        self.db = db
        self.db_conn = db.session

    def __del__(self):
        """
        Closing the open sessions.
        :return:
        """
        self.db_conn.close()

    def insert(self, table_name, form_data, module_type, description_id=0, dual=0):
        """
        The public method that determines how the data should be prepared
        and saved based on the module_type.
        """

        if not table_name or table_name == "":
            return

        if not module_type or module_type == "generic":
            return self.__insert_generic_module(table_name,
                                                form_data,
                                                description_id, dual=dual)
        elif module_type == "row_columns":
            return self.__insert_row_column_module(table_name,
                                                   form_data,
                                                   description_id)
        elif module_type == "performance":
            return self.__insert_performance_module(table_name,
                                                    form_data,
                                                    description_id)
        elif module_type == "history":
            return self.__insert_history_module(form_data)
        elif module_type == "nuclear_performance":
            return self.__insert_nuclear_performance_data(table_name, form_data, description_id)
        elif module_type == "enum_table":
            return self.__insert_enum_table(table_name, form_data, description_id)
        return

    def __insert_enum_table(self, table_name, form_data, description_id):
        """
        Inserts a row for spl cases where the label is read from enum
         and a text box is provided for the value. Like Gas field contaminants.
        """

        type_name = form_data.get("Type_Name")
        label = table_name.replace(type_name + "_", "")

        select = Select(self.db)
        column_names = select.read_column_names(table_name)

        #enum_result = select.read_column_names(table_name, where=label)
        enum_value = column_names[1][1].replace("enum(", "")
        enum_value = enum_value[:-1]

        enum = []
        replace_comma = False

        for val in enum_value:
            if val == "'":
                replace_comma = True if not replace_comma else False
            if replace_comma and val == ',':
                val = "@"
            enum.append(val)

        enum = "".join(enum)

        sql_values = {}
        sql_fields = []

        sql_statement = []
        sql_statement.append("INSERT INTO " + table_name + " SET ")

        sql_fields.append("`Description_ID`=:description_id")
        sql_values['description_id'] = description_id

        for option in enum.split(","):
            option = option.replace("'", "")
            option = option.replace("@", ",")
            #print(option, label+"_"+option)

            value = form_data.get(label+"_"+option).strip()

            if value:
                sql_fields.append("`" + label + "`=%(" + label.lower() + ")s")
                sql_values[label.lower()] = option
                sql_fields.append("`" + column_names[2][0] + "`=%(" + column_names[2][0].lower() + ")s")
                sql_values[column_names[2][0].lower()] = value

        sql_statement.append(",".join(sql_fields))
        #print("".join(sql_statement), sql_values)

        session = self.db_conn.cursor()
        try:
            session.execute("".join(sql_statement), sql_values)
            self.db_conn.commit()
        except Exception as e:
            print(e)
        finally:
            session.close()

        return 1

    def __insert_history_module(self, form_data):
        """
        Creates an entry for the edit in the History table.
        A new Description_ID is minted here for all the edits.
        """

        sql_fields = []
        sql_fields.extend(["`User_ID`=%(user_id)s",
                          "`Moderated`=%(moderated)s",
                          "`Moderator_ID`=%(moderator_id)s",
                          "`Type_ID`=%(type_id)s",
                          "`Country_ID`=%(country_id)s",
                          "`State_ID`=%(state_id)s",
                          "`Accepted`=%(accepted)s"])

        sql_values = {}

        parent_plant_id = form_data.get("Parent_Plant_ID", 0)

        if int(parent_plant_id) > 0:
            sql_fields.append("`Parent_Plant_ID`=%(parent_plant_id)s")
            sql_values['parent_plant_id'] = parent_plant_id

        sql_statement = "INSERT INTO History SET " + ",".join(sql_fields)

        sql_values['user_id'] = str(form_data.get('User_ID', 0))
        sql_values['moderated'] = form_data.get('Moderated', 0)
        sql_values['moderator_id'] = form_data.get('Moderator_ID', None)
        sql_values['type_id'] = form_data.get('Type_ID')
        sql_values['country_id'] = form_data.get('Country_ID')
        sql_values['state_id'] = form_data.get('State_ID')
        sql_values['accepted'] = form_data.get('Accepted')

        session = self.db_conn.cursor()
        try:
            session.execute(sql_statement, sql_values)
            self.db_conn.commit()
        except Exception:
            #session.rollback()
            raise

        description_id = session.lastrowid

        if int(parent_plant_id) == 0:
            parent_update_stmt = "UPDATE HISTORY SET \
                Parent_Plant_ID=%(parent_plant_id)s \
                WHERE Description_ID=%(description_id)s"
            try:
                session.execute(parent_update_stmt,
                                {'parent_plant_id': description_id,
                                 'description_id': description_id})
                self.db_conn.commit()
            except Exception:
                #session.rollback()
                raise

        session.close()
        return description_id

    def insert_dual_node_description(self, table_name, form_data, description_id,
                                       station_1_id, station_2_id, connection_id):
        """
        for dual node descriptions
        """

        sql_values = {}
        sql_fields = []
        alt_sql_fields = []

        alt_sql_statement = []
        sql_statement = []
        sql_statement.append("INSERT INTO " + table_name + " SET ")
        alt_sql_statement.append("INSERT INTO " + table_name + " SET ")

        sql_fields.append("`Description_ID`=:description_id,"
                          "Station_1_ID=:station_1_id,"
                          "Station_2_ID=:station_2_id,"
                          "Connection_ID=:connection_id")
        sql_values['description_id'] = description_id
        alt_sql_fields.append("`Description_ID`=%(description_id)s")
        sql_values['station_1_id'] = station_1_id
        alt_sql_fields.append("`Station_1_ID`=%(station_1_id)s")
        sql_values['station_2_id'] = station_2_id
        alt_sql_fields.append("`Station_2_ID`=%(station_2_id)s")
        sql_values['connection_id'] = connection_id
        alt_sql_fields.append("`Connection_ID`=%(connection_id)s")

        select = Select(self.db)
        column_names = select.read_column_names(table_name)

        #print(form_data)
        for k in column_names:
            if not form_data.get(k[0]):
                continue
            value = form_data.get(k[0])

            if k[0].find("_ID") < 0 and value:
                key = k[0]
                key = key.replace("(", "")
                key = key.replace(")", "")
                key = key.replace(":", "")
                key = key.replace("%", "")
                sql_fields.append("`" + k[0] + "`=:" + key.lower())
                alt_sql_fields.append("`" + k[0] + "`='%(" + key.lower() + ")s'")
                sql_values[key.lower()] = value.strip()

        sql_statement.append(",".join(sql_fields))
        alt_sql_statement.append(",".join(alt_sql_fields))

        session = self.db_conn.cursor()
        try:
            session.execute("".join(alt_sql_statement), sql_values)
            self.db_conn.commit()
        except Exception:
            try:
                # may be there is a spl char in the sql stmt
                # using connection().execute will not quote the sql stmt
                # and some messy hack is needed to avoid param execution
                sql_stmt = " ".join(alt_sql_statement)
                sql_stmt = sql_stmt.replace("(%)", "(##)")
                sql_stmt = re.sub(r"(\d+)%", "\g<1>##", sql_stmt)
                sql_stmt = sql_stmt % sql_values
                sql_stmt = sql_stmt.replace("(##)", "(%)")
                sql_stmt = re.sub(r"(\d+)##", "\g<1>%", sql_stmt)

                #print(sql_stmt)
                session.execute(sql_stmt)
                self.db_conn.commit()
            except Exception:
                #session.rollback()
                raise
        finally:
            session.close()

        return 1

    def __insert_generic_module(self, table_name, form_data, description_id, dual=0):
        """
        Prepares and saves data for a generic module like _Description,
        _Location, etc.
        """

        sql_values = {}
        sql_fields = []
        alt_sql_fields = []
        insert_id = 0

        alt_sql_statement = []
        sql_statement = []
        sql_statement.append("INSERT INTO " + table_name + " SET ")
        alt_sql_statement.append("INSERT INTO " + table_name + " SET ")

        if description_id > 0:
            sql_fields.append("`Description_ID`=:description_id")
            sql_values['description_id'] = description_id
            alt_sql_fields.append("`Description_ID`=%(description_id)s")

        select = Select(self.db)
        column_names = select.read_column_names(table_name)

        for k in column_names:
            kk = k[0]
            if dual > 0:
                kk = kk + "_stn" + str(dual)
            if not form_data.get(kk):
                continue
            value = form_data.get(kk)

            if kk.find("_ID") < 0 and value:
                key = k[0]
                key = key.replace("(", "")
                key = key.replace(")", "")
                key = key.replace(":", "")
                key = key.replace("%", "")
                sql_fields.append("`" + k[0] + "`=:" + key.lower())
                alt_sql_fields.append("`" + k[0] + "`=%(" + key.lower() + ")s")
                value = value.strip().replace("'", "")
                value = value.replace('"', "")
                sql_values[key.lower()] = value

        sql_statement.append(",".join(sql_fields))
        alt_sql_statement.append(",".join(alt_sql_fields))

        session = self.db_conn.cursor(dictionary=True)
        try:
            #print("".join(alt_sql_statement))
            #print(sql_values)
            session.execute("".join(alt_sql_statement), sql_values)
            self.db_conn.commit()
            insert_id = session.lastrowid
        except Exception:
            #print(session.statement)
            """
            try:
                # may be there is a spl char in the sql stmt
                # using connection().execute will not quote the sql stmt
                # and some messy hack is needed to avoid param execution
                sql_stmt = " ".join(alt_sql_statement)
                sql_stmt = sql_stmt.replace("(%)", "(##)")
                sql_stmt = re.sub(r"(\d+)%", "\g<1>##", sql_stmt)
                sql_stmt = sql_stmt % sql_values
                sql_stmt = sql_stmt.replace("(##)", "(%)")
                sql_stmt = re.sub(r"(\d+)##", "\g<1>%", sql_stmt)

                #print(sql_stmt)
                result = session.execute(sql_stmt)
                self.db_conn.commit()
                insert_id = result.lastrowid
            except Exception:
                #session.rollback()
                raise
            """
            raise
        finally:
            session.close()

        return insert_id

    def __insert_performance_module(self,
                                    table_name,
                                    form_data,
                                    description_id):
        """
        Handles performance data.
        """
        start_decade = 1950
        end_decade = 2020
        table_name = table_name.replace("_Annual", "")
        select = Select(self.db)
        column_names = select.read_column_names(table_name)

        for year in range(start_decade, end_decade):
            sql_values = {}
            sql_fields = []
            alt_sql_fields = []
            sql_statement = []
            alt_sql_statement = []

            sql_statement.append("INSERT INTO " + table_name + " SET ")
            alt_sql_statement.append("INSERT INTO " + table_name + " SET ")

            sql_fields.extend(["`Description_ID`=:description_id",
                               "`Year_yr`=:year_yr"])
            alt_sql_fields.extend(["`Description_ID`=%(description_id)s",
                                   "`Year_yr`=%(year_yr)s"])
            sql_values['description_id'] = description_id
            sql_values['year_yr'] = year

            for k in column_names:
                field_name = k[0] + "_###_" + str(year)
                if not form_data.get(field_name):
                    continue
                value = form_data.get(field_name)

                if k[0].find("_ID") < 0 and value:
                    key = k[0]
                    key = key.replace("(", "")
                    key = key.replace(")", "")
                    key = key.replace(":", "")
                    key = key.replace("%", "")
                    sql_fields.append("`" + k[0] + "`=:" + key.lower())
                    alt_sql_fields.append("`" + k[0] + "`='%(" + key.lower() + ")s'")
                    sql_values[key.lower()] = value.strip()

            if len(sql_values) == 0:
                continue

            sql_statement.append(",".join(sql_fields))
            alt_sql_statement.append(",".join(alt_sql_fields))

            session = self.db_conn.cursor()
            try:
                session.execute("".join(alt_sql_statement), sql_values)
                self.db_conn.commit()
            except Exception:
                try:
                    # may be there is a spl char in the sql stmt
                    # using connection().execute will not quote the sql stmt
                    # and some messy hack is needed to avoid param execution
                    sql_stmt = " ".join(alt_sql_statement)
                    sql_stmt = sql_stmt.replace("(%)", "(##)")
                    sql_stmt = sql_stmt % sql_values
                    sql_stmt = sql_stmt.replace("(##)", "(%)")
                    session.execute(sql_stmt)
                    self.db_conn.commit()
                except Exception:
                    #session.rollback()
                    raise
            finally:
                session.close()

        return 1

    def __insert_row_column_module(self,
                                   table_name,
                                   form_data,
                                   description_id):
        """
        Handles multiple column modules like unit_description.
        """

        select = Select(self.db)
        column_names = select.read_column_names(table_name)

        number_of_rows = form_data.get("numberOf" + table_name, 0)
        if int(number_of_rows) == 0:
            return 0

        for row_num in range(1, int(number_of_rows)+1):
            sql_values = {}
            sql_statement = []
            sql_fields = []
            alt_sql_statement = []
            alt_sql_fields = []

            sql_statement.append("INSERT INTO " + table_name + " SET ")
            alt_sql_statement.append("INSERT INTO " + table_name + " SET ")
            sql_fields.append("`Description_ID`=:description_id")
            alt_sql_fields.append("`Description_ID`=%(description_id)s")
            sql_values['description_id'] = description_id

            for k in column_names:
                field_name = k[0] + "_###_" + str(row_num)
                if not form_data.get(field_name):
                    continue

                value = form_data.get(field_name)
                if k[0].find("_ID") < 0 and value:
                    key = k[0]
                    key = key.replace("(", "")
                    key = key.replace(")", "")
                    key = key.replace(":", "")
                    key = key.replace("%", "")
                    sql_fields.append("`" + k[0] + "`=:" + key.lower())
                    alt_sql_fields.append("`" + k[0] + "`=%(" + key.lower() + ")s")
                    sql_values[key.lower()] = value.strip()

            sql_statement.append(",".join(sql_fields))
            alt_sql_statement.append(",".join(alt_sql_fields))

            session = self.db_conn.cursor(raw=True)
            try:
                #print("".join(alt_sql_statement) % sql_values)
                session.execute("".join(alt_sql_statement), sql_values)
                self.db_conn.commit()
                #print("SQL: " + session.statement)
            except Exception as e:
                #print("ERROR: " + str(e))
                try:
                    # may be there is a spl char in the sql stmt
                    # using connection().execute will not quote the sql stmt
                    # and some messy hack is needed to avoid param execution
                    sql_stmt = " ".join(alt_sql_statement)
                    sql_stmt = sql_stmt.replace("(%)", "(##)")
                    sql_stmt = sql_stmt.replace("%_", "##_")
                    sql_stmt = sql_stmt % sql_values
                    sql_stmt = sql_stmt.replace("(##)", "(%)")
                    sql_stmt = sql_stmt.replace("##_", "%_")
                    #print("ALT SQL:")
                    #print(sql_stmt)
                    session.execute(sql_stmt)
                    self.db_conn.commit()
                except Exception:
                    #session.rollback()
                    raise
            finally:
                session.close()

        return 1

    def __insert_nuclear_performance_data(self, table_name, form_data, description_id):

        select = Select(self.db)
        column_names = select.read_column_names(table_name)

        number_of_units = form_data.get("numberOfNuclear_Unit_Description", 0)
        if int(number_of_units) == 0:
            return 0

        unit_result = select.read("Nuclear_Unit_Description",
                                  columns=["Unit_Description_ID"],
                                  where=[["Description_ID",
                                          "=",
                                          description_id]]
                                  )

        unit_ids = unit_result.fetchall()
        start_decade = 1950
        end_decade = 2020
        for r, unit_id in enumerate(unit_ids):
            row_num = r + 1
            unit_id = unit_id[0]

            for year in range(start_decade, end_decade):
                sql_values = {}
                sql_statement = []
                sql_fields = []
                alt_sql_statement = []
                alt_sql_fields = []

                sql_statement.append("INSERT INTO " + table_name + " SET ")
                alt_sql_statement.append("INSERT INTO " + table_name + " SET ")
                sql_fields.append("`Description_ID`=:description_id")
                alt_sql_fields.append("`Description_ID`=%(description_id)s")
                sql_values['description_id'] = description_id

                sql_fields.append("`Unit_Description_ID`=:unit_description_id")
                alt_sql_fields.append("`Unit_Description_ID`=%(unit_description_id)s")
                sql_values['unit_description_id'] = unit_id

                sql_fields.append("`Year_yr`=:year_yr")
                alt_sql_fields.append("`Year_yr`=%(year_yr)s")
                sql_values['year_yr'] = year

                for k in column_names:
                    field_name = k[0] + "_" + str(row_num) + "_###_" + str(year)
                    if not form_data.get(field_name) or form_data.get(field_name) == "None" or form_data.get(field_name) == "":
                        continue

                    value = form_data.get(field_name)
                    if k[0].find("_ID") < 0 and value:
                        key = k[0]
                        key = key.replace("(", "")
                        key = key.replace(")", "")
                        key = key.replace(":", "")
                        key = key.replace("%", "")
                        sql_fields.append("`" + k[0] + "`=:" + key.lower())
                        alt_sql_fields.append("`" + k[0] + "`='%(" + key.lower() + ")s'")
                        sql_values[key.lower()] = value.strip()

                if len(sql_values) <= 3:
                    continue

                sql_statement.append(",".join(sql_fields))
                alt_sql_statement.append(",".join(alt_sql_fields))

                session = self.db_conn.cursor()
                try:
                    session.execute("".join(alt_sql_statement), sql_values)
                    self.db_conn.commit()
                except Exception:
                    try:
                        # may be there is a spl char in the sql stmt
                        # using connection().execute will not quote the sql stmt
                        # and some messy hack is needed to avoid param execution
                        sql_stmt = " ".join(alt_sql_statement)
                        sql_stmt = sql_stmt.replace("(%)", "(##)")
                        sql_stmt = sql_stmt.replace("%_", "##_")
                        sql_stmt = sql_stmt % sql_values
                        sql_stmt = sql_stmt.replace("(##)", "(%)")
                        sql_stmt = sql_stmt.replace("##_", "%_")
                        session.execute(sql_stmt)
                        self.db_conn.commit()
                    except Exception:
                        #session.rollback()
                        raise
                finally:
                    session.close()

        return 1
