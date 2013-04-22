import requests
from lxml import objectify, etree
import pymongo
import datetime
import pytz
from pytz import timezone
from utils import parse_date
import pytz
utc = pytz.utc

class SitzungsParser(object):
    """parse the list of sitzungen for 1 year back from now"""

    base_url = "http://ratsinfo.aachen.de/bi/si010.asp?selfaction=ws&template=xyz&kaldatvon=%s&kaldatbis=%s"
    to_url = "http://ratsinfo.aachen.de/bi/to010.asp?selfaction=ws&template=xyz&SILFDNR=%s"
    tzinfo = timezone('Europe/Berlin')

    def __init__(self, months = 12):
        self.utc = pytz.utc
        self.tzinfo = timezone('Europe/Berlin')
        self.coll = pymongo.Connection().ratsinfo.sitzungen
        self.parser = etree.XMLParser(recover=True)

        end = datetime.date.today()
        start = end - datetime.timedelta(months*31)

        self.url = self.base_url %(start.strftime("%d.%m.%Y"), end.strftime("%d.%m.%Y"))

    def process(self):
        """process sitzungen"""
        parser = etree.XMLParser(recover=True)
        r = requests.get(self.url)
        xml = r.text.encode('ascii','xmlcharrefreplace') 
        root = etree.fromstring(xml, parser=parser)

        sitzungen = []
        for item in root[1].iterchildren():
            elem = {}
            for e in item.iterchildren():
                elem[e.tag] = e.text

            elem['start_date'] = parse_date(elem['sisbvcs'])
            elem['end_date'] = parse_date(elem['sisevcs'])
            elem['tz_start_date'] = parse_date(elem['sisbvcs'], tzinfo=utc).astimezone(self.tzinfo)
            elem['tz_end_date'] = parse_date(elem['sisevcs'], tzinfo=utc).astimezone(self.tzinfo)
            try:
                elem['to'] = self.process_tagesordnung(elem['silfdnr'])
            except:
                elem['ERROR'] = True
            elem['_id'] = int(elem['silfdnr'])
            self.coll.save(elem)

        return sitzungen

    def process_tagesordnung(self, silfdnr):
        """process tagesordnung for sitzung"""
        url = self.to_url %silfdnr
        print url

        r = requests.get(url)
        xml = r.text.encode('ascii','xmlcharrefreplace') 
        root = etree.fromstring(xml, parser=self.parser)

        record = {'tops' : []}

        head = {}
        for item in root[1].iterchildren():
            head[item.tag] = item.text
        record['head'] = head

        meta = {}
        for item in root[1].iterchildren():
            meta[item.tag] = item.text
        record['meta'] = meta

        for item in root[0].iterchildren():
            elem = {}
            for e in item.iterchildren():
                elem[e.tag] = e.text

            record['tops'].append(elem)

        record['_id'] = int(record['head']['silfdnr'])
        print record
        return record


sp = SitzungsParser()
sp.process()
#import pprint
#print pprint.pprint(sp.process())


