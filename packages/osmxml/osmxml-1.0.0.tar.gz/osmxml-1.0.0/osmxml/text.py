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


    def to_string(self, raw=True) -> str:
        if (raw):
            return self._escape_characters(self.text)
        return self.text

    # Converting special characters into their safe, equivalent XML entities
    def _escape_characters(self, text: str) -> str:
        escaped_text = text.replace("&", "&amp;")
        escaped_text = escaped_text.replace("<", "&lt;")
        escaped_text = escaped_text.replace(">", "&gt;")
        escaped_text = escaped_text.replace('"', "&quot;")
        escaped_text = escaped_text.replace("'", "&apos;")

        return escaped_text

    def __str__(self):
        return self.to_string(raw=True)

    def __repr__(self):
        repr = 'XMLTextElement(text="{text}")'
        repr = repr.format(text=self.text)
        return repr
    
