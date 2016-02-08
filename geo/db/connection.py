"""
Instantiate a db connection.
"""

import mysql.connector as mysql
from mysql.connector.pooling import MySQLConnectionPool


class Db(object):
    """
    Instantiate a db connection.
    """

    def __init__(self):

        dbconfig = {
            "database": "geoDev",
            "user": "geo",
            "password": "0p3nM0d3!",
            "host": "localhost",
            #"raw": True,
            "pool_name": "geo_pool",
            "pool_size": 20,
            "pool_reset_session": True
        }

        try:
            self.__conn_pool = MySQLConnectionPool(**dbconfig)
            #self.__conn_pool = mysql.connect(**dbconfig)
        except Exception:
            raise

    def __get_session(self):
        """
        Returns the private session var.
        """
        return self.__conn_pool.get_connection()
        #return self.__conn_pool

    def __cant_set(self):
        """Raises runtime error."""
        raise RuntimeError("Private property cannot be set.")

    def __cant_get(self):
        """Raises runtime error."""
        raise RuntimeError("Cannot get protected property.")

    db_conn = property(__cant_get, __cant_set)
    session = property(__get_session, __cant_set)
