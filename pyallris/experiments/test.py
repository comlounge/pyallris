import requests
from lxml import objectify, etree
import pymongo


"""

holt die TOPs einer einzelnen Sitzung mit Nr. 2767

Originalseite: http://ratsinfo.aachen.de/bi/to010.asp?SILFDNR=2767

"""

coll = pymongo.Connection().ratsinfo.tos

url = "http://ratsinfo.aachen.de/bi/to010.asp?selfaction=ws&template=xyz&SILFDNR=2767"

r = requests.get(url)
xml = r.text.encode('ascii','xmlcharrefreplace') 
root = objectify.fromstring(xml)

# our full record
record = {'tops' : []}

# parse head
head = {}
for item in root['head'].iterchildren():
    head[item.tag] = item.text
record['head'] = head

meta = {}
for item in root['special'].iterchildren():
    meta[item.tag] = item.text
record['meta'] = meta

for item in root['list'].iterchildren():
    elem = {}
    for e in item.iterchildren():
        elem[e.tag] = e.text

    record['tops'].append(elem)

record['_id'] = int(record['head']['silfdnr'])
import pprint
pprint.pprint(record)
#coll.save(record)
