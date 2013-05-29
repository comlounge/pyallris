import requests
from lxml import etree, html
from StringIO import StringIO
import pymongo

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

    def __init__(self, url, base_url = "/", db="ratsinfo"):
        """initialize the RIS parser with the base URL of the system (for computing absolute URLs) and the URL to parse

        :param url: The main URL to start parsing from.
        :param base_url: The base url of the system. This can be used to construct absolute URLs
            as the system only provides relative URLs in it's HTML source
        """

        self.base_url = base_url
        self.url = url
        self.db = pymongo.Connection()[db]

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

