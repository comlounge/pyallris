from starflyer import Handler

class Homepage(Handler):

    template = "master.html"

    def get(self):
        persons = self.app.mongodb.personen.find({'active' : "1"}).sort([('association', 1), ('last_name', 1)])
        committees = self.app.mongodb.committees.find().sort("name")
        return self.render(persons = persons, committees = committees)
