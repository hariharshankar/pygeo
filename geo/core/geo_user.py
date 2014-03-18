from geo.db.query import Select


class GeoUser():

    def __init__(self, connection, user_id=None, username=None):
        """
        The primitive class for all users.
        """

        if not user_id and not username:
            raise AttributeError("User ID or username required.")

        self.select = Select(connection)

        user = self.get_user_info(self.select, username=username, user_id=user_id)

        self.user_id = user['User_ID']
        self.username = user['Username_require']
        self.__password = user['Password_require']
        self.firstname = user['First_Name_require']
        self.lastname = user['Last_Name_require']

    @staticmethod
    def get_user_info(select, user_id=None, username=None):

        result = None
        if user_id:
            result = select.read("User", where=[["User_ID", "=", user_id]])
            if result.rowcount == 0:
                raise LookupError("User ID %s does not exist." % user_id)
        elif username:
            result = select.read("User", where=[["Username_require", "LIKE", "'"+username+"'"]])
            if result.rowcount == 0:
                raise LookupError("Username %s does not exist." % username)
        if not result:
            raise Exception("No results retrieved for the user info")

        return result.first()

    def validate_user(self, password):
        return self.__password == password
