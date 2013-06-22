from starflyer import Handler

class Sitzungen(Handler):

    template = "sitzungen.html"

    def get(self):
        sitzungen = self.app.mongodb.sitzungen.find()
        return self.render(sitzungen = sitzungen)


