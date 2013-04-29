from mongogogo import *

class Website(Schema):
    """describes a location on the web"""
    url = String()
    name = String()             # e.g. Homepage, Blog

class Base(Schema):
    """base schema"""

    last_modified = DateTime()
    created = DateTime()
    workflow = String()

class Address(Schema):
    """defines an address. All information can be optional"""

    street = String()               # and number
    zip = String()
    city = String()
    country = String()

class DayOfBirth(Schema):
    """defines a day of birth"""

    day = Number()
    month = Number()
    year = Number(required = True)     # at least the year should be given if it's given at all

