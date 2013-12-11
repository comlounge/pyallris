from starflyer import Handler, asjson
import pymongo

class Meetings(Handler):

    template = "meetings.html"

    def process(self, meetings, city = "Aachen"):
        """process all the meetings and add additional information eventually"""
        result = []
        for meeting in meetings:
            meeting['url'] = self.url_for("api.meeting", city = city.lower(), mid = meeting['silfdnr'], _full=True)
            result.append(meeting)
        return result

    @asjson()
    def get(self, city = "Aachen"):
        """return a certain amount of meetings"""
        limit = max(int(self.request.args.get("l", "10")), 50)
        print city
        meetings = self.app.mongodb.meetings.find({
            'ERROR': {"$exists": False},
            'city' : city.capitalize(),
        } ).sort("start_date", pymongo.DESCENDING ).limit(limit)
        return self.process(meetings, city = city)


