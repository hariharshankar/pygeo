
class Html():

    def generate_editable(self):
        """
        Creates an html form using the resource data.
        """

        html = []
        if self.description_id > 0:
            html = self.__generate_resource_modules()

        #FIXME create similar page for users
        return html

    def __generate_resource_modules(self):

        res_modules = self.select.read("Type_Features",
                                       where=[["Type_ID", "=", self.type_id]]
                                       )
        modules = res_modules.first()

        html = []

        for m in modules.Features.split(","):
            module_id = m
            module_heading = self.__make_readable(m)

            module_header_class, module_content = \
                self.__get_module_for_feature(m)

            if module_content:
                html.append(
                    {"module_heading": module_heading,
                     "module_id": module_id,
                     "module_header_class": module_header_class,
                     "module_content": module_content
                     }
                )

        return html

    def __make_readable(self, token):

        reserved_words = \
            ["_itf", "_rng1", "_rng2", "_rng3", "_nbr", "_yr", "_dt"]
        for r in reserved_words:
            token = token.replace(r, "")

        token = token.replace("_", " ")
        return token

    def __get_module_for_feature(self, feature):

        if feature.startswith("Unit_"):
            return "single-row-module", self.__make_unit_module(feature)
        elif feature.startswith("Location"):
            return "generic-module", self.__make_location_module(feature)
        elif feature.startswith("Annual_Performance"):
            return "generic-module", self.__make_performance_module(feature)
        elif feature.startswith("Identifiers"):
            return "generic-module", self.__make_identifiers_module(feature)
        elif feature.startswith("Environmental_Issues")\
                or feature.startswith("Comments") \
                or feature.startswith("References") \
                or feature.startswith("Upgrades"):
            return "single-row-module", self.__make_single_row_module(feature)
        elif feature.startswith("Owner_Details"):
            h = []
            h.append(self.__make_single_row_module("Owners"))
            h.append(self.__make_generic_module(feature))
            return "single-row-module", "".join(h)
        elif feature.startswith("Associated_Infrastructure") or \
                feature.startswith("History"):
            return "", ""
        else:
            return "generic-module", self.__make_generic_module(feature)

    def __make_generic_module(self, feature):

        html = []
        table_name = self.type_name + "_" + feature
        result = self.select.read(table_name,
                                  where=[["Description_ID",
                                          "=",
                                          self.description_id]]
                                  )

        keys = result.keys()
        values = result.first()

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

    def __make_location_module(self, feature):
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

    def __make_identifiers_module(self, feature):
        table_name = self.type_name + "_Description"
        result = self.select.read(table_name,
                                  where=[["Description_ID",
                                         "=",
                                         self.description_id]]
                                  )

        keys = result.keys()
        values = result.first()
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

    def __make_performance_module(self, feature):
        table_name = self.type_name + "_Performance"
        result = self.select.read(table_name,
                                  where=[["Description_ID",
                                         "=",
                                         self.description_id]]
                                  )

        keys = result.keys()
        values = result.fetchall()

        html = []
        html.append(self.__create_performance_table(keys, values))
        return "".join(html)

    def __make_unit_module(self, feature):
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
                control_keys.append(k)

        unit_count = 0
        for v in values:
            unit_values.append(v[0:len(unit_keys)])
            unit_count += 1

        control_count = 0
        for v in values:
            control_values.append(v[len(unit_keys):len(keys)])
            control_count += 1

        html.append("<table>")
        html.append(
            self.__create_spreadsheet_row(
                unit_keys,
                unit_values,
                self.type_name + "_" + feature,
                "unit")
        )
        html.append("</table>")
        html.append("<table>")
        html.append(
            self.__create_spreadsheet_row(
                control_keys,
                control_values,
                self.type_name + "_" + feature,
                "unit")
        )
        html.append("</table>")
        return "".join(html)

    def __create_label(self, key, field_type):
        r = []
        k = key
        if key.find("_rng3") >= 0:
            k = k.split("_rng3")[1]
            k = "-- <i>" + k + "</i>"
            r.append("<td class='label_rng'>")
        elif key.find("_rng2") >= 0:
            k = k.split("_rng2")[1]
            k = "-- <i>" + k + "</i>"
            r.append("<td class='label_rng'>")
        elif key.find("_rng1") >= 0:
            t = key.split("_rng1")
            k = t[0]
            if len(t) > 1:
                k += " -- <i>" + t[1] + "</i>"
            r.append("<td class=''>")
        elif key.find("_other") >= 0:
            k = "-- <i>Or other</i>"
            r.append("<td class='label_rng'>")
        else:
            r.append("<td class='label_left'>")

        r.append(self.__make_readable(k.replace(field_type, "")))
        r.append("</td>")
        return "".join(r)

    def __display_key(self, key):
        return not key.find("_ID") >= 0 and not key.find("Year_yr") >= 0

    def __create_spreadsheet_row(self, keys, values, table_name,
                                 module_type=None):
        row = []
        row.append("<tr>")

        # check box heading
        row.append("<th></th>")

        if table_name.find("Owners") >= 0:
            row.append("<th>Owner #</th>")
        else:
            row.append("<th>#</th>")

        null_vals = []
        for k in keys:
            null_vals.append(None)
            if self.__display_key(k):
                row.append("<th>" + self.__make_readable(k) + "</th>")

        if not values:
            values = []
            values.append(null_vals)
        elif len(values) == 0:
            values.append(null_vals)

        row.append("</tr>")

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
            for v in val:
                if not self.__display_key(keys[count]):
                    count += 1
                    continue

                if not v:
                    v = ""
                else:
                    v = str(v)

                if keys[count].find("_enumfield") >= 0:
                    row.extend(["<td>",
                                self.__create_enum_field(
                                    keys[count] + "_###_" + str(line_count),
                                    v,
                                    table_name),
                                "</td>"])
                elif keys[count].find("_setfield") >= 0:
                    row.extend(["<td>",
                                self.__create_set_field(
                                    keys[count] + "_###_" + str(line_count),
                                    v, table_name),
                                "</td>"])
                elif keys[count].find("_nbr") >= 0:
                    row.extend(["<td>",
                                self.__create_number_input_field(
                                    keys[count] + "_###_" + str(line_count),
                                    v, size=6),
                                "</td>"])
                else:
                    if keys[count].lower().find("year") >= 0 or \
                            keys[count].lower().find("cost") >= 0:
                        row.extend(
                            ["<td>",
                             self.__create_input_field(
                                 keys[count] + "_###_" + str(line_count),
                                 v,
                                 "unit"
                             ),
                             "</td>"]
                        )
                    else:
                        row.extend(
                            ["<td>",
                             self.__create_input_field(
                                 keys[count] + "_###_" + str(line_count),
                                 v,
                                 module_type
                             ),
                             "</td>"]
                        )
                count += 1
            row.append("</tr>\n")

        row.append("</tr>")
        row.extend(["<input type='hidden'",
                    "name='numberOf", table_name, "'",
                    "value='", str(line_count), "' />"])
        return "".join(row)

    def __create_editable_row(self, key, value, table_name, itf):

        if not value:
            value = ""

        if not self.__display_key(key):
            return ""

        if not itf and key.find("_itf") >= 0:
            return ""

        row = []
        row.append("<td class='input-right'>")
        k = key
        if k.find("_enumfield") >= 0:
            row.append(self.__create_enum_field(key, value, table_name))
            row.append("</td>")
            row.insert(0, self.__create_label(k, "_enumfield"))
        elif k.find("_setfield") >= 0:
            row.append(self.__create_set_field(key, value, table_name))
            row.append("</td>")
            row.insert(0, self.__create_label(k, "_setfield"))
        elif k.find("_nbr") >= 0:
            row.append(self.__create_number_input_field(key, value))
            row.append("</td>")
            row.insert(0, self.__create_label(k, "_nbr"))
        elif k.find("_enum") >= 0:
            row.append(self.__create_enum_from_table(key, value, table_name))
            row.append("</td>")
            row.insert(0, self.__create_label(k, "_enum"))
        else:
            row.append(self.__create_input_field(key, value, "generic"))
            row.append("</td>")
            row.insert(0, self.__create_label(k, "_nbr"))

        return "".join(row)

    def __create_input_field(self, key, value, row_type):

        value = str(value)

        if row_type == "unit":
            return "".join(["<input type='text' name='", key,
                            "' id='", key,
                            "' value='", value,
                            "' size='6' />"
                            ])
        elif row_type == "generic":
            return "".join(["<input type='text' name='", key,
                            "' id='", key,
                            "' value='", value,
                            "' size='50' />"
                            ])
        elif row_type == "performance":
            return "".join(["<input type='text' name='", key,
                            "' id='", key,
                            "' value='", value,
                            "' size='6' />"
                            ])
        else:
            return "".join(["<input type='text' name='", key,
                           "' id='", key,
                           "' value='", value,
                           "' size='85' />"])

    def __create_enum_from_table(self, key, value, table_name):
        t_name = key.replace("_enum", "")
        row = []

        columns = ["`" + t_name + "_ID`", "`" + t_name + "`"]

        result = self.select.read("`" + t_name + "`", columns=columns)
        values = result.fetchall()

        row.extend(["<select id='", key,
                    "' name='", key, "'>"])

        for v in values:
            option_value = str(v[0])
            option_text = v[1]
            if option_value == value:
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

    def __create_enum_field(self, key, value, table_name):
        db_key = key.split("_###_")[0]
        result = self.select.read_column_names(table_name, where=db_key)

        # the result object is a list of tuples.
        # the tuple looks like (db_key, values)
        enum_value = result[0][1].replace("enum(", "")
        enum_value = enum_value[:-1]

        enum = []
        replace_comma = False

        for c in enum_value:
            if c == '(':
                replace_comma = True
            if c == ')':
                replace_comma = False
            if replace_comma and c == ',':
                c = "@"
            enum.append(c)

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

    def __create_number_input_field(self, key, value, size=11):
        return "".join(["<input type='text' name='", key,
                        "' id='", key,
                        "' value='", str(value),
                        "' size='", str(size), "' />"
                        ])

    def __create_performance_table(self, keys, values):

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

        for k in keys:
            if self.__display_key(k):
                if row_count % 2 == 0:
                    table.append("<tr class='perf-row even-row'>")
                else:
                    table.append("<tr class='perf-row odd-row'>")
                table.append("<th>" + self.__make_readable(k) + "</th>")
                table.append("</tr>")
                row_count += 1

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
        for k in keys:
            year_index = 1
            if k == "Year_yr":
                year_index = key_count

            if self.__display_key(k):
                if row_count % 2 == 0:
                    table.append("<tr class='perf-row even-row'>")
                else:
                    table.append("<tr class='perf-row odd-row'>")

                for year in range(decade_start, decade_end):
                    for v in values:
                        if v[year_index] == str(year):
                            break

                    value = ""
                    value = v[key_count]
                    if not value:
                        value = ""

                    table.append(
                        "<td>" +
                        self.__create_input_field(
                            k + "_###_" + str(year), value, "performance"
                        ) +
                        "</td>"
                    )

                table.append("</tr>\n")
                row_count += 1
            key_count += 1

        table.append("</table>")
        table.append("</td>")
        table.append("</tr>")
        table.append("</table>")

        return "".join(table)
