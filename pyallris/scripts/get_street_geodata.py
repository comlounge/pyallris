"""

Script for retrieving lat/long and geojson polygons for the streets in the database

"""


import pymongo
import argparse
import requests

class GeoDataRetriever(object):
    """class for retrieving geodata for a list of streets. We retrieve the geolocation but also a geojson object
    and store it inside mongodb.
    """

    CLS_FILENAME = "documents"

    def __init__(self, 
            city = None,
            mongodb_host="localhost",
            mongodb_port=27017,
            mongodb_name='allris',
        ):
        """initialize the RIS parser with the base URL of the system (for computing absolute URLs) and the URL to parse

        :param city: city name to use (default to `None`)
        :param mongodb_host: hostname of the mongodb instance to use (defaults to localhost)
        :param mongodb_port: port mongodb instance to use (defaults to 27017)
        :param mongodb_name: name of the mongodb databse to use (defaults to allris)
        """

        self.db = pymongo.MongoClient(
            host = mongodb_host,
            port = mongodb_port,
        )[mongodb_name]
        self.city = city.lower()

    def __call__(self):
        """go through all the streets for a city"""
        streets = self.db.streets.find({'city' : self.city})
        for street in streets:
            print street['original']
            url = "http://nominatim.openstreetmap.org/search?q=%s, %s&format=json&polygon=0&addressdetails=1" %(
                street['original'],
                self.city
            )
            data = requests.get(url).json()
            if len(data) == 0:
                print "aww, no city found"
            else:
                result = data[0]
                street['lat'] = result['lat']
                street['lng'] = result['lon']
                self.db.streets.save(street)

def run():
    """run the script"""
    # build the argparser to parse mongodb details
    parser = argparse.ArgumentParser(description='process document')
    parser.add_argument('-c', '--city', metavar='CITY', 
        required = True,
        help='the city code for the city to parse, e.g. "aachen"', dest="city")
    parser.add_argument('--mongodb_host', default="localhost", metavar='HOST', help='mongodb host', dest="mongodb_host")
    parser.add_argument('--mongodb_port', default=27017, type=int, metavar='PORT', help='mongodb port', dest="mongodb_port")
    parser.add_argument('--mongodb_name', default="allris", metavar='DB_NAME', help='name of mongodb database to use', dest="mongodb_name")
    args = parser.parse_args()
    c = GeoDataRetriever(
            city = args.city,
            mongodb_host = args.mongodb_host,
            mongodb_port = args.mongodb_port,
            mongodb_name = args.mongodb_name,
        )
    print "fetching data"
    c()


if __name__=="__main__":
    run()


