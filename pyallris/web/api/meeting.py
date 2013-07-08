from starflyer import Handler, asjson
import pymongo

class Meeting(Handler):

    @asjson()
    def get(self, mid):

        meeting = self.app.mongodb.meetings.find_one({'_id': int(mid) } )

        tolfdnrs = []
        for top in meeting['tops']:
            tolfdnrs.append(top['tolfdnr'])
        print tolfdnrs

        # get a table with all the details
        top_infos_raw = self.app.mongodb.agenda_items.find({'_id': {'$in' : tolfdnrs}})
        top_infos = {} 
        for top in top_infos_raw:
            top_infos[top['_id']] = top
            if "volfdnr" in top:
                top['document_url'] = self.url_for("api.document", did = top['volfdnr'], _full=True)

        # now create a new list with all the TOP information
        new_tops = []
        for top in meeting['tops']:
            tolfdnr = top['tolfdnr']
            if tolfdnr in top_infos:
                new_tops.append(top_infos[tolfdnr])
            else:
                new_tops.append(top)
        meeting['tops'] = new_tops
        return meeting


