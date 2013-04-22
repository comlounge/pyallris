import requests
from lxml import objectify, etree
import pymongo
import datetime
import pytz
from pytz import timezone

"""

holt die Sitzungen eines kompletten Jahres bzw. eines Zeitraums

Originalseite: http://ratsinfo.aachen.de/bi/si010.asp?kaldatvon=01.01.2012&kaldatbis=31.12.2012

"""

utc = pytz.utc
tzinfo = timezone('Europe/Berlin')

coll = pymongo.Connection().ratsinfo.tos

url = "http://ratsinfo.aachen.de/bi/si010.asp?selfaction=ws&template=xyz&kaldatvon=01.01.2012&kaldatbis=31.12.2012"

parser = etree.XMLParser(recover=True)

r = requests.get(url)
xml = r.text.encode('ascii','xmlcharrefreplace') 
root = objectify.fromstring(xml, parser=parser)

def parse_date(s, tzinfo = utc):
    """parse dates like 20121219T160000Z"""
    year = int(s[0:4])
    month = int(s[4:6])
    day = int(s[6:8])
    hour = int(s[9:11])
    minute = int(s[11:13])
    second = int(s[13:15])
    return datetime.datetime(year, month, day, hour, minute, second, 0, tzinfo)

def print_tree(t, level=0):
    print level*"    ", t.tag, t.text
    for child in t.getchildren():
        print_tree(child, level+1)

sitzungen = []
for item in root[1].iterchildren():
    elem = {}
    for e in item.iterchildren():
        elem[e.tag] = e.text

    elem['start_date'] = parse_date(elem['sisbvcs'])
    elem['end_date'] = parse_date(elem['sisevcs'])
    elem['tz_start_date'] = parse_date(elem['sisbvcs'], tzinfo=utc).astimezone(tz)
    elem['tz_end_date'] = parse_date(elem['sisevcs'], tzinfo=utc).astimezone(tz)

    sitzungen.append(elem)


import pprint
pprint.pprint(sitzungen)
