# coding=utf-8
from pyallris.documents import DocumentParser as BaseParser

class DocumentParser(BaseParser):
    """special document parser for Staedteregion Aachen"""


    def preprocess_text(self, text):
        """remove the <?xml encoding line if present as lxml cannot deal with it"""
        lines = text.split("\n")
        if "<?xml" in lines[0]:
            return "\n".join(lines[1:])
        else:
            return "\n".join(lines)

    def before_save(self, data):
        """set the geolocation of the sr-haus"""
        loc = {
            'name' : u'Städteregionshaus',
            'lat' : 50.76892691,
            'lon' : 6.09773773
        }
        geolocations = [loc]
        geolocation = {
            'lat' : 50.76892691,
            'lon' : 6.09773773
        }
        data['geolocation'] = geolocation
        data['geolocations'] = geolocations

        return data
