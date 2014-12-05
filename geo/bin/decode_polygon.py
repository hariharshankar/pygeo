"""
Decodes the Google encoded polygon/polyline string into
a list of lat lng lists.

Decoding function from 
http://cartometric.com/blog/2012/10/20/decode-google-map-encoded-points-as-well-known-text-wkt-with-python/
"""

__author__ = 'Harihar Shankar'

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from geo.db.query import Select
from geo.db import connection
from geo.core.main import Main
from geo.core.moderation import Moderation
import json


class DecodePolygon(object):
    """
    Decodes the Google encoded polygon/polyline string into
    a list of lat lng tuples.
    """

    def __init__(self):
        self.conn = connection.Db()
        self.main = Main(self.conn)
        self.moderation = Moderation(self.conn)
        self.select = Select(self.conn)

    @staticmethod
    def decode_GMap(encoded_string):
        index = 0
        lat = 0
        lng = 0
        coords = []
        str_len = len(encoded_string)

        #print(encoded_string)
        #print()
        while index < str_len:
            shift = 0
            result = 0
    
            stay_in_loop = True
            while stay_in_loop and index < str_len:  # GET THE LATITUDE
                b = ord(encoded_string[index]) - 63
                result |= (b & 0x1f) << shift
                shift += 5
                index += 1
    
                if not b >= 0x20:
                    stay_in_loop = False
    
            # Python ternary instruction..
            d_lat = ~(result >> 1) if (result & 1) else (result >> 1)
            lat += d_lat
    
            shift = 0
            result = 0

            stay_in_loop = True
            while stay_in_loop and index < str_len:                                                # GET THE LONGITUDE
                b = ord(encoded_string[index]) - 63
                result |= (b & 0x1f) << shift
                shift += 5
                index += 1
    
                if not b >= 0x20:
                    stay_in_loop = False
    
            # Python ternary instruction..
            d_lng = ~(result >> 1) if (result & 1) else (result >> 1)
            lng += d_lng
    
            lng_num = lng * 1e-5
            lat_num = lat * 1e-5
            coords.append([str(lat_num), str(lng_num)])

        return coords

    def decode_all(self):
        databases = self.main.get_databases()
        session = self.conn.session
        for db in databases[1]:
            print(db[0])
            t_keys, types = self.main.get_types(db[0])
            overlays_table = "_Overlays"
            for typ in types:
                type_overlay = typ[1] + overlays_table

                points = self.select.read(type_overlay,
                                          columns=['Overlay_ID', 'Points'])
                for point in points:
                    if not point[1]:
                        continue

                    decoded_point = self.decode_GMap(point[1])
                    sql = "UPDATE " + type_overlay + " SET Points=:decoded_point WHERE Overlay_ID=:overlay_id"
                    print(sql, point[0])
                    session.execute(sql, {"overlay_id": point[0], "decoded_point": json.dumps(decoded_point)})
                session.commit()
        session.close()


if __name__ == "__main__":
    d = DecodePolygon()
    d.decode_all()
