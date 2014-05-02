"""
Handles moderation and moderated resources.
"""

from geo.db.query import Select
from geo.core.main import Main
from geo.core.geo_resource import GeoResource


class Moderation(object):
    """
    Handles moderation and moderated resources.
    """

    def __init__(self, db_conn):
        self.db_conn = db_conn

    def get_all_resources(self, country=0, typ=0):
        """
        Fetches the most recent version for all the resources
        for the given country and type.
        @param: country: country id/name
        @param: typ: type id/name

        """

        if not country or not typ:
            return ([], [])

        main = Main(self.db_conn)

        type_id = main.get_type_id(typ)
        country_id = main.get_country_id(country)

        select = Select(self.db_conn)

        # get the latest description id for all resources
        description_ids = select.read("History",
                                      columns=["distinct(Parent_Plant_ID)",
                                               "Type_ID",
                                               "Country_ID",
                                               "State_ID"],
                                      where=[["Country_ID", "=", country_id],
                                             ["and"],
                                             ["Type_ID", "=", type_id],
                                             ["and"], ["Accepted", "=", 1]
                                             ]
                                      )

        #row_count = len(description_ids)
        keys = ["Description_ID", "Name"]
        values = []

        type_name = main.get_type_name(type_id)

        for res in description_ids:
            geo_resource = GeoResource(self.db_conn,
                                       res['Parent_Plant_ID'],
                                       type_id=res['Type_ID'],
                                       country_id=res['Country_ID'],
                                       state_id=res['State_ID'])
            latest_id = geo_resource.get_latest_revision_id()
            resource_name = geo_resource.get_resource_name(type_name)
            values.append([str(latest_id), unicode(resource_name, "utf-8")])

        return keys, values

    def get_resources_to_moderate(self):
        """
        Returns a list of resources awaiting moderation.
        Will return both new and edited resources.
        """

        select = Select(self.db_conn)

        description_ids = select.read("History",
                                      columns=[
                                          "Parent_Plant_ID",
                                          "Description_ID"
                                      ],
                                      where=[["Moderated", "=", "0"]],
                                      order_by=["Description_ID", "desc"]
        )

        main = Main(self.db_conn)
        new_submits = []
        edits = []

        for description_id in description_ids:
            geo_resource = GeoResource(self.db_conn, description_id['Description_ID'])
            type_id = geo_resource.type_id
            country_id = geo_resource.country_id

            type_name = main.get_type_name(type_id)
            country_name = main.get_country_name(country_id)
            geo_name = geo_resource.get_resource_name(type_name=type_name)
            print(geo_name)
            if description_id['Description_ID'] == description_id['Parent_Plant_ID']:
                new_submits.append({
                    'type_name': type_name,
                    'country_name': country_name,
                    'geo_name': unicode(geo_name, "utf-8"),
                    'description_id': str(description_id['Description_ID'])
                })
            else:
                edits.append({
                    'type_name': type_name,
                    'country_name': country_name,
                    'geo_name': unicode(geo_name, "utf-8"),
                    'description_id': str(description_id['Description_ID'])
                })
        return new_submits, edits
