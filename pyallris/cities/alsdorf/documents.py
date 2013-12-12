from pyallris.documents import DocumentParser as BaseParser

class DocumentParser(BaseParser):
    """special document parser for alsdorf"""


    def preprocess_text(self, text):
        """remove the <?xml encoding line if present as lxml cannot deal with it"""
        lines = text.split("\n")
        if "<?xml" in lines[0]:
            return "\n".join(lines[1:])
        else:
            return "\n".join(lines)

    def noparse_consultation_list_headline(self, line, data):
        """parse the consultation list for alsdorf"""
        data['consultation'] = self.process_consultation_list(line[1]) # consultation list table is in the next td
        dates = [m['date'] for m in data['consultation']]
        dates.append(data['last_discussed'])
        data['last_discussed'] = max(dates) # get the highest date
        self.consultation_list_start = False
        return data

