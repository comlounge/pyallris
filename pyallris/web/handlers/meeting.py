from starflyer import Handler

class Meeting(Handler):

    template = "meeting.html"

    def get(self, silfdnr):
        meeting = self.app.mongodb.meetings.find_one({'_id': int(silfdnr) } )
        return self.render(meeting = meeting)


