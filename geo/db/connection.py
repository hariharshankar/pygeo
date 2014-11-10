"""
Instantiate a db connection.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys


class Db(object):
    """
    Instantiate a db connection.
    """

    def __init__(self):

        connection_string = ""
        if sys.version_info[0] == 3:
            connection_string = \
                "mysql+mysqlconnector://geo:0p3nM0d3!@localhost/geoDev"
        elif sys.version_info[0] == 2:
            connection_string = "mysql://geo:0p3nM0d3!@localhost/geoDev"
        else:
            return

        try:
            self.__db_conn = create_engine(
                connection_string,
                echo=False)
            session = sessionmaker(bind=self.__db_conn)
            self.__session = session()
        except Exception:
            raise

    def __del__(self):
        """
        Close sessions and connections.
        """
        if self.__session:
            self.__session.close()


    def __get_session(self):
        """
        Returns the private session var.
        """
        return self.__session

    def __cant_set(self):
        "Raises runtime error."
        raise RuntimeError("Private property cannot be set.")

    def __cant_get(self):
        "Raises runtime error."
        raise RuntimeError("Cannot get protected property.")

    db_conn = property(__cant_get, __cant_set)
    session = property(__get_session, __cant_set)
