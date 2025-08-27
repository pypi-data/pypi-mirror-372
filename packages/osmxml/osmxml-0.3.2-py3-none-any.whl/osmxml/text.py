from .element import XMLElement

class XMLTextElement(XMLElement):
    def __init__(self, text: str):
        super().__init__(name="")

        self._text = text

    @property
    def text(self):
        return self._text 

    @text.setter
    def text(self, text):
        self._text = text 


    def to_string(self):
        return self.make_string(raw=False)

    def to_raw_string(self):
        return self.make_string(raw=True)

    def make_string(self, raw=False):
        return self.text

    def __str__(self):
        return self.make_string(raw=True)

    def __repr__(self):
        repr = 'XMLTextElement(text="{text}")'
        repr = repr.format(text=self.text)
        return repr
    
