from starflyer import Application, URL
from sfext.mongo import mongodb
import handlers


class ALLRIS(Application):
    """a for now simple ALLRIS output application"""

    defaults = {
        'mongodb_name'  : 'ratsinfo',
    }

    routes = [
        URL("/",                "home",         handlers.Homepage),
        URL("/sitzungen",       "sitzungen",    handlers.Sitzungen),
        #URL("/p",               "persons",      handlers.PersonOverview),
        #URL("/p/<pid>",         "person",       handlers.PersonDetails),
        #URL("/c",               "committees",   handlers.CommitteeOverview),
        #URL("/c/<cid>",         "committee",    handlers.CommitteeDetails),
    ]

    modules = [
        mongodb(mongodb_name = "ratsinfo"),
    ]


def app(config, **local_config):
    """return the application"""
    app = ALLRIS(__name__, local_config)
    if app.config.debug:
        from werkzeug import DebuggedApplication
        return DebuggedApplication(app)
    return app

