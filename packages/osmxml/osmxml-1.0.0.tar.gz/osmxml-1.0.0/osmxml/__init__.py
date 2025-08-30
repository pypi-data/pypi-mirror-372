__version__ = "1.0.0"
__author__ = "osmiumnet"

from .xml import XML
from .element import XMLElement
from .attribute import XMLAttribute
from .text import XMLTextElement
from .parser import XMLParser

__all__ = [
    "XML",
    "XMLElement",
    "XMLAttribute",
    "XMLTextElement",
    "XMLParser",
]
