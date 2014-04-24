from geo.db.query import Select
import flask


class Main(object):
    """
    Utility class for retrieving non-geo-resource centric data.
    """

    def __init__(self, connection):
        #self.connection = connection
        self.select = Select(connection)
        self.session = flask.session

    def get_type_name(self, type_id):
        """
        Returns the type name given a type id.

        :@param type_id: the type id
        :@returns type name as a string
        """

        result = self.select.read("Type",
                                  columns=["Type"],
                                  where=[["Type_ID", "=", type_id]]
                                  )

        if result.returns_rows:
            return result.first()['Type']

    def get_type_id(self, type_name):
        """
        Returns the type id or None given a type name.

        :@param type_name: the type
        :@returns type id or None
        """

        try:
            t = int(type_name)
            #FIXME: check if the id is valid
            # this is already an id, so return
            return t
        except:
            pass

        result = self.select.read("Type",
                                  columns=["Type_ID"],
                                  where=[["Type", "like", "'" + type_name + "'"]]
                                  )

        if result.returns_rows:
            return result.first()['Type_ID']

    def get_types(self, db_name):
        """
        Returns all type ids, type name for the give db name.

        :@param db_name: db name
        :@returns List of tuples: [(type_ids, type),...]
        """

        result = self.select.read("Type",
                                  columns=["Type_ID", "Type"],
                                  where=[["Database_Type", "like", "'" + db_name + "'"]],
                                  order_by=["Type_ID", "asc"]
                                  )

        return self.select.process_result_set(result)

    def get_databases(self, type_id=None):
        """
        Returns the database names for all types.

        :@returns List of tuples: [(db_name),..]
        """

        where = []
        if type_id:
            where.append(["Type_ID", "=", type_id])
        result = self.select.read("Type",
                                  columns=["distinct(Database_Type)"],
                                  where=where
                                  )

        return self.select.process_result_set(result)

    def get_country_name(self, country_id):
        """
        Returns the country name given a country id.

        :@param country_id: the country id
        :@returns country name as a string
        """

        result = self.select.read("Country",
                                  columns=["Country"],
                                  where=[["Country_ID", "=", country_id]]
                                  )

        if result.returns_rows:
            return result.first()['Country']

    def get_country_id(self, country_name):
        """
        Returns the country id or None given a country name.

        :@param country_name: the country
        :@returns country id or None
        """

        try:
            c = int(country_name)
            #FIXME: check if the id is valid
            # this is already an id, so return
            return c
        except:
            pass

        result = self.select.read("Country",
                                  columns=["Country_ID"],
                                  where=[["Country", "like", "'" + country_name + "'"]]
                                  )

        if result.returns_rows:
            return result.first()['Country_ID']

    def get_types_for_country(self, country_id):
        """
        Returns all the types for a given country

        :@param country_id: country id or country name
        :@returns Keys and values as a list of tuples:
            ['k1', 'k2'], [(type_id, type),..]
        """

        type_result = self.select.read("History",
                            columns=["distinct(Type_ID)"],
                            where=[["Country_ID", "=", country_id]],
                            order_by=["Type_ID", "asc"])

        types = type_result.fetchall()
        keys = ['Type_ID', 'Type']
        values = []

        for t in types:
            tid = t['Type_ID']
            result = self.select.read("Type",
                                    columns=["Type_ID", "Type"],
                                    where=[["Type_ID", "=", tid]]
                                    )
            values.append(result.first().values())

        return keys, values

    def get_countries(self, typ):
        """
        Returns all the countries that has data for the given type.

        :@param typ: type id or type name
        :@returns Keys and values as a list of tuples:
            ['k1', 'k2'], [(country_id, country),..]
        """

        try:
            type_id = int(typ)
        except ValueError as e:
            type_id = self.get_type_id(typ)

        if not type_id:
            return

        country_result = self.select.read("History",
                                     columns=["distinct(Country_ID)"],
                                     where=[["Type_ID", "=", type_id]]
                                     )
        countries = country_result.fetchall()
        keys = ["Country_ID", "Country"]
        values = []

        for country in countries:
            cid = country['Country_ID']
            result = self.select.read("Country",
                                  columns=["Country_ID", "Country"],
                                  where=[["Country_ID", "=", cid]]
                                  )
            values.append(result.first().values())
        values.sort()
        return keys, values

    def get_states(self, country):
        """
        Returns all the states for a country.

        :@param country: country name or id
        :@returns List of tuples [(state_id, state), ...]
        """

        try:
            country_id = int(country)
        except ValueError as e:
            country_id = self.get_country_id(country)

        if not country_id:
            return

        result = self.select.read("State",
                                  columns=["State_ID", "State"],
                                  where=[["Country_ID", "=", country_id]],
                                  order_by=["State", "asc"]
                                  )
        return self.select.process_result_set(result)

    def get_search_redirect_url(self, prefix, return_type=None):
        url = []
        if not prefix.startswith("/"):
            prefix = "/" + prefix

        url.append(prefix)

        if not return_type in ['type_summary', 'country_summary']:
            url.append(self.session.get('pref_db_type', 'powerplants'))

        if not return_type == 'country_summary':
            url.append(self.session.get('pref_type', "1"))

        url.append(self.session.get('pref_country', "1"))

        if not return_type in ['type_summary', 'country_summary']:
            url.append(self.session.get('pref_state', "0"))

        return "/".join(url)

    def store_user_pref(self, db_type, country, typ, state):

        self.session['pref_country'] = str(country)
        self.session['pref_type'] = str(typ)
        self.session['pref_db_type'] = db_type
        self.session['pref_state'] = str(state)
        return


if __name__ == "__main__":
    from geo.db.connection import Db
    d = Db()
    m = Main(d)
    print(m.get_type_name(1))
