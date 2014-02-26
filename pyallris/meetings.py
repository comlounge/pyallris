import requests
from lxml import objectify, etree
import pymongo
import datetime
import pytz
import uuid
from pytz import timezone
from utils import parse_date
import pytz
import argparse
import sys
utc = pytz.utc

from base import RISParser

class MeetingParser(RISParser):
    """parse the list of meetings for 1 year back from now"""
    
    agenda_item_url = "http://ratsinfo.aachen.de/bi/to020.asp?selfaction=ws&template=xyz&TOLFDNR=%s"
    CLS_FILENAME = "meetings"

    def __init__(self, url, base_url="/",
            tzinfo = timezone('Europe/Berlin'), 
            months = 12,
            **kwargs):
        self.utc = pytz.utc
        self.tzinfo = tzinfo
        super(MeetingParser, self).__init__(url, base_url = base_url, **kwargs)

        today = datetime.date.today()
        end = today + datetime.timedelta(months*1) # look one month into the future
        start = end - datetime.timedelta(months*31) # kinda rough computation here
        print start, end

        self.timerange_url = self.base_url %(start.strftime("%d.%m.%Y"), end.strftime("%d.%m.%Y"))

    @classmethod
    def construct_instance(cls, args):
        """construct the parse instance"""
        bu = args.base_url
        if not bu.endswith("/"):
            bu = bu + "/"
        url = bu+"to010.asp?selfaction=ws&template=xyz&SILFDNR=%s"
        base_url = bu+ "si010.asp?selfaction=ws&template=xyz&kaldatvon=%s&kaldatbis=%s"
        return cls(url,
            base_url = base_url,
            city = args.city,
            mongodb_host = args.mongodb_host,
            mongodb_port = args.mongodb_port,
            mongodb_name = args.mongodb_name,
            force = args.force
        )

    def process(self):
        """process meetings"""
        parser = etree.XMLParser(recover=True)
        r = requests.get(self.timerange_url)
        xml = r.text.encode('ascii','xmlcharrefreplace') 
        root = etree.fromstring(xml, parser=parser)

        for item in root[1].iterchildren():
            meeting = {}
            for e in item.iterchildren():
                meeting[e.tag] = e.text

            meeting['start_date'] = parse_date(meeting['sisbvcs'])
            meeting['end_date'] = parse_date(meeting['sisevcs'])
            meeting['tz_start_date'] = parse_date(meeting['sisbvcs'], tzinfo=utc).astimezone(self.tzinfo)
            meeting['tz_end_date'] = parse_date(meeting['sisevcs'], tzinfo=utc).astimezone(self.tzinfo)
            silfdnr = meeting['silfdnr']
            try:
                result = self.process_agenda(silfdnr)
                meeting.update(result)
                print "ok"
            except Exception, e:
                meeting['ERROR'] = True
                print e
            meeting['meeting_id'] = str(meeting['silfdnr'])
            meeting['_id'] = "%s:%s" %(self.city, silfdnr)
            meeting['city'] = self.city
            self.db.meetings.save(meeting)

    def process_agenda(self, silfdnr):
        """process tagesordnung for sitzung"""
        url = self.url %silfdnr
        print "processing agenda at %s" %url

        r = requests.get(url)
        xml = r.text.encode('ascii','xmlcharrefreplace') 
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml, parser=parser)

        record = {'tops' : []}

        special = {}
        for item in root[1].iterchildren():
            special[item.tag] = item.text
        record['special'] = special

        head = {}
        for item in root[1].iterchildren():
            head[item.tag] = item.text
        record['head'] = head

        for item in root[2].iterchildren():
            elem = {}
            for e in item.iterchildren():
                elem[e.tag] = e.text

            section = [elem['tofnum'], elem['tofunum'], elem['tofuunum']]
            section = [x for x in section if x!="0"]
            elem['section'] = ".".join(section)

            record['tops'].append(elem)
        return record

if __name__=="__main__":
    p = MeetingParser.from_args()
    p.process()
    sys.exit()
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
    parser.add_argument('-f', '--force', action = "store_true", help='should meetings be parsed again even if they are already in the database?')
    args = parser.parse_args()

    #city = "Aachen"
    #url = "http://ratsinfo.aachen.de/bi/to010.asp?selfaction=ws&template=xyz&SILFDNR=%s"
    #base_url = "http://ratsinfo.aachen.de/bi/si010.asp?selfaction=ws&template=xyz&kaldatvon=%s&kaldatbis=%s"
    bu = args.base_url
    if not bu.endswith("/"):
        bu = bu + "/"
    url = bu+"to010.asp?selfaction=ws&template=xyz&SILFDNR=%s"
    base_url = bu+ "si010.asp?selfaction=ws&template=xyz&kaldatvon=%s&kaldatbis=%s"
    sp = MeetingParser(
        url, 
        base_url = base_url,
        city = args.city,
        mongodb_host = args.mongodb_host,
        mongodb_port = args.mongodb_port,
        mongodb_name = args.mongodb_name,
        force = args.force
    )
    sp.process()


