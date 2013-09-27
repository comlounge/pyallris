import requests
from lxml import etree, html
from lxml.cssselect import CSSSelector
import datetime
import pytz
from pytz import timezone
import pytz
utc = pytz.utc

from base import RISParser

class AgendaItemParser(RISParser):
    """parses all known agenda items and stores them in the database"""

    body_sel = CSSSelector('body')

    def __init__(self, url,
            tzinfo = timezone('Europe/Berlin'), 
            months = 12):
        self.utc = pytz.utc
        self.tzinfo = tzinfo
        super(AgendaItemParser, self).__init__(url)

    def process(self):
        """process meetings"""

        # get all the agenda items we need to parse
     
        meetings = self.db.meetings.find({'ERROR' : {'$exists' : False } })
        tolfdnrs = []
        for meeting in meetings:
            for top in meeting['tops']:
                tolfdnrs.append(top['tolfdnr'])
                self.process_agenda_item(top['tolfdnr'])
        return

    def process_agenda_item(self, tolfdnr):
        """process a single agenda item

        :param tolfdnr: id of agenda item
        """
        url = self.url %tolfdnr
        print url

        r = requests.get(url)
        xml = r.text.encode('ascii','xmlcharrefreplace') 
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml, parser=parser)
        agenda_item = {
            '_id' : tolfdnr,
        }
        for item in root[0].iterchildren():
            if item.tag == "rtfWP" and len(item) > 0:
                try:
                    agenda_item["transcript"] = etree.tostring(item[0][1][0])
                except:
                    print etree.tostring(item)
                    raise
            else:
                agenda_item[item.tag] = item.text
        self.db.agenda_items.save(agenda_item)


url = "http://ratsinfo.aachen.de/bi/to020.asp?selfaction=ws&template=xyz&TOLFDNR=%s"
sp = AgendaItemParser(url)
sp.process()


