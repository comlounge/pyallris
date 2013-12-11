from starflyer import Handler, asjson
import pymongo
import datetime
import math

class Documents(Handler):

    @asjson()
    def get(self, city = "Aachen"):
        limit = min(int(self.request.args.get("limit", "10")), 50)
        offset = int(self.request.args.get("offset", "0"))
        city = city.capitalize()

        # compute default values for from and to as date objects
        date_from = datetime.date.today() - datetime.timedelta(days=365) # default is a year back
        date_to = datetime.date.today()

        # override from request if possible
        if "from" in self.request.args:
            date_from = datetime.datetime.strptime(self.request.args['from'].strip(), "%d.%m.%Y").date()
        if "to" in self.request.args:
            date_to = datetime.datetime.strptime(self.request.args['to'].strip(), "%d.%m.%Y").date()

        # convert to datetime
        tt = datetime.time(23,59)
        date_to = datetime.datetime.combine(date_to, tt)
        tt = datetime.time(00,00)
        date_from = datetime.datetime.combine(date_from, tt)

        documents = self.app.mongodb.documents.find(
            {
                'ERROR': {"$exists": False},
                'last_discussed' : {"$gte" : date_from, "$lte" : date_to},
                'city' : city,
            } 
        ).sort("last_discussed", pymongo.DESCENDING ).limit(limit).skip(offset)

        # generate metadata
        count = documents.count()
        pages = int(math.ceil(float(count)/limit))
        metadata = {
            'limit' : limit,
            'offset' : offset,
            'count' : count,
            'page_count' : pages,
        }
        # check for next link.
        args = {
            'limit' : limit,
        }
        if "to" in self.request.args:
            args['to'] = self.request.args['to']
        if "from" in self.request.args:
            args['from'] = self.request.args['from']
        if (offset + limit) <= count:
            metadata['next'] = self.url_for("api.documents", city = city.lower(), offset = limit+offset, _full = True, _append = True, **args)
        if offset != 0:
            metadata['prev'] = self.url_for("api.documents", city = city.lower(), offset = offset-limit, _full = True, _append = True, **args)
        result = {
            '_meta' : metadata,
            'results' : list(documents)
        }
        return result


