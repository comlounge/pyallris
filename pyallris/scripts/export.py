"""

experimental exporter for some meetings with the agenda items (tops) and their documents attached

meetings = SILFDNR
agenda_items = TOPFLDNR
documents = VOLFDNR

documents are attached to agenda items via volfdnr and agenda items are attached to meetings via their toplfdnr.

"""

import pymongo
import json
import datetime
import pprint
from starflyer import AttributeMapper

def jsonconverter(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif hasattr(obj, "to_dict"):
        return obj.to_dict()
    else:
        # skip it otherwise
        return None

class Exporter():
    """export all data as JSON"""

    def __init__(self):
        """initialize the class"""

        self.db = pymongo.Connection().ratsinfo

    def export(self, amount = 10):
        """export meetings and their related content

        Meetings are not in any order.

        The structure is as follows::

        {
            'meetings' : [
                { meeting info,
                  'agenda_items: [
                    {
                        agenda item info,
                        document: {
                            document info
                        }
                    }
                  ]
            ]
        }
        """

        doc = AttributeMapper({'meetings' : []})
        meetings = self.db.meetings.find().limit(10)
        for meeting in meetings:
            ai = meeting['agenda_items'] = []
            for top in meeting['tops']:
                topdata = self.db.agenda_items.find_one({'_id' : top['tolfdnr']})
                if topdata is None:
                    continue
                ai.append(topdata)
                volfdnr = topdata.get("volfdnr", None)
                if volfdnr:
                    document = self.db.documents.find_one({'_id' : volfdnr})
                    topdata['document'] = document
            doc.meetings.append(meeting)
        print json.dumps(doc, default = jsonconverter)
            





if __name__ == "__main__":
    e = Exporter()
    e.export()
