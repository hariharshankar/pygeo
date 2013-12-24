from geo.db.query import Select


class GeoResource():

    parent_plant_id = 0
    type_id = 0
    country_id = 0
    state_id = 0
    description_id = 0

    def __init__(self, connection, description_id, type_id=None, country_id=None, state_id=None):
        """
        The primitive class for all geo resources.
        """
        if not description_id or int(description_id) == 0:
            raise AttributeError("Description ID must be an int > 0")

        self.description_id = description_id
        self.connection = connection
        self.type_id = type_id
        self.country_id = country_id
        self.state_id = state_id
        self.parent_plant_id = 0
        self.latest_revision_id = 0
        self.name = ""

        if not self.type_id or not self.country_id or not self.state_id:
            self.__get_ids()

    def __get_ids(self):
        select = Select(self.connection)
        result = select.read("History", where=[["Description_ID", "=", self.description_id]])
        if result.rowcount == 0:
            raise LookupError("Description ID %s does not exist." % self.description_id)

        ids = result.first()
        self.type_id = ids['Type_ID']
        self.country_id = ids['Country_ID']
        self.state_id = ids['State_ID']
        self.parent_plant_id = ids['Parent_Plant_ID']

    def get_latest_revision_id(self):
        """
        Get the latest revision id for this resource.
        """

        if self.latest_revision_id > 0:
            return self.latest_revision_id

        if self.parent_plant_id == 0:
            self.__get_ids()

        select = Select(self.connection)
        id = select.read("History", columns=["max(Description_ID) as Description_ID"],
                         where=[["Parent_Plant_ID", "=", self.parent_plant_id],
                                ["and"], ["Accepted", "=", "1"]])

        self.latest_revision_id = id.first()['Description_ID']
        return self.latest_revision_id


    def get_resource_name(self, type_name):
        """
        Get the name of the resource. Requires type name to be passed
        as the name is in the description table.
        """

        if self.name:
            return self.name

        desc_table = type_name + "_Description"
        select = Select(self.connection)
        desc = select.read(desc_table,
                    columns=["Name_omit"],
                    where=[["Description_ID", "=", self.get_latest_revision_id()]]
                    )
        self.name = desc.first()['Name_omit']
        return self.name

