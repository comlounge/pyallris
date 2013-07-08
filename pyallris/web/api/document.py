from starflyer import Handler, asjson
import pymongo

class Document(Handler):

    @asjson()
    def get(self, did):

        document = self.app.mongodb.documents.find_one({'_id': did} )
        return document


