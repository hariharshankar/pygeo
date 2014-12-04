"""
Builds the HTML representation for the fact sheets.
"""


class Html(object):
    """
    Builds the HTML representation for the fact sheets.
    """

    def __init__(self):
        self.description_id = 0
        self.select = None
        self.type_id = 0
        self.state_id = 0
        self.country_id = 0
        self.type_name = None

    def generate_editable(self):
        """
        Creates an html form using the resource data.
        """

        html = []
        #if int(self.description_id) > 0:
        html = self.__generate_resource_modules()

        return html

    def __generate_resource_modules(self):
        """
        Handles creating the appropriate module representation.
        """

        res_modules = self.select.read("Type_Features",
                                       where=[["Type_ID", "=", self.type_id]]
                                       )
        modules = res_modules.first()
        module_names = []
        full_feature_list = self.select.read_column_names("Type_Features", where='Features')[0][1]

        if type(modules.Features) == str:
            module_names = modules.Features.split(',')
        else:
            full_feature_list = full_feature_list.replace("set(", "")
            full_feature_list = full_feature_list.replace(")", "")
            full_feature_list = full_feature_list.replace("\"", "")
            full_feature_list = full_feature_list.replace("'", "")

            module_names = [str(module)
                            for module in full_feature_list.split(",")
                            if module in modules.Features]

        html = []

        for module in module_names:
            module_id = module
            module_heading = Html.__make_readable(module)

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

        if feature.startswith("Unit_"):
            return "single-row-module", self.__make_unit_module(feature)
        elif feature.startswith("Location"):
            return "generic-module", self.__make_location_module()
        elif feature.startswith("Annual_Performance"):
            return "generic-module", self.__make_performance_module()
        elif feature.startswith("Identifiers"):
            return "generic-module", self.__make_identifiers_module()
        elif feature.startswith("Environmental_Issues")\
                or feature.startswith("Comments") \
                or feature.startswith("References") \
                or feature.startswith("Upgrades"):
            return "single-row-module", self.__make_single_row_module(feature)
        elif feature.startswith("Owner_Details"):
            owner = []
            owner.append(self.__make_generic_module(feature))
            owner.append(self.__make_single_row_module("Owners"))
            return "single-row-module", "".join(owner)
        elif feature.startswith("Associated_Infrastructure") or \
                feature.startswith("History"):
            return "", ""
        else:
            return "generic-module", self.__make_generic_module(feature)

    def __make_generic_module(self, feature):
        """
        Builds the generic module representation,
        like description module.
        """

        html = []
        table_name = self.type_name + "_" + feature
        result = self.select.read(table_name,
                                  where=[["Description_ID",
                                          "=",
                                          self.description_id]]
                                  )

        keys = result.keys()
        values = result.first()
        if not values:
            values = dict((k, None) for k in keys)

        html.append("<table>")
        for k in keys:
            html.append("<tr>")
            html.append(self.__create_editable_row(k,
                                                   values[k],
                                                   table_name,
                                                   False)
                        )
            html.append("</tr>")
        html.append("</table>")

        return "".join(html)

    def __make_single_row_module(self, feature):
        """
        Builds multi column modules like unit description.
        """

        table_name = self.type_name + "_" + feature
        result = self.select.read(table_name,
                                  where=[["Description_ID",
                                         "=",
                                         self.description_id]]
                                  )
        keys = result.keys()
        values = result.fetchall()

        html = []
        html.append("<table>")
        html.append(self.__create_spreadsheet_row(keys, values, table_name,
                                                  module_type=feature))
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
        html.extend(["<input type='hidden'",
                    "name='map_json'",
                    "id='map_json'",
                    "value='/location?description_id="
                     + str(self.description_id) + "'",
                     "class='widget_urls' />"])
        return "".join(html)

    def __make_identifiers_module(self):
        """
        Makes the identifier module.
        """

        table_name = self.type_name + "_Description"
        result = self.select.read(table_name,
                                  where=[["Description_ID",
                                         "=",
                                         self.description_id]]
                                  )

        keys = result.keys()
        values = result.first()
        if not values:
            values = dict((k, None) for k in keys)
        html = []
        html.extend(["<input type='hidden'",
                    "name='Description_ID'",
                    "id='Description_ID'",
                    "value='" + str(self.description_id) + "'",
                     "/>"
                     ])
        html.extend(["<input type='hidden'",
                    "name='Type_ID'",
                    "id='Type_ID'",
                    "value='" + str(self.type_id) + "'",
                     "/>"
                     ])
        html.extend(["<input type='hidden'",
                    "name='Country_ID'",
                    "id='Country_ID'",
                    "value='" + str(self.country_id) + "'",
                     "/>"
                     ])
        html.extend(["<input type='hidden'",
                    "name='State_ID'",
                    "id='State_ID'",
                    "value='" + str(self.state_id) + "'",
                     "/>"
                     ])
        html.extend(["<input type='hidden'",
                     "name='Type_Name'",
                     "id='Type_Name'",
                     "value='" + self.type_name + "'",
                     "/>"
        ])
        html.append("<table>")

        for k in keys:
            if k == "Name_omit" or k.find("_itf") >= 0:
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

        keys = []
        values = []

        table_name = self.type_name + "_Performance"
        result = self.select.read(table_name,
                                  where=[["Description_ID",
                                         "=",
                                         self.description_id]]
                                  )

        keys.extend(result.keys())
        values.extend(result.fetchall())

        """
        if self.type_id == 5:
            cap_gen_table_name = "Nuclear_Capacity_Generated"
            gwh_table_name = "Nuclear_Gigawatt_Hours_Generated"

            cap_gen_result = self.select.read(cap_gen_table_name,
                                              columns=["Unit_Description_ID", "Year_yr", "Capacity_Generated_nbr"],
                                              where=[["Description_ID",
                                                      "=",
                                                      self.description_id]],
                                              order_by=["Unit_Description_ID", "asc"]
            )
            cap_gen_values = cap_gen_result.fetchall()

            print(cap_gen_values)

            year_index = None
            key_count = 0
            for key in keys:
                if key == "Year_yr":
                    year_index = key_count
                    break
                elif not year_index:
                    key_count += 1
            yfound = []

            cap_val = {}
            for val in values:
                for cap_gen_val in cap_gen_values:
                    if val[year_index] == cap_gen_val[1]:
                        #yfound.append(val[year_index])
                        val.insert(year_index+1, cap_gen_val[2])

            print(cap_gen_values)
            unit_no = 0
            for cap_gen_val in cap_gen_values:
                if cap_gen_val[1] not in yfound:
                    if not cap_val.get(cap_gen_val[1]):
                        cap_val[cap_gen_val[1]] = []
                        for key in keys:
                            cap_val[cap_gen_val[1]].append(None)
                        #year
                        cap_val[cap_gen_val[1]].insert(year_index, cap_gen_val[1])
                        cap_val[cap_gen_val[1]].insert(year_index+1, cap_gen_val[2])
                        keys.insert(year_index+1, cap_gen_result.keys()[2])
                        unit_no += 1
                    else:
                        unit_no += 1
                        cap_val[cap_gen_val[1]].insert(year_index+unit_no, cap_gen_val[2])
            for cv in cap_val:
                print(cap_val[cv])
                values.append(cap_val[cv])

            gwh_result = self.select.read(gwh_table_name,
                                          where=[["Description_ID",
                                                  "=",
                                                  self.description_id]]
            )
            keys.extend(gwh_result.keys())
            values.extend(gwh_result.fetchall())

        """
        #print(keys)
        #print(values)

        html = []
        html.append(self.__create_performance_table(keys, values))
        return "".join(html)

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

    def __make_unit_module(self, feature):
        """
        Builds the unit description module.
        """

        html = []
        table_name = self.type_name + "_" + feature
        result = self.select.read(table_name,
                                  where=[["Description_ID",
                                         "=",
                                         self.description_id]]
                                  )
        keys = result.keys()
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
                self.type_name + "_" + feature,
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
                    self.type_name + "_" + feature,
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
            if key.find('Year_rng1') >= 0:
                key = key.replace("Year_rng1", "Year_From_rng1")
            if key.find('Year_rng2') >= 0:
                key = key.replace("Year_rng2_-", "Year_To_rng2")
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
            row.extend(["<td><input type='checkbox'",
                        "id='", table_name, "_###_", str(line_count),
                        "' name='", table_name, "_###_", str(line_count),
                        "'></td>"])
            line_count += 1
            row.extend(["<td>", str(line_count), "</td>"])
            for value in val:
                if not self.__display_key(keys[count]):
                    count += 1
                    continue

                if not value:
                    value = ""
                else:
                    value = str(value)

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
        row.extend(["<input type='hidden'",
                    "name='numberOf", table_name, "'",
                    "value='", str(line_count), "' />"])
        return row

    def __create_editable_row(self, key, value, table_name, itf):
        """
        Creates a row for generic modules.
        """

        if not value:
            value = ""

        if not self.__display_key(key):
            return ""

        if not itf and key.find("_itf") >= 0:
            return ""

        row = []
        row.append("<td class='input-right'>")
        key_local = key
        if key_local.find("_enumfield") >= 0:
            row.append(self.__create_enum_field_from_table(key, value, table_name))
            row.append("</td>")
            row.insert(0, self.__create_label(key_local, "_enumfield"))
        elif key_local.find("_setfield") >= 0:
            row.append(self.__create_set_field(key, value, table_name))
            row.append("</td>")
            row.insert(0, self.__create_label(key_local, "_setfield"))
        elif key_local.find("_nbr") >= 0:
            row.append(self.__create_number_input_field(key, value))
            row.append("</td>")
            row.insert(0, self.__create_label(key_local, "_nbr"))
        elif key_local.find("_enum") >= 0:
            row.append(self.__create_enum_field(key, value))
            row.append("</td>")
            row.insert(0, self.__create_label(key_local, "_enum"))
        else:
            row.append(self.__create_input_field(key, value, "generic"))
            row.append("</td>")
            row.insert(0, self.__create_label(key_local, "_nbr"))

        return "".join(row)

    @staticmethod
    def __create_input_field(key, value, row_type):
        """
        Creates an input html element.
        """
        def get_input_text(key, value, size):
            """
            creates the input html.
            """
            return "".join(["<input type='text' name='", key,
                            "' id='", key,
                            "' value='", value,
                            "' size='", size, "' />"
                            ])


        value = str(value)

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

    def __create_enum_field(self, key, value):
        """
        Creates a select html element for drop down ui.
        """
        t_name = key.replace("_enum", "")
        row = []

        columns = ["`" + t_name + "_ID`", "`" + t_name + "`"]

        result = self.select.read("`" + t_name + "`", columns=columns)
        values = result.fetchall()

        row.extend(["<select id='", key,
                    "' name='", key, "'>"])

        for val in values:
            option_value = str(val[0])
            option_text = val[1]
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

    def __create_set_field(self, key, value, table_name):
        """
        Creates a set field.
        """
        result = self.select.read_column_names(table_name, where=key)

        enum_value = result[0][1].replace("set(", "")
        enum_value = enum_value[:-1]
        row = []

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

    def __create_enum_field_from_table(self, key, value, table_name):
        """
        Creates enum field for drop down menus.
        """
        db_key = key.split("_###_")[0]
        result = self.select.read_column_names(table_name, where=db_key)

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

        row = []
        row.extend(["<select id='", key,
                    "' name='", key, "'>"])
        for option in enum.split(","):
            option = option.replace("'", "")
            option = option.replace("@", ",")
            if option == value:
                row.extend(["<option value='", option,
                            "' selected='selected'>", option,
                            "</option>"])
            else:
                row.extend(["<option value='", option,
                            "'>", option, "</option>"])

        row.append("</select>")
        return "".join(row)

    @staticmethod
    def __create_number_input_field(key, value, size=15):
        """
        Creates an input html element for numbers.
        """
        return "".join(["<input type='text' name='", key,
                        "' id='", key,
                        "' value='", str(value),
                        "' size='", str(size), "' />"
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
