import requests
from lxml import objectify, etree
import pymongo
import datetime
import pytz

"""

holt den Teil einer Mitschrift zu einem TOP

Original: http://ratsinfo.aachen.de/bi/to020.asp?TOLFDNR=52682&options=8

"""

url = "http://ratsinfo.aachen.de/bi/to020.asp?TOLFDNR=52682&options=8&selfaction=ws&template=xyz"

parser = etree.XMLParser(recover=True)
r = requests.get(url)
xml = r.text.encode('ascii','xmlcharrefreplace') 
root = objectify.fromstring(xml, parser=parser)

def print_tree(t, level=0):
    print level*"    ", t.tag, t.text
    for child in t.getchildren():
        print_tree(child, level+1)

print_tree(root)
