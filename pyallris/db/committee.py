from mongogogo import *
import datetime

class Member(Schema):
    """defines a member of a committee by linking a person to a committee"""
    person = String() # id
    start_date = Date()
    end_date = Date()

class Committee(Schema):
    """a committee of any sort"""
    name = String(required = True)
    members = List(Member())

    # generic elements
    last_modified = DateTime()
    created = DateTime()
    workflow = String()
