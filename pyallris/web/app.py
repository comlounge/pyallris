from starflyer import Application, URL
from sfext.mongo import mongodb
import handlers


class ALLRIS(Application):
    """a for now simple ALLRIS output application"""

    defaults = {
        'mongodb_name'  : 'ratsinfo',
    }

    routes = [
        URL("/",                    "home",         handlers.Homepage),
        URL("/meetings",            "meetings",     handlers.Meetings),
        URL("/meetings/<silfdnr>",  "meeting",      handlers.Meeting),
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

