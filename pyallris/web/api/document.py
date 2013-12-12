from starflyer import Handler, asjson
import pymongo

class Document(Handler):

    @asjson()
    def get(self, did, city = "aachen"):

        document = self.app.mongodb.documents.find_one({
            'document_id': did,
            'city' : city,
        })
        return document


