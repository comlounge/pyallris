from pyallris.agenda_items import AgendaItemParser

class AlsdorfAgendaItemParser(AgendaItemParser):
    """special agenda item parser for alsdorf"""

    city = "Alsdorf"


url = "http://ratsinfo.alsdorf.de/bi/to020.asp?selfaction=ws&template=xyz&TOLFDNR=%s"
sp = AlsdorfAgendaItemParser(url, db="ratsinfo")
sp.process()


