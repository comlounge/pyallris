
import pytz
import datetime
import hashlib
import types
from pytz import timezone
utc = pytz.utc
tzinfo = timezone('Europe/Berlin')

def parse_date(s, tzinfo = utc):
    """parse dates like 20121219T160000Z"""
    year = int(s[0:4])
    month = int(s[4:6])
    day = int(s[6:8])
    hour = int(s[9:11])
    minute = int(s[11:13])
    second = int(s[13:15])
    return datetime.datetime(year, month, day, hour, minute, second, 0, tzinfo)

def update_md5(d, fields=[]):
    """computes the md5 hash from the listed ``fields`` inside the dictionary ``d``
    
    It stored the hash in the ``md5`` field inside the dict and also updates the last_updated
    field in case the old md5 and the new one differs.
    
    """
    h = hashlib.md5()
    for field in fields:
        try:
            v = d.get("field", u"")
            if type(v) == types.ListType:
                v.sort()
            s = unicode(v).encode("ascii","replace")
            h.update(s)
        except Exception, e: 
            print e
            import pdb; pdb.set_trace()
    md5 = h.hexdigest()
    if d.has_key("md5"):
        if d['md5'] != md5:
            print "CHANGED"
            d['md5'] = md5
            d['last_changed'] = datetime.datetime.now()
    else:
        d['md5'] = md5
        d['last_changed'] = datetime.datetime.now()
    return d


