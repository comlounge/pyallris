from starflyer import Handler
import pymongo

class Meetings(Handler):

    template = "meetings.html"

    def get(self):
        meetings = self.app.mongodb.meetings.find({'ERROR': {"$exists": False} } ).sort("start_date", pymongo.DESCENDING )
        return self.render(meetings = meetings)


