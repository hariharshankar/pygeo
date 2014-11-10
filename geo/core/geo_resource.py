"""
Defining an energy resource.
"""

from geo.db.query import Select
from geo.core.main import Main
from geo.serializations.html import Html


class GeoResource(Html):
    """
    Defines an energy resource.
    """

    parent_plant_id = 0
    type_id = 0
    country_id = 0
    state_id = 0
    description_id = 0

    def __init__(self, connection, description_id,
                 type_id=None, country_id=None, state_id=None):
        """
        The primitive class for all geo resources.
        """

        Html.__init__(self)

        if not description_id or int(description_id) == 0:
            if not type_id and not country_id and not state_id:
                raise AttributeError("Invalid request. Necessary details were not provided.")

        self.description_id = description_id
        self.connection = connection
        self.type_id = type_id
        self.country_id = country_id
        self.state_id = state_id
        self.parent_plant_id = 0
        self.latest_revision_id = 0
        self.is_moderated = 0
        self.name = ""

        self.select = Select(self.connection)
        self.main = Main(self.connection)

        if not self.type_id or not self.country_id or not self.state_id:
            self.__get_ids()

        self.type_name = self.main.get_type_name(self.type_id)

    def __get_ids(self):
        """
        Private class, gets the necessary ids from the History
        table for a resource.
        """

        result = self.select.read("History",
                                  where=[["Description_ID", "=",
                                          self.description_id]])
        if result.rowcount == 0:
            raise LookupError("Description ID %s does not exist." %
                              self.description_id)

        ids = result.first()
        self.type_id = ids['Type_ID']
        self.country_id = ids['Country_ID']
        self.state_id = ids['State_ID']
        self.parent_plant_id = ids['Parent_Plant_ID']
        self.is_moderated = ids['Moderated']

    def get_latest_revision_id(self, moderated=True):
        """
        Get the latest revision id for this resource.
        """

        if self.latest_revision_id > 0:
            return self.latest_revision_id

        if self.description_id == 0:
            # new plant creation
            return None

        if self.parent_plant_id == 0:
            self.__get_ids()

        where = [["Parent_Plant_ID", "=", self.parent_plant_id]]
        if moderated:
            where.extend([["and"], ["Accepted", "=", "1"]])

        ids = self.select.read("History", columns=["max(Description_ID)"],
                               where=where)

        res = ids.first()
        self.latest_revision_id = res[0]
        return self.latest_revision_id

    def get_resource_name(self, type_name):
        """
        Get the name of the resource. Requires type name to be passed
        as the name is in the description table.
        """

        if self.description_id == 0:
            return None

        if self.name:
            return self.name

        desc_table = type_name + "_Description"
        desc = self.select.read(desc_table,
                                columns=["Name_omit"],
                                where=[["Description_ID", "=",
                                        self.get_latest_revision_id(moderated=False)]]
                                )
        self.name = desc.first()['Name_omit']
        return self.name
