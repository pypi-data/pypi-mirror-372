import re

from typing import Optional, List

from .element import XMLElement
from .attribute import XMLAttribute
from .text import XMLTextElement

class XMLParser:
    def __init__(self):
        pass

    @staticmethod
    def parse_elements(xml_string: str) -> List[XMLElement]:
        if (not xml_string):
            return []

        elements = []

        element_tree = [] 

        pattern = re.compile(r'<([^>]+)>|([^<]+)')
        matches = pattern.finditer(xml_string)
       
        for match in matches:
            # The content inside the angle brackets (<...>)
            tag_content = match.group(1)
            # The text content between tags
            text_content = match.group(2)

            if (tag_content and tag_content.strip()):
                tag_is_close = (tag_content.startswith("/") or tag_content.endswith("/"))

                name_match = re.search(r'^/?([^\s/]+)', tag_content) 
                # <name ... | </name>
                tag_name = name_match.group(1) if name_match else None

                if (tag_name):
                    # key="value"
                    attr_pattern = re.compile(r'(\S+)=["\'](.+?)["\']')
                    attributes = []
                    for k, v in {k: v for k, v in attr_pattern.findall(tag_content)}.items():
                        attributes.append(XMLAttribute(name=k, value=v))

                    # Create xml element
                    xml_element = XMLElement(
                        name=tag_name, 
                        attributes=attributes,
                        is_closed=False,
                    )


                    if (len(element_tree) > 0):
                        last_xml_element = element_tree[-1]

                        if (last_xml_element.name == tag_name):
                            if (tag_is_close):
                                # Close tag of last element
                                last_xml_element.is_closed = True

                                if (len(element_tree) > 1):
                                    # Get and remove last element and put to previous as a child
                                    element_tree[-2].add_child(element_tree.pop())
                                else:
                                    # Add last full closed element to stack
                                    elements.append(element_tree.pop())
                        else:
                            element_tree.append(xml_element)
                            if (tag_is_close):
                                # Close tag of last element
                                element_tree[-1].is_closed = True
                                # Get and remove last element and put to previous as a child
                                element_tree[-2].add_child(element_tree.pop())
                    else:
                        element_tree.append(xml_element)

            elif (text_content):
                strip_text = text_content.strip()
                if (strip_text):
                    element_tree[-1].add_child(XMLTextElement(text=strip_text))

        # Add not closed elements
        if (len(element_tree) > 0):
            # Add not closed element as new element
            elements.append(element_tree.pop(0))
            # and add every other elements to that open element as a child
            for i in range(len(element_tree)):
                elements[-1].add_child(element_tree.pop(0))

        return elements 

