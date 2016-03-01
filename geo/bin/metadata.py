#! /usr/bin/env python

__author__ = 'harihar'

import sys
import os
import json
import math

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from geo.db.query import Select
from geo.db import connection
from geo.core.main import Main
from geo.core.moderation import Moderation


class Metadata(object):
    """
    Computes the values and updates the metadata table.
    This table provides summary info for the views.
    """

    def __init__(self):
        self.conn = connection.Db().session
        self.main = Main(connection.Db())
        self.moderation = Moderation(connection.Db())
        self.select = Select(connection.Db())

        self.perf_fields = ("_Performance", "Year_yr",
                       ["Total_Gigawatt_Hours_Generated_nbr", "CO2_Emitted_(Tonnes)_nbr"])
        self.unit_fields = ("_Unit_Description", "Date_Commissioned_dt", "Capacity_(MWe)_nbr")

        self.alt_types = [4, 7, 8, 10]
        self.alt_perf_fields = ("_Performance", "Year_yr",
                           ["Total_Gigawatt_Hours_Generated_nbr", "Plant_Load_Factor_(%)_nbr"])

        self.nuclear_perf_fields = ("_Performance", "Year_yr",
                                ["Plant_Load_Factor_(%)_nbr"])
        self.nuclear_ghg_fields = ("_Gigawatt_Hours_Generated", "Year_yr",
                                   ["Gigawatt_Hours_Generated_nbr"])
        self.wind_unit_fields = ("_Unit_Description", "Date_Commissioned_dt",
                                 "Peak_MWe_per_Turbine_nbr", "Number_Of_Turbines_nbr")

    def get_unit_data(self, typ, plants):
        # units
        results = self.select.read(typ[1] + self.unit_fields[0],
                            columns=["`" + self.unit_fields[1] + "`",
                                     "`" + self.unit_fields[2] + "`", "Description_ID"],
                            where=[["Description_ID", "in",
                                    [plant[0] for plant in plants]]],
                                 dict_cursor=False)
        units = results.fetchall()
        cumulative_capacity_total = 0
        cumulative_capacity = {}
        new_capacity = {}
        new_capacity['keys'] = [self.unit_fields[1], self.unit_fields[2]]
        cumulative_capacity['keys'] = [self.unit_fields[1], self.unit_fields[2]]
        cap_values = {}
        cum_cap_values = {}
        for unit in units:
            if not unit[1] or not unit[0]:
                continue

            unit_val = math.ceil(float(unit[1]))
            cumulative_capacity_total += unit_val

            year = unit[0].decode("utf8")
            val = cap_values.get(year, -1)
            if val == -1:
                cap_values[year] = 0
            cap_values[year] += unit_val

        prev_year = 0
        for year in sorted(cap_values.keys()):
            cum_cap_values[year] = cap_values[year] + cum_cap_values.get(prev_year, 0)
            prev_year = year

        new_capacity['values'] = sorted([list(values) for values in
                                         zip(cap_values.keys(),
                                             cap_values.values())]
                                        )
        cumulative_capacity['values'] = sorted([list(values) for values in
                                         zip(cum_cap_values.keys(),
                                             cum_cap_values.values())]
        )

        return cumulative_capacity_total, cumulative_capacity, new_capacity

    def get_wind_unit_data(self, typ, plants):
        # units
        results = self.select.read(typ[1] + self.wind_unit_fields[0],
                                 columns=["`" + self.wind_unit_fields[1] + "`",
                                          "`" + self.wind_unit_fields[2] + "`",
                                          "`" + self.wind_unit_fields[3] + "`"],
                                 where=[["Description_ID", "in",
                                         [plant[0] for plant in plants]]],
                                 dict_cursor=False)
        units = results.fetchall()
        cumulative_capacity_total = 0
        new_capacity = {}
        new_capacity['keys'] = [self.unit_fields[1], self.unit_fields[2]]
        cap_values = {}
        for unit in units:
            if not unit[1] or not unit[0]:
                continue

            unit_val = math.ceil(float(unit[1]))
            cumulative_capacity_total += unit_val

            year = unit[0].decode("utf8")
            val = cap_values.get(year, -1)
            if val == -1:
                cap_values[year] = 0
            if unit[2] and float(unit[2]):
                cap_values[year] += unit_val * math.ceil(float(unit[2]))

        cum_cap_values = {}
        prev_year = 0
        for year in sorted(cap_values.keys()):
            cum_cap_values[year] = cap_values[year] + cum_cap_values.get(prev_year, 0)
            prev_year = year

        new_capacity['values'] = sorted([list(values) for values in
                                         zip(cap_values.keys(),
                                             cap_values.values())])

        cumulative_capacity = {}
        cumulative_capacity['values'] = sorted([list(values) for values in
                                                zip(cum_cap_values.keys(),
                                                    cum_cap_values.values())]
        )

        return cumulative_capacity_total, cumulative_capacity, new_capacity

    def get_general_performance_data(self, typ, plants):
        # performance
        cols = [self.perf_fields[1]]
        if typ[0] in self.alt_types:
            cols.extend(["`" + p_col + "`" for p_col in self.alt_perf_fields[2]])
        else:
            cols.extend(["`" + p_col + "`" for p_col in self.perf_fields[2]])

        results = self.select.read(typ[1] + self.perf_fields[0],
                                   columns=cols,
                                   where=[["Description_ID", "in",
                                           [plant[0] for plant in plants]]],
                                        dict_cursor=False)
        performances = results.fetchall()
        co2 = {}
        ghg = {}
        for perf in performances:
            year = str(perf[0])

            if perf[1]:
                g_val = ghg.get(year, -1)
                if g_val == -1:
                    ghg[year] = 0
                ghg[year] += math.ceil(float(perf[1]))

            if perf[2]:
                c_val = co2.get(year, -1)
                if c_val == -1:
                    co2[year] = 0
                co2[year] += math.ceil(float(perf[2]))

        # for plotting purposes, the years in both the dicts must
        # be the same. so adding zeros to missing years.
        for year in co2.keys():
            val = ghg.get(year, -1)
            if val == -1:
                ghg[year] = 0

        for year in ghg.keys():
            val = co2.get(year, -1)
            if val == -1:
                co2[year] = 0

        ghg_values = {"keys": [self.perf_fields[1], self.perf_fields[2][0]],
                      "values": sorted([list(values)
                                        for values in zip(ghg.keys(),
                                                          ghg.values())]
                                       )}

        co2_values = {"keys": [self.perf_fields[1], self.perf_fields[2][1]],
                      "values": sorted([list(values) for values in
                                        zip(co2.keys(), co2.values())])}

        return ghg_values, co2_values

    def get_nuclear_performance_data(self, typ, plants):
        # performance
        cols = [self.perf_fields[1]]
        cols.append("`" + self.nuclear_ghg_fields[2][0] + "`")
        ghg_res = self.select.read(typ[1] + self.nuclear_ghg_fields[0],
                                        columns=cols,
                                        where=[["Description_ID", "in",
                                                [plant[0] for plant in plants]]],
                                    dict_cursor=False)

        ghg_perf = ghg_res.fetchall()
        cols = [self.perf_fields[1]]
        cols.append("`" + self.nuclear_perf_fields[2][0] + "`")
        reg_res = self.select.read(typ[1] + self.nuclear_perf_fields[0],
                                    columns=cols,
                                    where=[["Description_ID", "in",
                                            [plant[0] for plant in plants]]],
                                    dict_cursor=False)
        reg_perf = reg_res.fetchall()
        co2 = {}
        ghg = {}
        for perf in ghg_perf:
            year = str(perf[0])

            if perf[1]:
                g_val = ghg.get(year, -1)
                if g_val == -1:
                    ghg[year] = 0
                ghg[year] += math.ceil(float(perf[1]))

        for perf in reg_perf:
            if perf[1]:
                c_val = co2.get(year, -1)
                if c_val == -1:
                    co2[year] = 0
                co2[year] += math.ceil(float(perf[1]))

        # for plotting purposes, the years in both the dicts must
        # be the same. so adding zeros to missing years.
        for year in co2.keys():
            val = ghg.get(year, -1)
            if val == -1:
                ghg[year] = 0

        for year in ghg.keys():
            val = co2.get(year, -1)
            if val == -1:
                co2[year] = 0

        ghg_values = {"keys": [self.nuclear_ghg_fields[1], self.nuclear_ghg_fields[2][0]],
                      "values": sorted([list(values) for values in
                                        zip(ghg.keys(), ghg.values())]
                                       )}

        co2_values = {"keys": [self.nuclear_perf_fields[1], self.nuclear_perf_fields[2][0]],
                      "values": sorted([list(values) for values in
                                        zip(co2.keys(), co2.values())]
                                       )}
        return ghg_values, co2_values

    def compute(self):
        t_keys, types = self.main.get_types("PowerPlants")
        #types = [[1, "Coal"]]
        session = self.conn.cursor()
        for typ in types:
            c_keys, countries = self.main.get_countries(typ[0])
            #countries = [[38, "Canada"]]

            for country in countries:
                p_keys, plants = self.moderation.get_all_resources(country_id=country[0], type_id=typ[0])

                # unit data
                if typ[0] == 10:
                    cumulative_capacity_total, cumulative_capacity, new_capacity = self.get_wind_unit_data(typ, plants)
                else:
                    cumulative_capacity_total, cumulative_capacity, new_capacity = self.get_unit_data(typ, plants)

                # perf data
                if typ[0] == 5:
                    ghg, co2 = self.get_nuclear_performance_data(typ, plants)
                else:
                    ghg, co2 = self.get_general_performance_data(typ, plants)

                sql = "INSERT INTO metadata SET Country_ID=%(country_id)s, \
                 Type_ID=%(type_id)s, Number_of_Plants=%(number_of_plants)s, \
                 Cumulative_Capacity=%(cum_cap)s, \
                 Cumulative_Capacity_Total=%(cum_cap_tot)s, New_Capacity_Added=%(new_cap)s, \
                 Annual_Gigawatt_Hours_Generated=%(ghg)s, Annual_CO2_Emitted=%(co2)s"

                session.execute(sql, {
                    "country_id": country[0],
                    "type_id": typ[0],
                    "number_of_plants": str(len(plants)),
                    "cum_cap": json.dumps(cumulative_capacity),
                    "cum_cap_tot": str(cumulative_capacity_total),
                    "new_cap": json.dumps(new_capacity),
                    "ghg": json.dumps(ghg),
                    "co2": json.dumps(co2)
                })
                self.conn.commit()
        session.close()

if __name__ == "__main__":
    m = Metadata()
    m.compute()