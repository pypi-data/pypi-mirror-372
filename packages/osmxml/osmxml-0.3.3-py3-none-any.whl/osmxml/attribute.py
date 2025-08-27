from .xml import XML   

class XMLAttribute(XML):
    def __init__(self, name: str, value: str):
        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    def to_string(self, raw=True) -> str:
        return '{name}="{value}"'.format(name=self.name, value=self.value)


    def __str__(self):
        return self.to_string()

    def __repr__(self):
        repr = 'XMLAttribute(name="{name}",'
        repr = "".join([repr, ' value="{value}")'])
        repr = repr.format(
                name=self.name,
                value=self.value,
        )
        return repr
