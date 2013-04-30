import requests
from lxml import etree
from StringIO import StringIO

__all__ = ['RISHTMLParser']

class RISHTMLParser(object):
    """base parser for RIS information contained in HTML pages.

    We do use this parser when there is no XML output available. 
    This base class mainly reads and pre-parses the content. 
    This will automatically open up the main url you give to it and 
    will pass the tree over to ``process()``. 

    """

    def __init__(self, url, base_url = "/"):
        """initialize the RIS HTML parser with the base URL of the system and the URL to parse

        :param url: The main URL to start parsing from.
        :param base_url: The base url of the system. This can be used to construct absolute URLs
            as the system only provides relative URLs in it's HTML source
        """

        self.base_url = base_url
        self.url = url

    def parse(self, url):
        """start up a parser and return the tree for further processing"""
        response = requests.get(url)
        parser = etree.HTMLParser()
        return etree.parse(StringIO(response.text), parser)

    def __call__(self):
        """start processing the HTML page"""
        tree = self.parse(self.url)
        return self.process(tree)

