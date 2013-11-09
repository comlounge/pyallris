from pyallris.documents import DocumentParser as BaseParser
import argparse

class DocumentParser(BaseParser):
    """special document parser"""

    def preprocess_text(self, text):
        """remove the <?xml encoding line if present as lxml cannot deal with it"""
        lines = text.split("\n")
        if "<?xml" in lines[0]:
            return "\n".join(lines[1:])
        else:
            return "\n".join(lines)

    def parse_consultation_list_headline(self, line, data):
        """parse the consultation list for alsdorf"""
        data['consultation'] = self.process_consultation_list(line[1]) # consultation list table is in the next td
        dates = [m['date'] for m in data['consultation']]
        dates.append(data['last_discussed'])
        data['last_discussed'] = max(dates) # get the highest date
        print data['last_discussed']
        self.consultation_list_start = False
        return data

if __name__ == "__main__":
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
    args = parser.parse_args()
    bu = args.base_url
    if not bu.endswith("/"):
        bu = bu + "/"
    url = bu+"vo020.asp?VOLFDNR=%s"
    sp = DocumentParser(url,
        city = args.city,
        mongodb_host = args.mongodb_host,
        mongodb_port = args.mongodb_port,
        mongodb_name = args.mongodb_name,
    )
    sp.process()

