from geo.db.query import Select
from geo.core.main import Main
from geo.core.geo_resource import GeoResource

class Moderation():

    def __init__(self, db):
        self.db = db

    def get_all_resources(self, country_id=0, type_id=0):
        """
        Fetches the most recent version for all the resources
        for the given country and type.
        @param: country_id: int
        @param: type_id: int

        """

        if country_id == 0 or type_id == 0:
            raise AttributeError("Invalid attributes given.")

        select = Select(self.db)

        # get the latest description id for all resources
        description_ids = select.read("History",
          columns=["distinct(Parent_Plant_ID) as Parent_Plant_ID", "Type_ID", "Country_ID", "State_ID"],
          where=[["Country_ID", "=", country_id], ["and"], ["Type_ID", "=", type_id],
          ["and"], ["Accepted", "=", 1]
          ])

        #row_count = len(description_ids)
        keys = ["Description_ID", "Name"]
        values = []

        main = Main(self.db)
        type_name = main.get_type_name(type_id)

        for r in description_ids:
            geo_resource = GeoResource(self.db,
                                       r['Parent_Plant_ID'],
                                       type_id=r['Type_ID'],
                                       country_id=r['Country_ID'],
                                       state_id=r['State_ID'])
            latest_id = geo_resource.get_latest_revision_id()
            resource_name = geo_resource.get_resource_name(type_name)
            values.append([latest_id, resource_name])

        return keys, values


