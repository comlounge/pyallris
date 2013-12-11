import requests
from lxml import etree, html
from lxml.cssselect import CSSSelector
import datetime
import pytz
from pytz import timezone
import pytz
utc = pytz.utc
import pprint
import argparse

from base import RISParser

class AgendaItemParser(RISParser):
    """parses all known agenda items and stores them in the database"""

    body_sel = CSSSelector('body')
    city = "Aachen"

    def __init__(self, url,
            tzinfo = timezone('Europe/Berlin'), 
            months = 12,
            **kwargs):
        self.utc = pytz.utc
        self.tzinfo = tzinfo
        super(AgendaItemParser, self).__init__(url, **kwargs)

    def process(self):
        """process meetings"""

        # get all the agenda items we need to parse
     
        meetings = self.db.meetings.find({
            'ERROR' : {'$exists' : False },
            'city' : self.city
        })
        tolfdnrs = []
        for meeting in meetings:
            print "*** processing meeting %s" %meeting['meeting_id']
            for top in meeting['tops']:
                tolfdnrs.append(top['tolfdnr'])
                self.process_agenda_item(top['tolfdnr'])
        return

    def process_agenda_item(self, tolfdnr):
        """process a single agenda item

        :param tolfdnr: id of agenda item
        """
        url = self.url %tolfdnr

        r = requests.get(url)
        xml = r.text.encode('ascii','xmlcharrefreplace') 
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml, parser=parser)
        agenda_item = {
            '_id' : "%s:%s" %(self.city, tolfdnr),
            'top_id' : str(tolfdnr),
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
        if "nowDate" not in agenda_item:
            # something is broken with this so we don't store it
            print "skipping broken agenda at ", url
            pprint.pprint(agenda_item)
            return
        agenda_item['city'] = self.city
        self.db.agenda_items.save(agenda_item)
        print "saved agenda item at ", url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='process meetings')
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
    args = parser.parse_args()
    bu = args.base_url
    if not bu.endswith("/"):
        bu = bu + "/"
    url = bu + "to020.asp?selfaction=ws&template=xyz&TOLFDNR=%s"
    sp = AgendaItemParser(url, 
        city = args.city,
        mongodb_host = args.mongodb_host,
        mongodb_port = args.mongodb_port,
        mongodb_name = args.mongodb_name,
    )
    sp.process()


