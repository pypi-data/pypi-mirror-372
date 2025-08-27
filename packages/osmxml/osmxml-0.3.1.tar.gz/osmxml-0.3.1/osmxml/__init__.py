__version__ = "0.3.1"
__author__ = "osmiumnet"

from .xml import XML
from .element import XMLElement
from .attribute import XMLAttribute
from .text import XMLTextElement
from .parser import XMLParser
#from .stream_parser import XMLStreamParser

__all__ = [
    "XML",
    "XMLElement",
    "XMLAttribute",
    "XMLTextElement",
    "XMLParser",
    #"XMLStreamParser",
]
