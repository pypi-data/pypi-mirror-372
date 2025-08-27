from typing import Optional, List

from .element import XMLElement
from .attribute import XMLAttribute
from .text import XMLTextElement

class XMLStreamParser:
    def __init__(self):
        self._element_buffer = []
        self._leftovers = ""

        self._current_element = None
        self._current_attribute = None
    
    def _get_symbol(self, symbol: str) -> bool:
        return self._leftovers.startswith(symbol)
    
    def _get_text(self) -> tuple[bool, str]:
        if self._leftovers[0] in "<>":
            return False, None
        
        i = 0
        while i < len(self._leftovers) and self._leftovers[i] not in "<> ":
            i += 1
        
        text = self._leftovers[:i]
        return True, text
    
    def _consume_symbol(self, symbol: str) -> bool:
        if self._leftovers.startswith(symbol):
            self._leftovers = self._leftovers[len(symbol):]
            return True
        return False
    
    def _consume_text(self, text) -> bool:
        if self._leftovers.startswith(text):
            self._leftovers = self._leftovers[len(text):]
            return True
        return False
    
    def _consume_identation(self) -> bool:
        while len(self._leftovers) > 0:
            if self._leftovers[0] in [" ", "\n", "\t"]:
                self._leftovers = self._leftovers[1:]
            else:
                break

    def _is_last_element_closed(self) -> bool:
        return self._element_buffer[-1].is_closed


    def parse(self, xml_string: str) -> List[XMLElement]:
        if (not xml_string):
            return []
        
        self._leftovers += xml_string

        if (len(self._element_buffer) == 0) or (self._is_last_element_closed()):
            self._consume_identation()

            if (self._get_symbol("<")):
                
                # Closing element
                if (self._get_symbol("/")):
                    # Closed element
                    self._consume_symbol("/")
                    name = self._get_text()
                    self._consume_symbol(">")
                    return self._element_buffer.pop()
        else:
            # Continue parsing current element
            pass


