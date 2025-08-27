import unittest

from osmxml import XMLParser
from osmxml import XMLElement
from osmxml import XMLTextElement

class TestParser(unittest.TestCase):
    def test_parse_number(self):
        xml_data = """
            <note>
              <to>Tove</to>
              <from>Jani</from>
              <heading>Reminder</heading>
              <body>Don't forget me this weekend!</body>
            </note>
            """

        elements = XMLParser.parse_elements(xml_data)
       
        self.assertEqual(len(elements), 1)


        xml_data = """
            <book id="12345" type="fiction">
              <title>The Great Gatsby</title>
              <author>F. Scott Fitzgerald</author>
            </book>
            """

        elements = XMLParser.parse_elements(xml_data)
       
        self.assertEqual(len(elements), 1)


        xml_data = """
            <message>
              Hello, I am a 
              <b>message</b> with some 
              <i>bold</i> and 
              <i>italic</i> words.
            </message>
            """

        elements = XMLParser.parse_elements(xml_data)
       
        self.assertEqual(len(elements), 1)


        xml_data = """
            <product id="P101">
                <name>Laptop</name>
                <price currency="USD">1200.00</price>
                <stock>50</stock>
            </product>
            <product id="P102">
                <name>Mouse</name>
                <price currency="EUR">25.50</price>
                <stock>200</stock>
            </product>
            <product id="P103" discontinued="true">
                <name>Keyboard</name>
                <price currency="USD">75.00</price>
                <stock>0</stock>
            </product>
            """

        elements = XMLParser.parse_elements(xml_data)

        self.assertEqual(len(elements), 3)
