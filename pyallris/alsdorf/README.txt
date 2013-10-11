how to update the mongo db
==========================

db.documents.update({"city" : {$exists: false}}, {$set: {city: "Aachen"}}, false, true);
db.meetings.update({"city" : {$exists: false}}, {$set: {city: "Aachen"}}, false, true);
db.agenda_items.update({"city" : {$exists: false}}, {$set: {city: "Aachen"}}, false, true);
