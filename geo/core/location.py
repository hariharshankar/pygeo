"""
A class for all location information needs.
"""

from geo.db.query import Select
from geo.core.geo_resource import GeoResource
from geo.core.main import Main
from geo.core.moderation import Moderation


class Location(object):
    """
    A class for all the location information.
    """

    def __init__(self, connection):
        self.connection = connection
        self.select = Select(self.connection)
        self.main = Main(self.connection)

    def __get_lat_lng(self, table_name, description_id):
        """
        A private class to get lat and lng for a resource.
        """

        result = self.select.read(table_name,
                                  where=[["Description_ID",
                                          "=",
                                          description_id]]
                                  )
        if not result.with_rows:
            return (None, None)

        loc = result.fetchone()
        lat = loc['Latitude_Start']
        lng = loc['Longitude_Start']
        lat_end = loc['Latitude_End']
        lng_end = loc['Longitude_End']

        return (lat, lng), (lat_end, lng_end)

    def for_one_resource(self, description_id):
        """
        Returns the location for a resource.

        :@param description_id
        :@returns dict: {lat, lng, overlays}
        """

        gresource = GeoResource(self.connection, description_id)

        type_id = gresource.type_id
        type_name = self.main.get_type_name(type_id)

        (lat, lng), (lat_end, lng_end) = self.__get_lat_lng(type_name + "_Location", description_id)

        overlay_result = self.select.read(type_name + "_Overlays",
                                          where=[["Description_ID",
                                                  "=",
                                                  description_id]]
                                          )

        o_results = overlay_result.fetchall()
        overlays = []

        for overlay in o_results:
            details = {}
            details['color'] = overlay['Color']
            details['weight'] = overlay['Weight']
            details['opacity'] = overlay['Opacity']
            details['points'] = overlay['Points']
            details['numLevels'] = overlay['Num_Levels']
            details['zoomFactor'] = overlay['Zoom_Factor']
            details['overlayType'] = overlay['Overlay_Type']
            details['overlayName'] = overlay['Overlay_Name']
            overlays.append(details)

        locations = {}
        locations['lat'] = lat
        locations['lng'] = lng
        if lat_end and lng_end:
            locations['lat_end'] = lat_end
            locations['lng_end'] = lng_end
        locations['name'] = gresource.get_resource_name(type_name)
        locations['overlays'] = overlays
        return {"locations": [locations]}

    def for_many_resources(self, country_id=None, type_id=None):
        """
        Returns the location information for all the resources
        in a country for the type.

        :@param country: the country id
        :@param typ: type id
        """

        if int(country_id) <= 0 or int(type_id) <= 0:
            return {}

        moderation = Moderation(self.connection)
        keys, values = moderation.get_all_resources(country_id=country_id, type_id=type_id)
        del keys

        table_name = self.main.get_type_name(type_id) + "_Location"

        loc = []
        locations = self.select.read(table_name,
                                     columns=["Description_ID",
                                              "Latitude_Start",
                                              "Longitude_Start"],
                                     where=[["Description_ID",
                                             "in",
                                             [value[0] for value in values]]],
                                     dict_cursor=False)

        locations = locations.fetchall()

        for value in values:
            for location in locations:
                if value[0] == location[0]:
                    loc.append([location[1],
                                location[2],
                                value[1]
                                ])
        """
        lat = loc['Latitude_Start']
        lng = loc['Longitude_Start']
        for value in values:
            desc_id = value[0]
            name = value[1]

            lat, lng = self.__get_lat_lng(table_name, desc_id)
            loc.append([lat, lng, name])
        """
        return {"locations": loc, "boundLocation":
                self.main.get_country_name(country_id)}
