from pyallris.meetings import MeetingParser as BaseParser

class MeetingParser(BaseParser):
    """special version for herzogenrath"""
    
    URL_POSTIX = "to010.asp?selfaction=ws&template=xyz&SILFDNR=%s"
    BASE_URL_POSTFIX = "si010_j.asp?selfaction=ws&template=xyz&kaldatvon=%s&kaldatbis=%s"
