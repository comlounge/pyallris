from starflyer import Handler

class Meeting(Handler):

    template = "meeting.html"

    def get(self, silfdnr):

        meeting = self.app.mongodb.meetings.find_one({'_id': int(silfdnr) } )

        tolfdnrs = []
        for top in meeting['tops']:
            tolfdnrs.append(top['tolfdnr'])

        top_infos_raw = self.app.mongodb.agenda_items.find({'_id': {'$in' : tolfdnrs}})
        top_infos = {} 
        for top in top_infos_raw:
            top_infos[top['_id']] = top

        return self.render(meeting = meeting, top_infos = top_infos)


