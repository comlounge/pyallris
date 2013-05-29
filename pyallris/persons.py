# coding=utf-8
from base import RISParser, ParseError
from lxml import etree
from lxml.cssselect import CSSSelector
import urlparse
import datetime


class PersonParser(RISParser):
    """parser to parse the list of person objects in the system. For each person we
    store name, address etc. but also their memberships information in committees. 

    As URL you should give the main list of persons in the system such as

    http://ratsinfo.aachen.de/bi/kp041.asp?showAll=true&selfaction=ws&template=xyz

    important is showAll=True in order to get past memberships as well

    """
    pasel = CSSSelector('input[name="FRLFDNR"]')
    frsel = CSSSelector('input[name="PALFDNR"]')
    ausel = CSSSelector('input[name="AULFDNR"]')

    unknown_groups = {} # in case we get an unknown group we will store it here. This is group_name -> group_id

    def dictify(self, node):
        """create a dictionary from a node by iterating through it and
        using the tags as keys and text values as dict values
        """
        elem = {}
        for e in node.iterchildren():
            elem[e.tag] = e.text
        return elem

    def __call__(self):
        """start processing person objects by starting from the person list

        This will start with the base URL and will go from there. 

        :return: 
        
        """
        tree = self.parse_xml(self.url)
        personen = []

        # element 0 is the special block
        # element 1 is the list of persons
        for node in tree[1].iterchildren():
            elem = self.dictify(node)
            person = dict(
                _id = elem['kplfdnr'],
                association = elem['kppartei'],           # can also be Verein etc. so maybe rename it to 
                gdat = elem['kpgdat'],                # ??
                sdat = elem['kpsdat'],                # ??
                active = elem['aktiv'],             # what is what? 0 = not active?
                salutation = elem['antext1'],       # Herr
                salutation_alt = elem['antext3'],   # Sehr geehrter Herr
                last_name = elem['adname'],
                first_name = elem['advname'],
                title = elem['adtit'],
                adename = elem['adename'],          # ??
                street = elem['adstr'],
                city = elem['adort'],
                zip = elem['adplz'],
                city_part = elem['adoteil'],
                email = elem['ademail'],
                email_alt = elem['ademail2'],
                homepage = elem['adwww1'],
                homepage_alt = elem['adwww2'],
                phone = elem['adtel'],
                phone2 = elem['adtel2'],
                phone3 = elem['adtel3'],
                phone4 = elem['adtel4'],
                phone5 = elem['adtel5'],
                phone6 = elem['adtel6'],
                fax = elem['adfax'],
                fax_alt = elem['adfax2'],
                url = elem['link_kp'],
                full_url = urlparse.urljoin(self.base_url, elem['link_kp']),
            )

            # now retrieve person details such as committee memberships etc.
            # we also get the age (but only that, no date of birth)
            if elem['link_kp'] is not None:
                # we only get details on entries we also have a link for
                person = self.get_person_details(person)
            else:
                print "** WARNING: person %s %s has no link" %(person['first_name'], person['last_name'])
                print
            personen.append(person)
            self.db.personen.remove()   # remove old stuff for now
            self.db.personen.insert(personen)

        return personen
       
    def get_person_details(self, person):
        """retrieve the person details, esp. the membership information via
        the corresponding HTML page

        :param person: dictionary with at least the _id 
        """
        url = urlparse.urljoin(self.base_url, "kp020.asp")+"?KPLFDNR=%s&history=true" %person['_id']
        tree = self.parse_html(url)

        memberships = [] # list of dicts with key (membership type, group_id, groupname, start, end)

        # maps name of type to form name and membership type
        type_map = {
            u'Rat der Stadt' : {'mtype' : 'parliament', 'field' : 'PALFDNR'},
            u'Fraktion' : {'mtype' : 'organisation', 'field' : 'FRLFDNR'},
            u'Ausschüsse' : {'mtype' : 'committee', 'field' : 'AULFDNR'},
        }

        # obtain the table with the membership list via a simple state machine
        mtype = "parliament"
        old_group_id = None         # for checking if it changes
        old_group_name = None       # for checking if it changes
        group_id = None             # might break otherwise
        table = tree.xpath('//*[@id="rismain"]/table[2]')[0]
        for line in table.findall("tr"):
            if line[0].tag == "th":
                what = line[0].text.strip()
                if what not in type_map:
                    print "** unknown type ",what
                    raise Exception
                mtype = type_map[what]['mtype']
                field = type_map[what]['field']
            else:
                if "Keine Information" in line.text_content():
                    # skip because no content is available
                    continue
                
                # first get the name of group
                group_name = line[1].text_content()

                # now the first col might be a form with more useful information which will carry through until we find another one
                # with it. we still check the name though
                form = line[0].find("form")
                if form is not None:
                    group_id = int(form.find("input[@name='%s']" %field).get("value"))
                    old_group_id = group_id # remember it for next loop
                    old_group_name = group_name # remember it for next loop 
                else:
                    # we did not find a form. We assume that the old group still applies but we nevertheless check if
                    # the groupname is still the same
                    if old_group_name != group_name:
                        print "** WARNING: group name differs but we didn't get a form with new group id: group name=%s, old group name=%s, group_id=%s" %(group_name, 
                            old_group_name, old_group_id)
                        print "** URL:", url
                        print "** creating custom group"
                        if group_name in self.unknown_groups:
                            group_id = self.unknown_groups[group_name]
                            print "** found one with group_id", group_id
                        else:
                            group_id = 9999999+len(self.unknown_groups.keys())
                            self.unknown_groups[group_name] = group_id
                            print "** created new group with id", group_id
                        print
                        

                # TODO: create a list of functions so we can index them somehow
                function = line[2].text_content()
                raw_date = line[3].text_content()

                # parse the date information
                if "seit" in raw_date:
                    dparts = raw_date.split()
                    start_date = None
                    end_date = datetime.datetime.strptime(dparts[-1], "%d.%m.%Y")
                elif "Keine" in raw_date:
                    # no date information available
                    start_date = end_date = None
                else:
                    dparts = raw_date.split()
                    start_date = datetime.datetime.strptime(dparts[0], "%d.%m.%Y")
                    end_date = datetime.datetime.strptime(dparts[-1], "%d.%m.%Y")

                membership = dict(
                    membership_type = mtype,
                    group_id = group_id, 
                    group_name = group_name,
                    start_date = start_date,
                    end_date = end_date,
                )
                memberships.append(membership)
            
        person['memberships'] = memberships
        return person

if __name__ == "__main__":

    base_url = "http://ratsinfo.aachen.de/bi/"
    # this needs to be this long as it's a search result it seems
    url = "http://ratsinfo.aachen.de/bi/kp041.asp?template=xyz&selfaction=ws&showAll=true&PALFDNRM=1&kpdatfil=&filtdatum=filter&kpname=&kpsonst=&kpampa=99999999&kpfr=99999999&kpamfr=99999999&kpau=99999999&kpamau=99999999&searchForm=true&search=Suchen"

    import pprint

    p = PersonParser(url, base_url)
    pprint.pprint(p())
    print p.unknown_groups
    #person = {'_id' : 10}
    #pprint.pprint(p.get_person_details(person))




















