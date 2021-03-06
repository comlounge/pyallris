from lxml import etree
from lxml.cssselect import CSSSelector
import requests
import urlparse
import datetime
import hashlib
from base import *

class CommitteeParser(RISParser):
    """parser for committee data"""

    linesel = CSSSelector('table.tl1 tr.zl11, table.tl1 tr.zl12')
    ausel = CSSSelector('input[name="AULFDNR"]')
    silfsel = CSSSelector('input[name="SILFDNR"]')
    kpsel = CSSSelector('input[name="KPLFDNR"]')

    def __call__(self):
        """process the HTML source"""
        result = []

        tree = self.parse_html(self.url)

        for i in self.linesel(tree):
            tds = i.findall("td")
            if len(tds) == 1:
                # from this line on we only get retired committees and we skip them now.
                break
            if len(tds) == 8: 
                
                # base data
                form = tds[0]
                try:
                    committee_id = int(self.ausel(form)[0].get("value"))
                except:
                    print "found not form in table row"
                    continue
                url = urlparse.urljoin(self.base_url, tds[1][0].get("href"))
                name = tds[1][0].text.strip()
                print "processing committee", name

                # additional data which we can also derive from other sources
                members = tds[2].text
                try:
                    members = int(members)
                except ValueError:
                    members = None

                last_session = tds[4].text
                next_session = tds[6].text

                if last_session is not None:
                    last_session = datetime.datetime.strptime(last_session, "%d.%m.%Y")

                if next_session is not None:
                    next_session = datetime.datetime.strptime(next_session, "%d.%m.%Y")

                # try to get last session number
                silfs = self.silfsel(i)
                if len(silfs) == 1:
                    silfdnr = silfs[0].get("value")
                else:
                    silfdnr = None
                    
                record = dict(
                    _id = committee_id,
                    name = name,
                    members = members,
                    last_session = last_session,
                    next_session = next_session,
                    last_session_id = silfdnr,
                    url = url
                )


                # now get the member list
                data = self.process_committee(url, name=name)
                record.update(data)
                result.append(record)
            self.db.committees.remove()
            self.db.committees.insert(result)
        return result

    def process_committee(self, url, name = u''):
        """process one committee start page

        :param url: url of the committee page
        :param name: name of the committee, only used for debugging purposes
        
        """
        tree = self.parse_html(url)

        members = []
        data = {}

        def check_line(line):
            """checks what a line can be and returns a tuple containing
            the type and the value, e.g. ``('email' , 'some@example.com')``

            If it's not a defined field it will return the type ``text``

            :param line: the ``Element`` containing the tr
            :return: tuple containing type and value
            """

            elems = line.findall("td")
            if len(elems)==1:
                t = elems[0].text
                if t is None or len(t.strip()) < 2:
                    return None, None
                return "text", elems[0].text

            icon = elems[0][0].get("src")
            if icon=="images/telefon.gif":
                return "telefon", elems[1][0].text
            elif icon=="images/fax.gif":
                return "fax", elems[1][0].text
            elif icon=="images/email.gif":
                return "email", elems[1][0].text
            elif icon=="images/www.gif":
                return "url", elems[1][0].text
            return None, None

        contact_table = tree.xpath('//*[@id="rismain"]/table[1]/tr/td/table')[0]
        members_table = tree.xpath('//*[@id="rismain"]/table[3]')[0]

        # get contact
        address = {'lines' : []}
        lines = contact_table.findall("tr")
        address['salutation'] = lines[0][2].text   # this seems to be salutation or department
        address['name'] = lines[1][0].text         # this seems to be fixed
        for line in lines[2:]:
            typ, value = check_line(line)
            if typ is None:
                continue
            elif typ=="text":
                address['lines'].append(value)
            else:
                address[typ] = value

        data['address'] = address

        # get the members (we only need the ids and the start dates)
        all_lines = members_table.findall("tr")
        if len(all_lines)==4:
            print "    skipping empty committee %s at %s" %(name, url)
            return {}
        for line in members_table.findall("tr")[2:-1]:
            pline = self.kpsel(line)
            if len(pline)==0:
                #person_id = line[2]
                print "    skipping member without link"
                continue
            else:
                person_id = int(pline[0].get("value"))
            if line[-1].text is not None and line[-1].text!="":
                start_date = datetime.datetime.strptime(line[-1].text, "%d.%m.%Y")
            else:
                start_date = None
            members.append({
                'person_id' : person_id,
                'start_date' : start_date
            })

        data['members'] = members
        return data

if __name__ == "__main__":

    base_url = "http://ratsinfo.aachen.de/bi/"
    url = "http://ratsinfo.aachen.de/bi/au010.asp?SORTVON=0&SORTBIS=190"

    p = CommitteeParser(url, base_url)
    p()














