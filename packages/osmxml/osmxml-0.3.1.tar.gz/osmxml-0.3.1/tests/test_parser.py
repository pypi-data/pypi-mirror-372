import unittest

from osmxml import XMLParser
from osmxml import XMLElement
from osmxml import XMLTextElement

class TestParser(unittest.TestCase):
    def test_parse_structure(self):
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
        self.assertEqual(elements[0].name, "note")
        self.assertEqual(len(elements[0].attributes), 0)
        self.assertEqual(len(elements[0].children), 4)
        self.assertEqual(elements[0].is_closed, True)
        # Children
        names = ["to", "from", "heading", "body"]
        contents = ["Tove", "Jani", "Reminder", "Don't forget me this weekend!"]
        for index, child in enumerate(elements[0].children):
            self.assertEqual(child.name, names[index])
            self.assertEqual(str(child.children[0]), contents[index])
            self.assertEqual(child.is_closed, True)


        xml_data = """
            <book id="12345" type="fiction">
              <title>The Great Gatsby</title>
              <author>F. Scott Fitzgerald</author>
            </book>
            """

        elements = XMLParser.parse_elements(xml_data)
       
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].name, "book")
        self.assertEqual(len(elements[0].attributes), 2)
        self.assertEqual(len(elements[0].children), 2)
        self.assertEqual(elements[0].is_closed, True)
        # Children
        names = ["title", "author"]
        contents = ["The Great Gatsby", "F. Scott Fitzgerald"]
        for index, child in enumerate(elements[0].children):
            self.assertEqual(child.name, names[index])
            self.assertEqual(str(child.children[0]), contents[index])
            self.assertEqual(child.is_closed, True)


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
        self.assertEqual(elements[0].name, "message")
        self.assertEqual(len(elements[0].attributes), 0)
        self.assertEqual(len(elements[0].children), 7)
        self.assertEqual(elements[0].is_closed, True)
        # Children
        names = ["", "b", "", "i", "", "i", ""]
        contents = [ "Hello, I am a", "message", "with some", "bold", "and", "italic", "words."]
        for index, child in enumerate(elements[0].children):
            self.assertEqual(child.name, names[index])
            if (len(child.children) != 0):
                self.assertEqual(str(child.children[0]), contents[index])
            else:
                self.assertEqual(child.text, contents[index])
                
            self.assertEqual(child.is_closed, True)


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

        products = [
            { 
                "id": "P101",
                "name": "Laptop",
                "currency": "USD",
                "price": "1200.00",
                "stock": "50",
            },
            { 
                "id": "P102",
                "name": "Mouse",
                "currency": "EUR",
                "price": "25.50",
                "stock": "200",
            },
            { 
                "id": "P103",
                "name": "Keyboard",
                "currency": "USD",
                "price": "75.00",
                "stock": "0",
            },
        ] 

        self.assertEqual(len(elements), 3)
        for element_index, element in enumerate(elements):
            product = products[element_index]
            self.assertEqual(element.attributes[0].value, product["id"])

            self.assertEqual(element.children[0].name, "name")
            self.assertEqual(str(element.children[0].children[0]), product["name"])
            self.assertEqual(element.children[1].name, "price")
            self.assertEqual(str(element.children[1].children[0]), product["price"])
            self.assertEqual(str(element.children[1].attributes[0].value), product["currency"])
            self.assertEqual(element.children[2].name, "stock")
            self.assertEqual(str(element.children[2].children[0]), product["stock"])




        xml_data = """
            <xml version='1.0'><stream:stream></stream:stream> 
            """

        elements = XMLParser.parse_elements(xml_data)

        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].is_closed, False)
        self.assertEqual(elements[0].children[0].is_closed, True)


        xml_data = """
            <xml version='1.0'>
                <stream:stream>
                    <to host='host'>
                        <message/>
                    </to>
                        
            """

        elements = XMLParser.parse_elements(xml_data)

        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].is_closed, False)
        self.assertEqual(elements[0].children[0].is_closed, False)
        self.assertEqual(elements[0].children[0].children[0].is_closed, True)
        self.assertEqual(elements[0].children[0].children[0].children[0].is_closed, True)


        xml_data = """
            <?xml version='1.0'?>
            <stream:stream id='11467641' 
                version='1.0' 
                xml:lang='en' 
                xmlns:stream='http://etherx.jabber.org/streams' 
                from='5222.de' 
                xmlns='jabber:client'>      
            """

        elements = XMLParser.parse_elements(xml_data)

        self.assertEqual(elements[0].is_closed, False)
        self.assertEqual(elements[0].children[0].is_closed, False)
