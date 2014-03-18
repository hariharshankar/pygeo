from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Db():

    def __init__(self):
        """
        Instantiate a db connection.
        """

        try:
            self.__db = create_engine(
                "mysql://geo:0p3nM0d3!@localhost/geoDev",
                echo=True)
            Session = sessionmaker(bind=self.__db)
            self.__session = Session()
        except Exception as e:
            # FIXME: return a 404
            raise e

    def __session(self):
        return self.__session

    def __cant_set(self):
        raise RuntimeError("Private property cannot be set.")

    def __cant_get(self):
        raise RuntimeError("Cannot get protected property.")

    db = property(__cant_get, __cant_set)
    session = property(__session, __cant_set)


if __name__ == "__main__":
    d = Db()
    #print d.session.query("Type_ID").from_statement("select * from Type").all()
