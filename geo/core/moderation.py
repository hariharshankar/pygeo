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

    def get_all_resources(self, country_id=0, type_id=0):
        """
        Fetches the most recent version for all the resources
        for the given country and type.
        @param: country: country id/name
        @param: typ: type id/name

        """

        if int(country_id) <= 0 or int(type_id) <= 0:
            return ([], [])

        main = Main(self.db_conn)
        type_name = main.get_type_name(type_id)
        if not type_name:
            return ([], [])

        """
        parent_ids = select.read("History",
                                 columns=["distinct(Parent_Plant_ID)"],
                                 where=[["Country_ID", "=", country_id],
                                        ["and"],
                                        ["Type_ID", "=", type_id],
                                        ["and"], ["Accepted", "=", 1]
                                        ]
                                 )
        description_ids = select.read("History",
                                      columns=["Parent_Plant_ID",
                                               "Description_ID"],
                                      where=[["Parent_Plant_ID",
                                              "in",
                                              [x[0] for x in parent_ids]]
                                      ]
        )
        """

        select = Select(self.db_conn)
        sql = "SELECT Parent_Plant_ID,Description_ID FROM History WHERE \
                Parent_Plant_ID in \
                    (SELECT distinct(Parent_Plant_ID) \
                    FROM History \
                    WHERE Country_ID=:country_id \
                    and Type_ID=:type_id \
                    and Accepted=:accepted \
                    ) \
              and Accepted=1;"
        data = {
            "country_id": country_id,
            "type_id": type_id,
            "accepted": 1
        }
        description_ids = self.db_conn.session.execute(sql, data)
        self.db_conn.session.close()

        keys = ["Description_ID", "Name"]

        # get the latest description id for all resources
        resources = {}
        for did in description_ids:
            if resources.get(did['Parent_Plant_ID'], 0) < int(did['Description_ID']):
                resources[did['Parent_Plant_ID']] = did['Description_ID']

        names = select.read(type_name + "_Description",
                            columns=["Description_ID", "Name_omit"],
                            where=[["Description_ID", "in",
                                   list(resources.values())]
                                   ],
                            order_by=["Name_omit", "ASC"])


        values = [name for name in names if name[0] is not None]
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
            if description_id['Description_ID'] == description_id['Parent_Plant_ID']:
                new_submits.append({
                    'type_name': type_name,
                    'country_name': country_name,
                    'geo_name': geo_name,
                    'description_id': str(description_id['Description_ID'])
                })
            else:
                edits.append({
                    'type_name': type_name,
                    'country_name': country_name,
                    'geo_name': geo_name,
                    'description_id': str(description_id['Description_ID'])
                })
        return new_submits, edits
