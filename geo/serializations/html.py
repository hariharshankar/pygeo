"""
Builds the HTML representation for the fact sheets.
"""

from geo.core.geo_resource import GeoResource


class Html(object):
    """
    Builds the HTML representation for the fact sheets.
    """

    def __init__(self, resource):
        self.resource = resource
        self.editable = True

    def generate_editable(self):
        """
        Creates an html form using the resource data.
        """

        self.editable = True
        return self.__generate_resource_modules()

    def __generate_resource_modules(self):
        """
        Handles creating the appropriate module representation.
        """

        res_modules = self.resource.select.read("Type_Features",
                                       where=[["Type_ID", "=", self.resource.type_id]]
                                       )
        modules = res_modules.fetchone()
        module_names = []
        full_feature_list = self.resource.select.read_column_names("Type_Features", where='Features')[0][1]

        if type(modules['Features']) == str:
            module_names = modules['Features'].split(',')
        else:
            full_feature_list = full_feature_list.replace("set(", "")
            full_feature_list = full_feature_list.replace(")", "")
            full_feature_list = full_feature_list.replace("\"", "")
            full_feature_list = full_feature_list.replace("'", "")

            module_names = [str(module)
                            for module in full_feature_list.split(",")
                            if module in modules['Features']]

        html = []

        module_names.append("Notes")
        module_names.insert(0, "Abstract")

        for module in module_names:
            module_id = module + "_module"
            module_heading = Html.__make_readable(module)

            #print(module)
            module_header_class, module_content = \
                self.__get_module_for_feature(module)

            if module_content:
                html.append(
                    {"module_heading": module_heading,
                     "module_id": module_id,
                     "module_header_class": module_header_class,
                     "module_content": module_content
                     }
                )

        return html

    def __get_module_for_feature(self, feature):
        """
        Invokes the appropriate methods to build the module.
        """

        if feature == "Abstract":
            return "generic-module", self.__create_abstract_module()
        elif feature == "Notes":
            return "generic-module", self.__create_notes_module()
        elif feature.startswith("Unit_"):
            return "single-row-module", self.make_unit_module(feature)
        elif feature == "Location" or feature == "Dual_Node_Locations":
            return "generic-module", self.__make_location_module()
        elif feature.startswith("Annual_Performance"):
            return "generic-module", self.__make_performance_module()
        elif feature == "Identifiers" or feature == "Dual_Node_Identifiers":
            return "generic-module", self.__make_identifiers_module()
        elif feature.startswith("Environmental_Issues")\
                or feature.startswith("Comments") \
                or feature.startswith("References") \
                or feature.startswith("Upgrades"):
            return "single-row-module", self.__make_single_row_module(feature)
        elif feature.startswith("Owner_Details"):
            owner = []
            owner.append(self.__make_generic_module(feature=feature))
            owner.append(self.__make_single_row_module("Owners"))
            return "single-row-module", "".join(owner)
        elif feature.startswith("Associated_Infrastructure"):
            #return "generic-module", self.__create_associated_infrastructure()
            return "generic-module", "Associated Infrastructure"
        elif feature.startswith("History"):
            return "", ""
        elif feature.startswith("Description"):
            description = []
            description.append(self.__make_generic_module(feature=feature))
            if self.resource.type_id == 11:
                description.append(self.__make_enum_table_row("Contaminants"))
            return "generic-module", "".join(description)
        elif feature == "Refinery_Products":
            return "generic-module", self.__make_generic_module(table_name="Crude_Oil_Refineries_Products")
        elif feature == "Wind_Potential_Height":
            return "generic-module", self.__make_wind_potential_height()
        elif feature == "Dual_Node_Description":
            return "generic-module", self.__make_description_with_segments()
        return "", ""

    def __create_associated_infrastructure(self):

        html = []
        result = self.resource.select.read("Associated_Infrastructure",
                                  where=[["Parent_Plant_ID",
                                          "=",
                                          self.resource.parent_plant_id]]
                                  )

        #keys = result.column_names
        values = result.fetchall()
        for value in values:
            ai_parent_plant_id = value["Associated_Parent_Plant_ID"]

            ai_res = GeoResource(self.resource.connection, description_id=ai_parent_plant_id)

            html.append("<b><a href=\"geoid/%s\" target=\"_blank\">%s</a></b><br/>" % (ai_res.get_latest_revision_id(),
                                                                                ai_res.get_resource_name()))

        html.append('<div id="searchAI" class="ai-search-module">')
        html.append("<div id='aiDatabase_Type' class='aiSelectable'></div>")
        html.append("<div id='aiType' class='aiSelectable'></div>")
        html.append("<div id='aiCountry' class='aiSelectable'></div>")
        html.append("<div id='aiState' class='aiSelectable'></div>")
        html.append("<div class='aiUpdateButton' id='aiUpdateButton'>")
        html.append("<button id='createAIResource' class='createAIResource'>Create</button>")
        html.append("</div>")

        html.append("</div>")
        html.append("<div id='aiResources' class='aiSelectable' style='top: 20px;'>")
        html.append("</div>")
        return "".join(html)

    def __create_abstract_module(self):

        return "abstract"

    def __create_notes_module(self):
        return "notes"

    def __make_description_with_segments(self):
        """
        builds station and connecting pipeline sections.
        :return:
        """

        html = []
        desc_result = self.resource.select.read(self.resource.type_name + "_Description",
                                       where=[["Description_ID",
                                               "=",
                                               self.resource.description_id]]
                                        )
        values = desc_result.fetchone()
        station_1_id = values['Station_1_ID']
        station_2_id = values['Station_2_ID']
        connection_id = values['Connection_ID']


        html.append("<h2>Station A</h2>")
        html.append(self.__make_generic_module(feature=None,
                                               table_name=self.resource.type_name + "_Station_Description",
                                               _id=("Station_ID", station_1_id), dual=1))

        html.append("<h2>" + str(self.resource.type_name) + "</h2>")
        html.append(self.__make_generic_module(feature=None,
                                               table_name=self.resource.type_name + "_Connection_Description",
                                               _id=("Connection_ID", connection_id)))
        html.append("<h2>Station B</h2>")
        html.append(self.__make_generic_module(feature=None,
                                               table_name=self.resource.type_name + "_Station_Description",
                                               _id=("Station_ID", station_2_id), dual=2))

        return "".join(html)

    def __make_wind_potential_height(self):
        """
        Builds a module for wind potential height.
        :return:
        """

        html = []
        result = self.resource.select.read("Wind_Potential_Height",
                                  where=[["Description_ID",
                                          "=",
                                          self.resource.description_id]]
        )

        #keys = result.keys()
        #values = result.fetchall()
        keys, values = self.resource.select.process_result_set(result)

        #none_values = (None for k in keys)

        height_ranges = self.__process_enum_from_db("Wind_Potential_Height", "Height_enumfield")
        html.append("<table>")
        html.append("<tr>")
        html.append("<th></th>")
        height_values = {}
        for height in height_ranges:
            html.append("<th>" + height + "</th>")
        html.append("</tr>")
        for value in values:
            height_values[value[1]] = value

        #print(height_values)
        for index, key in enumerate(keys):
            if key.find("_ID") > 0 or key.find("Height_enumfield") >= 0:
                continue

            html.append("<tr>")
            html.append("<td>" + self.__make_readable(key) + "</td>")
            for height in height_ranges:
                print(height)
                html.append("<td>")
                #if not height_values.get(height):
                #    height_values[height] = none_values
                val = list(height_values.get(height))
                print(val)
                html.append(self.__create_number_input_field(key, val[index]))
                html.append("</td>")
            html.append("</tr>")
        #print(keys)
        #print(values)
        html.append("</table>")
        return "".join(html)

    def __make_generic_module(self, feature=None, table_name=None, _id=None, dual=0):
        """
        Builds the generic module representation,
        like description module.
        """

        if not table_name and not feature:
            return
        html = []
        if not table_name:
            table_name = self.resource.type_name + "_" + feature

        result = self.resource.select.read(table_name,
                                  where=[["Description_ID" if not _id else _id[0],
                                          "=",
                                          self.resource.description_id if not _id else _id[1]]],
                                  dict_cursor=False)

        keys = result.column_names
        values = result.fetchone()
        if not values:
            values = [None for k in keys]

        html.append("<table>")
        for i, k in enumerate(keys):
            html.append("<tr>")
            html.append(self.__create_editable_row(k,
                                                   values[i],
                                                   table_name,
                                                   False, dual=dual)
                        )
            html.append("</tr>")
        html.append("</table>")

        return "".join(html)

    def __make_single_row_module(self, feature):
        """
        Builds multi column modules like unit description.
        """

        table_name = self.resource.type_name + "_" + feature
        result = self.resource.select.read(table_name,
                                  where=[["Description_ID",
                                         "=",
                                         self.resource.description_id]]
                                  )
        #keys = result.column_names
        #values = result.fetchall()
        keys, values = self.resource.select.process_result_set(result)

        html = []
        html.append("<table>")
        html.append(self.__create_spreadsheet_row(keys, values, table_name,
                                                  module_type=feature))
        html.append("</table>")
        return "".join(html)

    def __process_enum_from_db(self, table_name, field_name):
        """
        reads the enum for the field in db, and returns a list of enum values
        :param table_name:
        :param field_name:
        :return:
        """
        enum_result = self.resource.select.read_column_names(table_name, where=field_name)

        # the result object is a list of tuples.
        # the tuple looks like (feature, values)
        enum_value = enum_result[0][1].replace("enum(", "")
        enum_value = enum_value[:-1]

        enum = []
        replace_comma = False

        for val in enum_value:
            if val == "'":
                replace_comma = True if not replace_comma else False
            #if val == "'":
            #    replace_comma = False
            if replace_comma and val == ',':
                val = "@"
            val = val.replace("'", "")
            val = val.replace('"', "")
            enum.append(val)

        enum = "".join(enum)

        return enum.split(",")

    def __make_enum_table_row(self, feature):
        """
        Builds a row for spl cases where the label is read from enum
         and a text box is provided for the value. Like Gas field contaminants.
        :param feature:
        :return:
        """

        table_name = self.resource.type_name + "_" + feature

        result = self.resource.select.read(table_name,
                                  where=[["Description_ID",
                                          "=",
                                          self.resource.description_id]]
        )

        keys = result.column_names
        values = result.fetchall()

        #print(keys)
        #print(values)
        value_key = keys[-1]

        html = []
        html.append("<table>")
        html.append("<tr>")
        html.append(self.__create_label(feature, ""))
        enum = self.__process_enum_from_db(table_name, feature)

        for option in enum:
            option = option.replace("'", "")
            option = option.replace("@", ",")

            val = ""
            for value in values:
                if value[1] == option:
                    val = value[2]

            html.append(self.__create_label(option, "_nbr"))
            html.append("<td>")
            html.append(self.__create_number_input_field(feature + "_" + option, val))
            html.append("</td>")

        html.append("</table>")
        return "".join(html)

    def __make_location_module(self):
        """
        Builds the location module.
        """

        html = []
        html.append("<div id='overlay-details'></div>")
        html.append("<div id='map-resize'>")
        html.append("<div id='map-container' style='height: 480px;'></div>")
        html.append("</div>")
        html.extend(["<input type='hidden' ",
                    "name='map_json' ",
                    "id='map_json' ",
                    "value='/location?description_id="
                     + str(self.resource.description_id) + "' ",
                     "class='widget_urls' />"])

        ai_result = self.resource.select.read("Associated_Infrastructure",
                                     columns=["Associated_Parent_Plant_ID"],
                                     where=[["Parent_Plant_ID",
                                             "=",
                                             self.resource.parent_plant_id]])

        ai_parent_plant_ids = ai_result.fetchall()

        for ai_id in ai_parent_plant_ids:
            ai_id = ai_id[0]
            where = [["Parent_Plant_ID", "=", ai_id]]
            where.extend([["and"], ["Accepted", "=", "1"]])

            desc_id_result = self.resource.select.read("History", columns=["max(Description_ID)"],
                                   where=where)

            res = desc_id_result.fetchone()
            ai_desc_id = res[0]
            html.extend(["<input type='hidden' ",
                         "name='ai_map_json' ",
                         "id='ai_map_json' ",
                         "value='/location?description_id="
                         + str(ai_desc_id) + "' ",
                         "class='widget_urls' />"])

        return "".join(html)

    def __make_identifiers_module(self):
        """
        Makes the identifier module.
        """

        table_name = self.resource.type_name + "_Description"
        result = self.resource.select.read(table_name,
                                  where=[["Description_ID",
                                         "=",
                                         self.resource.description_id]]
                                  )

        keys = result.column_names
        values = result.fetchone()
        if not values:
            values = dict((k, None) for k in keys)
        html = []
        html.extend(["<input type='hidden' ",
                    "name='Description_ID' ",
                    "id='Description_ID' ",
                    "value='" + str(self.resource.description_id) + "'",
                     "/>"
                     ])
        html.extend(["<input type='hidden' ",
                    "name='Type_ID' ",
                    "id='Type_ID' ",
                    "value='" + str(self.resource.type_id) + "' ",
                     "/>"
                     ])
        html.extend(["<input type='hidden' ",
                    "name='Country_ID' ",
                    "id='Country_ID' ",
                    "value='" + str(self.resource.country_id) + "' ",
                     "/>"
                     ])
        html.extend(["<input type='hidden' ",
                    "name='State_ID' ",
                    "id='State_ID' ",
                    "value='" + str(self.resource.state_id) + "' ",
                     "/>"
                     ])
        html.extend(["<input type='hidden' ",
                     "name='Type_Name' ",
                     "id='Type_Name' ",
                     "value='" + self.resource.type_name + "' ",
                     "/>"
        ])
        html.append("<table>")

        segment_names = ["Name_of_this_Segment",
                         "Name_of_the_Pipeline"]

        for k in keys:
            if k == "Name_omit" or k.find("_itf") >= 0 or k in segment_names:
                html.append("<tr>")
                html.append(self.__create_editable_row(k,
                                                       values[k],
                                                       table_name,
                                                       True)
                            )
                html.append("</tr>")
        html.append("</table>")

        return "".join(html)

    def __make_performance_module(self):
        """
        Retrieves the performance data and invokes the
        method that creates the performance table.
        """

        table_name = self.resource.type_name + "_Performance"
        result = self.resource.select.read(table_name,
                                  where=[["Description_ID",
                                         "=",
                                         self.resource.description_id]]
                                  )

        #keys.extend(result.column_names)
        #values.extend(result.fetchall())
        keys, values = self.resource.select.process_result_set(result)

        if self.resource.type_id == 5:

            units_number_result = self.resource.select.read(self.resource.type_name + "_Unit_Description",
                                                   columns=["count(Description_ID)"],
                                                   where=[["Description_ID",
                                                           "=",
                                                           self.resource.description_id]])

            number_of_units = units_number_result.fetchall()[0]["count(Description_ID)"]

            cap_gen_table_name = "Nuclear_Capacity_Generated"
            gwh_table_name = "Nuclear_Gigawatt_Hours_Generated"

            cap_gen_result = self.resource.select.read(cap_gen_table_name,
                                              columns=["Unit_Description_ID", "Year_yr", "Capacity_Generated_nbr"],
                                              where=[["Description_ID",
                                                      "=",
                                                      self.resource.description_id]],
                                              order_by=["Unit_Description_ID", "asc"]
            )
            cap_gen_keys, cap_gen_values = self.resource.select.process_result_set(cap_gen_result)
            keys, values = self.__format_nuclear_performance_data(keys, values, cap_gen_keys, cap_gen_values, number_of_units)

            gwh_result = self.resource.select.read(gwh_table_name,
                                          columns=["Unit_Description_ID", "Year_yr", "Gigawatt_Hours_Generated_nbr"],
                                          where=[["Description_ID",
                                                  "=",
                                                  self.resource.description_id]],
                                          order_by=["Unit_Description_ID", "asc"]
            )
            gwh_keys, gwh_values = self.resource.select.process_result_set(gwh_result)
            keys, values = self.__format_nuclear_performance_data(keys, values, gwh_keys, gwh_values, number_of_units)
        #print(keys)
        #print(values)

        html = []
        html.append(self.__create_performance_table(keys, values))
        return "".join(html)

    def __format_nuclear_performance_data(self, performance_keys, performance_values, nuclear_keys, nuclear_values, number_of_units):
        year_index = None
        key_count = 0
        for key in performance_keys:
            if key == "Year_yr":
                year_index = key_count
                break
            elif not year_index:
                key_count += 1
        yfound = []

        cap_val = {}
        units = {}
        unit_index = {}
        for cap_gen_val in nuclear_values:
            units[cap_gen_val[0]] = None
        performance_keys = list(performance_keys)
        for i in range(number_of_units):
            performance_keys.insert(year_index+i+1, nuclear_keys[2] + "_" + str(i+1))

        #print(performance_keys, len(performance_keys))
        #print(performance_values)

        new_perf_val = []
        for val in performance_values:
            val = list(val)
            for i in range(number_of_units):
                val.insert(year_index+i+1, None)
                if i < len(units):
                    unit_index[list(units.keys())[i]] = year_index+i+1
            #print("FFf", val, len(val))
            new_perf_val.append(val)

        for val in new_perf_val:
            for cap_gen_val in nuclear_values:
                if val[year_index] == cap_gen_val[1]:
                    yfound.append(val[year_index])
                    val[unit_index[cap_gen_val[0]]] = cap_gen_val[2]
            #while len(val) < len(performance_keys):
            #    val.append(None)
            #print("HHH", val, len(val))

        #print(performance_values)

        for cap_gen_val in nuclear_values:
            if cap_gen_val[1] not in yfound:
                if not cap_val.get(cap_gen_val[1]+cap_gen_val[0]):
                    cap_val[cap_gen_val[1]+cap_gen_val[0]] = []
                    for key in performance_keys:
                        cap_val[cap_gen_val[1]+cap_gen_val[0]].append(None)
                    #year
                    cap_val[cap_gen_val[1]+cap_gen_val[0]][year_index] = cap_gen_val[1]
                    cap_val[cap_gen_val[1]+cap_gen_val[0]][year_index+1] = cap_gen_val[2]
                else:
                    cap_val[cap_gen_val[1]+cap_gen_val[0]][year_index+(len(units)-1)] = cap_gen_val[2]
        for cv in cap_val:
            #print(cap_val[cv], len(cap_val[cv]))
            new_perf_val.append(cap_val[cv])

        return performance_keys, new_perf_val

    def __create_performance_table(self, keys, values):
        """
        Builds the performance table html.
        """

        decade_start = 1950
        decade_end = 2020

        table = []
        table.append("<table>")
        table.append("<tr>")

        row_count = 0
        table.append("<td>")
        table.append("<table class='performance-label'>")
        table.append("<tr class='perf-row even-row'></tr>")
        row_count += 1

        year_index = None
        key_count = 0
        vals = []
        for key in keys:

            if key == "Year_yr":
                year_index = key_count
            elif not year_index:
                key_count += 1

            if self.__display_key(key):
                if row_count % 2 == 0:
                    table.append("<tr class='perf-row even-row'>")
                else:
                    table.append("<tr class='perf-row odd-row'>")
                table.extend(["<td><input type='checkbox' id='",
                              key,
                              "_###_",
                              str(row_count),
                              "' /></td>"])
                table.append("<th>" + Html.__make_readable(key) + "</th>")
                table.append("</tr>")
                row_count += 1
            vals.append(None)

        table.append("<tr class='perf-row even-row'></tr>")
        table.append("</table>")
        table.append("</td>")

        row_count = 0

        table.append("<td>")
        table.append("<table class='performance-values'>")
        table.append("<tr class='perf-row even-row'>")
        row_count += 1

        for year in range(decade_start, decade_end):
            table.append("<th>" + str(year) + "</th>")
        table.append("</tr>")

        key_count = 0
        for key in keys:

            if self.__display_key(key):
                if row_count % 2 == 0:
                    table.append("<tr class='perf-row even-row'>")
                else:
                    table.append("<tr class='perf-row odd-row'>")

                for year in range(decade_start, decade_end):
                    value = None
                    for val in values:
                        if val[year_index] == year:
                            value = val
                            break
                    if not value:
                        value = vals

                    value = value[key_count]
                    if not value:
                        value = ""

                    table.append(
                        "<td>" +
                        self.__create_input_field(
                            key + "_###_" + str(year), value, "performance"
                        ) +
                        "</td>"
                    )

                table.append("</tr>\n")
                row_count += 1
            key_count += 1

        table.append("<tr class='perf-row'>")

        for year in range(decade_start, decade_end):
            table.append("<th>" + str(year) + "</th>")
        table.append("</tr>")

        table.append("</table>")
        table.append("</td>")
        table.append("</tr>")
        table.append("</table>")

        return "".join(table)

    def make_unit_module(self, feature):
        """
        Builds the unit description module.
        """

        html = []
        table_name = self.resource.type_name + "_" + feature
        result = self.resource.select.read(table_name,
                                  where=[["Description_ID",
                                         "=",
                                         self.resource.description_id]],
                                  dict_cursor=False)
        #keys = result.column_names
        #values = result.fetchall()
        #keys, values = self.resource.select.process_result_set(result)
        keys = result.column_names
        values = result.fetchall()

        unit_values = []
        control_values = []
        unit_keys = []
        control_keys = []

        for k in keys:
            if not k.find("Control_") >= 0 and not k.find("Monitor_") >= 0:
                unit_keys.append(k)
            else:
                #key = k.replace("Control_", "")
                #key = key.replace("Monitor_", "")
                control_keys.append(k)

        for value in values:
            unit_values.append(value[0:len(unit_keys)])

        for value in values:
            control_values.append(value[len(unit_keys):len(keys)])

        html.append("<table>")
        html.append(
            self.__create_spreadsheet_row(
                unit_keys,
                unit_values,
                self.resource.type_name + "_" + feature,
                "unit")
        )
        html.append("</table>")
        if len(control_keys) > 0:
            html.append("<table>")
            html.append("<tr><th colspan='6' style='padding-left: 100px;'>Year (YYYY) in which controls added</th>\
                        <th colspan='6' style='padding-left: 200px;'> Year (YYYY) in which monitors added</th></tr>")
            html.append(
                self.__create_spreadsheet_row(
                    control_keys,
                    control_values,
                    self.resource.type_name + "_" + feature,
                    "unit_control")
            )
            html.append("</table>")
        return "".join(html)

    def __create_spreadsheet_row(self, keys, values, table_name,
                                 module_type=None):
        """
        Creates a spreadsheet like row/column.
        """
        row = []
        row.append("<tr>")

        # check box heading
        row.append("<th></th>")

        if table_name.find("Owners") >= 0:
            row.append("<th>Owner #</th>")
        else:
            row.append("<th>#</th>")

        null_vals = []
        #rng_indexes = {}
        for index, key in enumerate(keys):
            if key.find('_rng1') >= 0:
                key = key.replace("_rng1", "_From_rng1")
            if key.find('_rng2') >= 0:
                key = key.replace("_rng2", "_To_rng2")
            null_vals.append(None)
            if self.__display_key(key):
                row.append("<th>" + Html.__make_readable(key, module_type="unit_control") + "</th>")

        if not values:
            values = []
            values.append(null_vals)
        elif len(values) == 0:
            values.append(null_vals)

        row.append("</tr>")

        row.extend(self.__create_rows_for_values(values,
                                                 keys,
                                                 table_name,
                                                 module_type))

        row.append("</tr>")
        return "".join(row)

    def __create_rows_for_values(self, values, keys, table_name, module_type):
        """
        Creates the individual rows for spreadsheet like rows.
        """
        row = []
        line_count = 0
        for val in values:
            count = 0
            row.append("<tr class='single-rows'>")
            if self.editable:
                row.extend(["<td><input type='checkbox'",
                            "id='", table_name, "_###_", str(line_count),
                            "' name='", table_name, "_###_", str(line_count),
                            "'></td>"])
            else:
                row.extend(["<td></td>"])

            line_count += 1
            row.extend(["<td>", str(line_count), "</td>"])
            for value in val:
                if not self.__display_key(keys[count]):
                    count += 1
                    continue

                if not value:
                    value = ""
                elif type(value) == bytearray:
                    value = value.decode("utf-8")

                if keys[count].find("_enumfield") >= 0:
                    row.extend(["<td>",
                                self.__create_enum_field_from_table(
                                    keys[count] + "_###_" + str(line_count),
                                    value,
                                    table_name),
                                "</td>"])
                elif keys[count].find("_setfield") >= 0:
                    row.extend(["<td>",
                                self.__create_set_field(
                                    keys[count] + "_###_" + str(line_count),
                                    value, table_name),
                                "</td>"])
                elif keys[count].find("_nbr") >= 0:
                    row.extend(["<td>",
                                self.__create_number_input_field(
                                    keys[count] + "_###_" + str(line_count),
                                    value, size=6),
                                "</td>"])
                else:
                    if keys[count].lower().find("year") >= 0 or \
                            keys[count].lower().find("cost") >= 0:
                        row.extend(
                            ["<td>",
                             self.__create_input_field(
                                 keys[count] + "_###_" + str(line_count),
                                 value,
                                 "unit"
                             ),
                             "</td>"]
                        )
                    else:
                        row.extend(
                            ["<td>",
                             self.__create_input_field(
                                 keys[count] + "_###_" + str(line_count),
                                 value,
                                 module_type
                             ),
                             "</td>"]
                        )
                count += 1
            row.append("</tr>\n")
        if self.editable:
            row.extend(["<input type='hidden' ",
                        "name='numberOf", table_name, "' ",
                        "id='numberOf", table_name, "' ",
                        "value='", str(line_count), "' />"])
        return row

    def __create_editable_row(self, key, value, table_name, itf, dual=0):
        """
        Creates a row for generic modules.
        """

        if not value:
            value = ""
        elif type(value) == bytearray:
            value = value.decode("utf-8")

        if not self.__display_key(key):
            return ""

        if not itf and key.find("_itf") >= 0:
            return ""

        row = []
        row.append("<td class='input-right'>")
        key_local = key
        if key_local.find("_enumfield") >= 0:
            row.append(self.__create_enum_field_from_table(key, value, table_name, dual=dual))
            row.append("</td>")
            row.insert(0, self.__create_label(key_local, "_enumfield"))
        elif key_local.find("_setfield") >= 0:
            row.append(self.__create_set_field(key, value, table_name, dual=dual))
            row.append("</td>")
            row.insert(0, self.__create_label(key_local, "_setfield"))
        elif key_local.find("_nbr") >= 0:
            row.append(self.__create_number_input_field(key, value, dual=dual))
            row.append("</td>")
            row.insert(0, self.__create_label(key_local, "_nbr"))
        elif key_local.find("_enum") >= 0:
            row.append(self.__create_enum_field(key, value, dual=dual))
            row.append("</td>")
            row.insert(0, self.__create_label(key_local, "_enum"))
        else:
            row.append(self.__create_input_field(key, value, "generic", dual=dual))
            row.append("</td>")
            row.insert(0, self.__create_label(key_local, "_nbr"))

        return "".join(row)

    def __create_input_field(self, key, value, row_type, dual=0):
        """
        Creates an input html element.
        """
        def get_input_text(key, value, size):
            """
            creates the input html.
            """
            if self.editable:
                return "".join(["<input type='text' name='", key,
                            "' id='", key,
                            "' value='", value,
                            "' size='", size, "' />"
                            ])
            else:
                return "".join(["<span class='searchable'>",
                                str(value),
                                "</span>"
                                ])


        value = str(value)

        if dual > 0:
            key = key + "_stn" + str(dual)
        if row_type == "unit":
            return get_input_text(key, value, "10")
        if row_type == "unit_control":
            return get_input_text(key, value, "7")
        elif row_type == "generic":
            return get_input_text(key, value, "50")
        elif row_type == "performance":
            return get_input_text(key, value, "6")
        else:
            return get_input_text(key, value, "95")

    def __create_enum_field(self, key, value, dual=0):
        """
        Creates a select html element for drop down ui.
        """
        t_name = key.replace("_enum", "")
        row = []

        columns = ["`" + t_name + "_ID`", "`" + t_name + "`"]

        result = self.resource.select.read("`" + t_name + "`", columns=columns)
        values = result.fetchall()

        if dual > 0:
            key = key + "_stn" + str(dual)
        row.extend(["<select id='", key,
                    "' name='", key, "'>"])

        for val in values:
            option_value = str(val[t_name+"_ID"])
            option_text = val[t_name]
            if option_value == str(value):
                row.extend(["<option value='", option_value,
                            "' selected='selected'>", option_text,
                            "</option>"])
            else:
                row.extend(["<option value='", option_value,
                            "'>", option_text,
                            "</option>"])

        row.append("</select>")
        return "".join(row)

    def __create_set_field(self, key, value, table_name, dual=0):
        """
        Creates a set field.
        """
        result = self.resource.select.read_column_names(table_name, where=key)

        enum_value = result[0][1].replace("set(", "")
        enum_value = enum_value[:-1]
        row = []

        if dual > 0:
            key = key + "_stn" + str(dual)
        for option in enum_value.split(","):
            option = str(option)
            option = option.replace("'", "")
            if option == value:
                row.extend(["<input type='checkbox'",
                            "name='", key, "_###_", option,
                            "' id='", key, "_###_", option,
                            "' value='", option,
                            "' selected='selected'/>", option])
            else:
                row.extend(["<input type='checkbox'",
                            "name='", key, "_###_", option,
                            "' id='", key, "_###_", option,
                            "' value='", option, "' />", option])
        return "".join(row)

    def __create_enum_field_from_table(self, key, value, table_name, dual=0):
        """
        Creates enum field for drop down menus.
        """
        db_key = key.split("_###_")[0]
        result = self.resource.select.read_column_names(table_name, where=db_key)

        # the result object is a list of tuples.
        # the tuple looks like (db_key, values)
        enum_value = result[0][1].replace("enum(", "")
        enum_value = enum_value[:-1]

        enum = []
        replace_comma = False

        for val in enum_value:
            if val == "'":
                replace_comma = True if not replace_comma else False
            #if val == "'":
            #    replace_comma = False
            if replace_comma and val == ',':
                val = "@"
            enum.append(val)

        enum = "".join(enum)

        if dual > 0:
            key = key + "_stn" + str(dual)

        row = []
        if self.editable:
            row.extend(["<select id='", key,
                        "' name='", key, "'>"])
        for option in enum.split(","):
            option = option.replace("'", "")
            option = option.replace("@", ",")
            if option == value:
                if self.editable:
                    row.extend(["<option value='", option,
                                "' selected='selected'>", option,
                                "</option>"])
                else:
                    row.extend(["<span>", option, "</span>"])
            else:
                if self.editable:
                    row.extend(["<option value='", option,
                                "'>", option, "</option>"])

        if self.editable:
            row.append("</select>")
        return "".join(row)

    def __create_number_input_field(self, key, value, size=15, dual=0):
        """
        Creates an input html element for numbers.
        """
        if not value:
            value = ""
        if dual > 0:
            key = key + "_stn" + str(dual)
        if self.editable:
            return "".join(["<input type='text' name='", key,
                            "' id='", key,
                            "' value='", str(value),
                            "' size='", str(size), "' />"
                            ])
        else:
            return "".join(["<span>",
                            str(value),
                            "</span>"
                            ])

    @staticmethod
    def __create_label(key, field_type):
        """
        Creates the label for the generic modules.
        Handles the range labels.
        """
        label = []
        key_local = key
        if key.find("_rng3") >= 0:
            key_local = key_local.split("_rng3")[1]
            key_local = "-- <i>" + key_local + "</i>"
            label.append("<td class='label_rng'>")
        elif key.find("_rng2") >= 0:
            key_local = key_local.split("_rng2")[1]
            key_local = "-- <i>" + key_local + "</i>"
            label.append("<td class='label_rng'>")
        elif key.find("_rng1") >= 0:
            temp = key.split("_rng1")
            key_local = temp[0]
            if len(temp) > 1:
                key_local += " -- <i>" + temp[1] + "</i>"
            label.append("<td class=''>")
        elif key.find("_other") >= 0:
            key_local = "-- <i>Or other</i>"
            label.append("<td class='label_rng'>")
        else:
            label.append("<td class='label_left'>")

        label.append(Html.__make_readable(key_local.replace(field_type, "")))
        label.append("</td>")
        return "".join(label)

    @staticmethod
    def __display_key(key):
        """
        Determines if a label should be displayed in the HTML representation.
        """

        return not key.find("_ID") >= 0 and not key.find("Year_yr") >= 0

    @staticmethod
    def __make_readable(token, module_type=None):
        """
        Removes the geo specific parts of a label and converts _ to " ".
        """

        reserved_words = \
            ["_itf", "_rng1", "_rng2", "_rng3", "_nbr", "_yr", "_dt", "_omit"]
        for word in reserved_words:
            token = token.replace(word, "")

        if module_type == "unit_control":
            token = token.replace("Control_", "")
            token = token.replace("Monitor_", "")

        token = token.replace("_", " ")
        return token
