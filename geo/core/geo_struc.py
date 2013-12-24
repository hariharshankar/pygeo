

class Geo():

    keys = []
    values = []

    def __init__(self, keys, values):
        self.keys = keys
        self.values = values

    def count_values(self):
        """
        Returns the number of rows in the values list.
        """
        return len(self.values)

    def get_value_for(self, key, index):
        """
        Get a particular value, given the column name and
        the row index.
        """

        number_of_rows = self.get_row_count()

        if number_of_rows == 0:
            return

        if 0 > index or index > number_of_rows:
            raise IndexError("Index %s/%s out of range." %
                             (index, number_of_rows - 1))

        if key not in self.keys:
            return

        return self.values[index][self.keys.index(key)]
