from pyallris.meetings import MeetingParser

class AlsdorfMeetingParser(MeetingParser):
    """special meeting parser for alsdorf"""

    agenda_item_url = "http://ratsinfo.alsdorf.de/bi/to020.asp?selfaction=ws&template=xyz&TOLFDNR=%s"
    city = "Alsdorf"


url = "http://ratsinfo.alsdorf.de/bi/to010.asp?selfaction=ws&template=xyz&SILFDNR=%s"
base_url = "http://ratsinfo.alsdorf.de/bi/si010.asp?selfaction=ws&template=xyz&kaldatvon=%s&kaldatbis=%s"
sp = AlsdorfMeetingParser(url, base_url = base_url, db="ratsinfo")
sp.process()


