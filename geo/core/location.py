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
        if not result.returns_rows:
            return (None, None)

        loc = result.first()
        lat = loc['Latitude_Start']
        lng = loc['Longitude_Start']

        return lat, lng

    def for_one_resource(self, description_id):
        """
        Returns the location for a resource.

        :@param description_id
        :@returns dict: {lat, lng, overlays}
        """

        gresource = GeoResource(self.connection, description_id)

        type_id = gresource.type_id
        type_name = self.main.get_type_name(type_id)

        lat, lng = self.__get_lat_lng(type_name + "_Location", description_id)

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
        locations['name'] = gresource.get_resource_name(type_name)
        locations['overlays'] = overlays
        return {"locations": [locations]}

    def for_many_resources(self, country=None, typ=None):
        """
        Returns the location information for all the resources
        in a country for the type.

        :@param country: the country id/name
        :@param typ: type id/name
        """

        moderation = Moderation(self.connection)
        keys, values = moderation.get_all_resources(country=country, typ=typ)
        del keys

        type_id = self.main.get_type_id(typ)
        country_id = self.main.get_country_id(country)

        table_name = self.main.get_type_name(type_id) + "_Location"

        loc = []
        for value in values:
            desc_id = value[0]
            name = value[1]

            lat, lng = self.__get_lat_lng(table_name, desc_id)
            loc.append([lat, lng, name])

        return {"locations": loc, "boundLocation":
                self.main.get_country_name(country_id)}
