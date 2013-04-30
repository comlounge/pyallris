
from base import RISParser
from lxml import etree
import urlparse


class PersonParser(RISParser):
    """parser to parse the list of person objects in the system. For each person we
    store name, address etc. but also their memberships information in committees. 

    As URL you should give the main list of persons in the system such as

    http://ratsinfo.aachen.de/bi/kp041.asp?showAll=true&selfaction=ws&template=xyz

    important is showAll=True in order to get past memberships as well

    """

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
            print person

            # now retrieve person details such as committee memberships etc.
            # we also get the age (but only that, no date of birth)
            details = self.get_person_details(person)
       
    def get_person_details(self, person):
        """retrieve the person details, esp. the membership information via
        the corresponding HTML page

        :param person: dictionary with at least the _id 
        """
        url = urlparse.urljoin(self.base_url, "kp020.asp")+"?KPLFDNR=%s&history=true" %person['_id']
        print url
        tree = self.parse_html(url)

        memberships = [] # list of tuples (membership type, group_id, groupname, start, end)

        # obtain the table with the membership list via a simple state machine
        mtype = "council"
        table = tree.xpath('//*[@id="rismain"]/table[2]')[0]
        for line in table.findall("tr"):
            if line[0].tag == "th":
                print "TH"
            else:
                print etree.tostring(line)





if __name__ == "__main__":

    base_url = "http://ratsinfo.aachen.de/bi/"
    # this needs to be this long as it's a search result it seems
    url = "http://ratsinfo.aachen.de/bi/kp041.asp?template=xyz&selfaction=ws&showAll=true&PALFDNRM=1&kpdatfil=&filtdatum=filter&kpname=&kpsonst=&kpampa=99999999&kpfr=99999999&kpamfr=99999999&kpau=99999999&kpamau=99999999&searchForm=true&search=Suchen"

    import pprint

    p = PersonParser(url, base_url)
    pprint.pprint(p())



















