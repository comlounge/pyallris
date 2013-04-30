import requests
from lxml import etree
from StringIO import StringIO

__all__ = ['RISParser']

class RISParser(object):
    """base parser for RIS information contained in HTML pages and XML output.

    We provide both methods of obtaining information in this base class as not
    everything is available from one source.

    """

    def __init__(self, url, base_url = "/"):
        """initialize the RIS parser with the base URL of the system (for computing absolute URLs) and the URL to parse

        :param url: The main URL to start parsing from.
        :param base_url: The base url of the system. This can be used to construct absolute URLs
            as the system only provides relative URLs in it's HTML source
        """

        self.base_url = base_url
        self.url = url

    def parse_html(self, url):
        """start up a parser and return the tree for further processing"""
        response = requests.get(url)
        parser = etree.HTMLParser()
        return etree.parse(StringIO(response.text), parser)

    def __call__(self):
        """start processing the HTML page"""
        tree = self.parse(self.url)
        return self.process(tree)

    def parse_xml(self, url):
        """parse an XML file and return the tree"""
        parser = etree.XMLParser(recover=True)
        r = requests.get(url)
        xml = r.text.encode('ascii','xmlcharrefreplace') 
        return etree.fromstring(xml, parser=parser)

    def __call__(self):
        """start processing"""
        raise NotImplemented

