import requests
from lxml import etree, html
from StringIO import StringIO
import pymongo
import argparse
import os
import importlib

__all__ = ['RISParser', 'ParseError']

class ParseError(Exception):
    """exception being raised when we encounter some error while parsing"""

    def __init__(self, url, msg):
        self.msg = msg
        self.url = url

    def __str__(self):
        return "<Parse Error in %s: %s>" %(self.url, self.msg)


class RISParser(object):
    """base parser for RIS information contained in HTML pages and XML output.

    We provide both methods of obtaining information in this base class as not
    everything is available from one source.

    """

    CLS_FILENAME = "documents"

    def __init__(self, 
            url, 
            base_url = "/", 
            city = None,
            mongodb_host="localhost",
            mongodb_port=27017,
            mongodb_name='allris',
            force = True,
        ):
        """initialize the RIS parser with the base URL of the system (for computing absolute URLs) and the URL to parse

        :param url: The main URL to start parsing from.
        :param base_url: The base url of the system. This can be used to construct absolute URLs
            as the system only provides relative URLs in it's HTML source
        :param city: city name to use (default to `None`)
        :param mongodb_host: hostname of the mongodb instance to use (defaults to localhost)
        :param mongodb_port: port mongodb instance to use (defaults to 27017)
        :param mongodb_name: name of the mongodb databse to use (defaults to allris)
        :param force: flag if records already present in the database should be read again
        """

        self.base_url = base_url
        self.url = url
        self.force = force
        self.db = pymongo.MongoClient(
            host = mongodb_host,
            port = mongodb_port,
        )[mongodb_name]
        self.city = city

    @classmethod
    def construct_instance(cls, args):
        """construct the actual parser instance and return it. You can override this class method in your own class to 
        adjust the parameters needed for the class.

        :param args: The result from the arg parser
        :returns: an instance of the RIS parser
        """
        return cls(args.base_url,
            city = args.city,
            mongodb_host = args.mongodb_host,
            mongodb_port = args.mongodb_port,
            mongodb_name = args.mongodb_name,
            force = args.force
        )

    @classmethod
    def from_args(cls):
        """parse the arguments from the command line and create a class instance from that"""


        parser = argparse.ArgumentParser(description='process document')
        parser.add_argument('-c', '--city', metavar='CITY', 
            required = True,
            help='the city code for the city to parse, e.g. "aachen"', dest="city")
        parser.add_argument('-b', '--base_url', metavar='URL', 
            required = True,
            help='base URL of the ALLRIS installation, e.g. http://www.berlin.de/ba-marzahn-hellersdorf/bvv-online/. si020.asp etc. should not be included', 
            dest="base_url")
        parser.add_argument('--mongodb_host', default="localhost", metavar='HOST', help='mongodb host', dest="mongodb_host")
        parser.add_argument('--mongodb_port', default=27017, type=int, metavar='PORT', help='mongodb port', dest="mongodb_port")
        parser.add_argument('--mongodb_name', default="allris", metavar='DB_NAME', help='name of mongodb database to use', dest="mongodb_name")
        parser.add_argument('-f', '--force', action = "store_true", help='should objects be parsed again even if they are already in the database?')
        args = parser.parse_args()


        # try to retrieve the correct class to use in case we have a specialized class in cities/<city>/<module>
        name = "cities.%s.%s" %(args.city, cls.CLS_FILENAME) 
        try:
            m = importlib.import_module(name)
            cls = m.DocumentParser
        except ImportError:
            # no specialized version of the parser for the given city was found
            pass

        return cls.construct_instance(args)


    def parse_html(self, url):
        """start up a parser and return the tree for further processing"""
        response = requests.get(url)
        return html.fromstring(response.text)

    def parse_xml(self, url):
        """parse an XML file and return the tree"""
        parser = etree.XMLParser(recover=True)
        r = requests.get(url)
        xml = r.text.encode('ascii','xmlcharrefreplace') 
        return etree.fromstring(xml, parser=parser)

    def __call__(self):
        """start processing"""
        raise NotImplemented

