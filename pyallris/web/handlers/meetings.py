from starflyer import Handler

class Meetings(Handler):

    template = "meetings.html"

    def get(self):
        meetings = self.app.mongodb.meetings.find({'ERROR': {"$exists": False} } )
        return self.render(meetings = meetings)


