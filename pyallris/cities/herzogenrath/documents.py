from pyallris.documents import DocumentParser as BaseParser

class DocumentParser(BaseParser):
    """special document parser for wuerselen"""


    def preprocess_text(self, text):
        """remove the <?xml encoding line if present as lxml cannot deal with it"""
        print "proprecessingg"
        lines = text.split("\n")
        if "<?xml" in lines[0]:
            return "\n".join(lines[1:])
        else:
            return "\n".join(lines)

