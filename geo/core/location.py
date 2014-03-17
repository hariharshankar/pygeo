from geo.db.query import Select
from geo.core.geo_resource import GeoResource
from geo.core.main import Main
from geo.core.moderation import Moderation


class Location():

    def __init__(self, connection):
        self.connection = connection
        self.select = Select(self.connection)
        self.main = Main(self.connection)

    def __get_lat_lng(self, table_name, description_id):
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

        for o in o_results:
            details = {}
            details['color'] = o['Color']
            details['weight'] = o['Weight']
            details['opacity'] = o['Opacity']
            details['points'] = o['Points']
            details['numLevels'] = o['Num_Levels']
            details['zoomFactor'] = o['Zoom_Factor']
            details['overlayType'] = o['Overlay_Type']
            details['overlayName'] = o['Overlay_Name']
            overlays.append(details)

        locations = {}
        locations['lat'] = lat
        locations['lng'] = lng
        locations['name'] = gresource.get_resource_name(type_name)
        locations['overlays'] = overlays
        return {"locations": [locations]}

    def for_many_resources(self, country=0, typ=0):
        """
        Returns the location information for all the resources
        in a country for the type.

        :@param country: the country id/name
        :@param typ: type id/name
        """

        moderation = Moderation(self.connection)
        keys, values = moderation.get_all_resources(country=country, typ=typ)

        type_id = self.main.get_type_id(typ)
        country_id = self.main.get_country_id(country)

        type_name = self.main.get_type_name(type_id)
        country_name = self.main.get_country_name(country_id)
        table_name = type_name + "_Location"

        loc = []
        for v in values:
            desc_id = v[0]
            name = v[1]

            lat, lng = self.__get_lat_lng(table_name, desc_id)
            loc.append([lat, lng, name])

        return {"locations": loc, "boundLocation": country_name}
