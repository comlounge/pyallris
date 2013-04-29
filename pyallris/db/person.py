from mongogogo import *
from base import Base, Website, Address, DayOfBirth

class Person(Base):
    """a person"""
    first_name = String(required = True)
    last_name = String(required = True)
    title = String()            # academic title
    sex = String(required = True)              # m/w
    profession = String()
    email = String()
    phone = String()
    fax = String()
    facebook = String()
    twitter = String()
    websites = List(Website())      # all the rest

    day_of_birth    = DayOfBirth()


