# coding=utf-8
import requests
from lxml import etree, html
from lxml.cssselect import CSSSelector
import datetime
import pytz
from pytz import timezone
utc = pytz.utc
import time
import uuid
import pprint
import utils
import argparse
import urlparse
import sys
import copy
import html2text

from base import RISParser
import re

body_re = re.compile("<?xml .*<body[ ]*>(.*)</body>") # find everything inside a body of a subdocument

TIME_MARKER = datetime.datetime(1903,1,1) # marker for no date being found

class DocumentParser(RISParser):
    """"""

    # an easy way to get there selectors is to use firefox and copy the unique selector from the dev tools
    #
    #adoption_css = CSSSelector("#rismain table.risdeco tbody tr td table.tk1 tbody tr td table.tk1 tbody tr td table tbody tr.zl12 td.text3")
    #adoption_css = CSSSelector("table.risdeco tr td table.tk1 tr td.ko1 table.tk1 tr td table tr.zl12 td.text3")
    adoption_css = CSSSelector("tr.zl12:nth-child(3) > td:nth-child(5)") # selects the td which holds status information such as "beschlossen"
    top_css = CSSSelector("tr.zl12:nth-child(3) > td:nth-child(7) > form:nth-child(1) > input:nth-child(1)") # selects the td which holds the link to the TOP with transcript
    table_css = CSSSelector(".ko1 > table:nth-child(1)") # table with info block
    attachments_css = CSSSelector("table.tk1:nth-child(23)")
    #main_css = CSSSelector("#rismain table.risdeco")

    MD5_FIELDS = ['docs', 'betreff', 'federführend']
    city = "Aachen"

    def __init__(self, url,
            tzinfo = timezone('Europe/Berlin'), 
            months = 12,
            **kwargs):
        self.utc = pytz.utc
        self.tzinfo = tzinfo
        self.consultation_list_start = False 
        super(DocumentParser, self).__init__(url, **kwargs)

        # this will be moved to the second stage
        #self.db.documents.remove()

    @classmethod
    def construct_instance(cls, args):
        """construct the parse instance"""
        bu = args.base_url
        if not bu.endswith("/"):
            bu = bu + "/"
        url = bu+"vo020.asp?VOLFDNR=%s"
        return cls(url,
            city = args.city,
            mongodb_host = args.mongodb_host,
            mongodb_port = args.mongodb_port,
            mongodb_name = args.mongodb_name,
            force = args.force
        )

    def preprocess_text(self, text):
        """preprocess the incoming text, e.g. do some encoding etc."""
        return text

    def process(self, force = True):
        """process documents"""

        # get all the ids of the documents we need to parse
     
        agenda_items = self.db.agenda_items.find({
            "city" : self.city,
        }, timeout=False)
        print "processing %s agenda items" %agenda_items.count()
        document_ids = [item['volfdnr'] for item in agenda_items if "volfdnr" in item]
        print "processing %s documents" %len(document_ids)
        #self.process_document("2567", force=True)
        #self.process_document("2535", force=True)
        #self.process_document("2536", force=True)
        #self.process_document("11057")
        #self.process_document("11199") # this has attachments
        #self.process_document("11136", True) # has some problem reading a missing TO link
        #self.process_document("2015", True) # has some problem reading a missing TO link
        #self.process_document("12405", True) # does not find geolocation
        #self.process_document("10893", True) # has last_discussed on 3.9. but last event was 17.4.
        #self.process_document("12515", True) # had the same date for 2 events in consultation list but was fixed
        self.process_document("11768", True) # had the same date for 2 events in consultation list but was fixed
        return
        #print document_ids
        for document_id in document_ids:
            self.process_document(document_id, force = self.force)
        return

    def process_document(self, document_id, force = False):
        """process a single document

        :param document_id: id of document to parse
        :param force: if True then reread the document regardless of whether 
            we have it already in the db or not
        """
        print "trying document %s:%s" %(self.city, document_id)
        found = False
        try:
            data = self.db.documents.find_one({
                '_id' : "%s:%s" %(self.city, document_id),
                'document_id' : str(document_id),
                'city' : self.city,
            })
            found = True
        except Exception, e:
            print "problem when trying to find document id %s: %s" %(document_id, e)
            # we did not find any old data, so lets create an empty one
            found = False
        if data is None:
            data = {
                '_id'            : "%s:%s" %(self.city, document_id),
                'document_id'    : document_id,
                'document_url'   : self.url %document_id,
                'last_discussed' : TIME_MARKER,            # date of last appearance in a meeting
                'created'        : datetime.datetime.now(),# for our own reference
            }
            found = False
        if found and not force: 
            print "%s already read" %document_id
            return
        url = self.url %document_id
        #print "reading", url

        self.response = response = requests.get(url)
        if "noauth" in response.url:
            print "*** no permission to read %s" %url
            print 
            return
        text = self.preprocess_text(response.text)
        doc = html.fromstring(text)

        # Beratungsfolge-Table checken
        table = self.table_css(doc)[0] # lets hope we always have this table
        self.consultation_list_start = False
        for line in table:
            headline = line[0].text
            if headline:
                headline = headline.split(":")[0].lower()
                if headline[-1]==":":
                    headline = headline[:-1]
                if headline == "betreff":
                    value = html2text.html2text(etree.tostring(line[1]))
                    data[headline] = value
                elif headline in ['status', 'verfasser', u'federführend']:
                    data[headline] = line[1].text.strip()
                elif headline == "beratungsfolge":
                    # the actual list will be in the next row inside a table, so we only set a marker
                    data = self.parse_consultation_list_headline(line, data) # for parser which have the consultation list here
                elif self.consultation_list_start:
                    data = self.parse_consultation_list(line, data) # for parser which have the consultation list in the next tr
                    self.consultation_list_start = False # set the marker to False again as we have read it
                # we simply ignore the rest (there might not be much more actually)

        # the actual text comes after the table in a div but it's not valid XML or HTML this using regex
        docs = body_re.findall(self.response.text)
        data['docs'] = docs
        data = utils.update_md5(data, self.MD5_FIELDS)
        data['city'] = self.city
        plaintext = data.get("betreff", "").lower()
        md = ""
        for d in data.get("docs"):
            plaintext = plaintext + " " + html2text.html2text(d.lower())
            md = md + "\n\n\n--------------------------------------------------------------------------------\n\n\n" + html2text.html2text(d)
        data['markdown'] = md
        streets = {} # this stores official street name => street._id
        geolocations = {}
        geolocation = None
        for street in self.streets.keys():
            if street in plaintext:
                print "found street", street
                s = self.streets[street]
                streets[s['original']] = s['_id']
                if "lat" in s:
                    geolocations[s['original']] = {'lat' : s["lat"], 'lon' : s["lng"]}
                    # we now store the location of the first street in our database for the geo index
                    if geolocation is None:
                        geolocation = {'lat' : s["lat"], 'lon' : s["lng"]}
        #data['streets'] = streets
        data['geolocations'] = geolocations
        data['geolocation'] = geolocation
        self.db.documents.save(data)
        time.sleep(1)
        return # we do attachments later, for now we save that stuff without

        # get the attachments if possible
        attachments = self.attachments_css(doc)
        if len(attachments)>0 and attachments[0][1][0].text.strip() == "Anlagen:":
            for tr in attachments[0][3:]:
                nummer = tr[1].text
                link = tr[2][0]
                href = link.attrib["href"]
                name = link.text
                # TODO: save it
        return

    def parse_consultation_list_headline(self, line, data):
        """parse the consultation list in case it is in the td next to the headline. This is the case
        for alsdorf and thus the alsdorf parser has to implement this method.

        @param line: the tr element which contains the consultation list
        @param data: the data so far
        @return data: the updated data element
        """
        self.consultation_list_start = True # mark that we found the headline, the table will be in the next line
        return data

    def parse_consultation_list(self, line, data):
        """parse the consultation list like it is for aachen. Here it is in the next line (tr) inside the first td.
        The list itself is a table which is parsed by process_consultation_list

        @param line: the tr element which contains the consultation list
        @param data: the data so far
        @return data: the updated data element
        """
        data['consultation'] = self.process_consultation_list(line[0]) # line is the tr, line[0] the td with the table inside
        dates = [m['date'] for m in data['consultation']]
        dates.append(data['last_discussed'])
        data['last_discussed'] = max(dates) # get the highest date
        self.consultation_list_start = False
        return data

    def process_consultation_list(self, elem):
        """process the "Beratungsfolge" table in elem"""
        elem = elem[0]
        # the first line is pixel images, so skip it, then we need to jump in steps of two
        amount = (len(elem)-1)/2
        result = []
        i = 0
        item = None
        for line in elem:
            if i == 0:
                i=i+1
                continue

            """
            here we need to parse the actual list which can have different forms. A complex example
            can be found at http://ratsinfo.aachen.de/bi/vo020.asp?VOLFDNR=10822
            The first line is some sort of headline with the committee in question and the type of consultation.
            After that 0-n lines of detailed information of meetings with a date, transscript and decision.
            The first line has 3 columns (thanks to colspan) and the others have 7.

            Here we make every meeting a separate entry, we can group them together later again if we want to.
            """
            # now we need to parse the actual list
            # those lists can either be two lines or 1. They either start with a date or some committee name
           
            # the first line is the committee name
            if line[1].attrib.get("class","") == "text1":
                # the order is "color/status", name of committee / link to TOP, more info
                status = line[0].attrib['title'].lower()
                # we define a head dict here which can be shared for the other lines
                # once we find another head line we will create a new one here
                item = {
                    'status'    : status,               # color coded status, like "Bereit", "Erledigt"
                    'committee' : line[1].text.strip(), # name of committee, e.g. "Finanzausschuss", unfort. without id
                }
                if len(line)>2:
                    item['action'] = line[2].text.strip(), # e.g. "Kenntnisnahme", "Entscheidung"
            else:
                # this is about line 2 with lots of more stuff to process
                # date can be text or a link with that text
                if len(line[1]) == 1: # we have a link (and ignore it)
                    print "date 1"
                    item['date'] = datetime.datetime.strptime(line[1][0].text.strip(), "%d.%m.%Y")
                else:
                    item['date'] = datetime.datetime.strptime(line[1].text.strip(), "%d.%m.%Y")
                    print item['date']
                if len(line[2]):
                    form = line[2][0] # form with silfdnr and toplfdnr but only in link (action="to010.asp?topSelected=57023")
                    item['silfdnr'] = form[0].attrib['value']
                    item['meeting'] = line[3][0].text.strip()       # full name of meeting, e.g. "A/31/WP.16 öffentliche/nichtöffentliche Sitzung des Finanzausschusses"
                else:
                    item['silfdnr'] = None # no link to TOP. should not be possible but happens (TODO: Bugreport?)
                    item['meeting'] = line[3].text.strip()   # here we have no link but the text is in the TD directly
                    item['PYALLRIS_WARNING'] = "the agenda item in the consultation list on the web page does not contain a link to the actual meeting"
                    #print "WARNING:", item['PYALLRIS_WARNING']
                item['decision'] = line[4].text.strip()         # e.g. "ungeändert beschlossen"
                toplfdnr = None
                if len(line[6]) > 0:
                    form = line[6][0]
                    toplfdnr = form[0].attrib['value']
                item['toplfdnr'] = toplfdnr                     # actually the id of the transcript 
                result.append(item)

                # in case we have more consultations for the same committee, we will copy the item now so we have a new object to work on and don't overwrite data (like the date)
                item = copy.copy(item)
            i=i+1
        return result
            

if __name__ == "__main__":
    #url = "http://ratsinfo.aachen.de/bi/vo020.asp?VOLFDNR=%s"
    #p = DocumentParser(url)
    #p.process(force = True)

    p = DocumentParser.from_args()
    p.process()
    sys.exit()


    parser = argparse.ArgumentParser(description='process document')
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
    parser.add_argument('-f', '--force', action = "store_true", help='should documents be parsed again even if they are already in the database?')
    args = parser.parse_args()
    bu = args.base_url
    if not bu.endswith("/"):
        bu = bu + "/"
    url = bu+"vo020.asp?VOLFDNR=%s"
    print args
    # TODO: try to import individual parsers for the given city
    sp = DocumentParser(url,
        city = args.city,
        mongodb_host = args.mongodb_host,
        mongodb_port = args.mongodb_port,
        mongodb_name = args.mongodb_name,
        force = args.force
    )
    sp.process()



