from starflyer import Module, URL

import meetings
import meeting
import document
import documents

class ApiModule(Module):
    """handles everything regarding barcamps"""

    name = "api"

    routes = [
        URL("/meetings", "meetings", meetings.Meetings),  # list of the last x meetings by date
        URL("/meetings/<mid>", "meeting", meeting.Meeting),  # one meetings with all the details
        URL("/documents", "documents", documents.Documents),  # one document with all the details
        URL("/documents/<did>", "document", document.Document),  # one document with all the details
        URL("/<city>/meetings", "meetings", meetings.Meetings),  # list of the last x meetings by date
        URL("/<city>/meetings/<mid>", "meeting", meeting.Meeting),  # one meetings with all the details
    ]

api_module = ApiModule(__name__)

