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
        self.types_with_segments = [19, 20, 24, 25, 26, 27]

    def get_all_resources(self, country_id=0, type_id=0, state_id=0):
        """
        Fetches the most recent version for all the resources
        for the given country and type.
        @param: country_id: country id
        @param: type_id: type id
        @param: state_id: state id

        """

        db_cxn = self.db_conn.session
        db_cur = db_cxn.cursor(dictionary=True)

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
        name_field = "Name_omit"
        if type_id in self.types_with_segments:
            name_field = "Name_of_this_Segment"

        sql = "SELECT Parent_Plant_ID,Description_ID FROM History WHERE \
                Parent_Plant_ID in \
                    (SELECT distinct(Parent_Plant_ID) \
                    FROM History \
                    WHERE Country_ID=%(country_id)s \
                    and Type_ID=%(type_id)s \
                    and Accepted=%(accepted)s \
                    ) \
              and Accepted=1;"
        data = {
            "country_id": country_id,
            "type_id": type_id,
            "accepted": 1
        }
        if state_id > 0:
            sql = "SELECT Parent_Plant_ID,Description_ID FROM History WHERE \
                    Parent_Plant_ID in \
                        (SELECT distinct(Parent_Plant_ID) \
                        FROM History \
                        WHERE Country_ID=%(country_id)s \
                        and State_ID=%(state_id)s \
                        and Type_ID=%(type_id)s \
                        and Accepted=%(accepted)s \
                        ) \
                  and Accepted=1;"
            data = {
                "country_id": country_id,
                "type_id": type_id,
                "state_id": state_id,
                "accepted": 1
            }
        db_cur.execute(sql, data)

        keys = ["Description_ID", "Name"]

        select = Select(self.db_conn)
        # get the latest description id for all resources
        resources = {}
        for did in db_cur:
            if resources.get(did['Parent_Plant_ID'], 0) < int(did['Description_ID']):
                resources[did['Parent_Plant_ID']] = did['Description_ID']

        result = select.read(type_name + "_Description",
                            columns=["Description_ID", name_field],
                            where=[["Description_ID", "in",
                                   list(resources.values())]
                                   ],
                            order_by=[name_field, "ASC"])

        db_cxn.close()
        return select.process_result_set(result)

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

            if not description_id['Parent_Plant_ID']:
                #TODO: this should not happen. all versions shd have a parent. error from old code?
                continue

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
