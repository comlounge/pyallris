import requests
from lxml import etree, html
from lxml.cssselect import CSSSelector
import datetime
import pytz
from pytz import timezone
import pytz
utc = pytz.utc

from base import RISParser

class DocumentParser(RISParser):
    """"""

    #jadoption_css = CSSSelector("#rismain table.risdeco tbody tr td table.tk1 tbody tr td table.tk1 tbody tr td table tbody tr.zl12 td.text3")
    adoption_css = CSSSelector("table.risdeco tr td table.tk1 tr td.ko1 table.tk1 tr td table tr.zl12 td.text3")
    #main_css = CSSSelector("#rismain table.risdeco")

    def __init__(self, url,
            tzinfo = timezone('Europe/Berlin'), 
            months = 12):
        self.utc = pytz.utc
        self.tzinfo = tzinfo
        super(DocumentParser, self).__init__(url)

        # this will be moved to the second stage
        self.db.documents.remove()

    def process(self):
        """process documents"""

        # get all the ids of the documents we need to parse
     
        agenda_items = self.db.agenda_items.find()
        document_ids = [item['volfdnr'] for item in agenda_items if "volfdnr" in item]
        for document_id in document_ids:
            self.process_document(document_id)
        return

    def process_document(self, document_id):
        """process a single document

        :param document_id: id of document to parse
        """
        url = self.url %document_id
        print url

        response = requests.get(url)
        doc = html.fromstring(response.text)
        #import pdb; pdb.set_trace()
        #print etree.tostring(doc)
        #print doc.xpath(self.expr).text_content

        status = td[0].text
        print status
        #import pdb; pdb.set_trace()


url = "http://ratsinfo.aachen.de/bi/vo020.asp?VOLFDNR=%s"
p = DocumentParser(url)
p.process()


