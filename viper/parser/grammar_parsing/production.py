from .production_part import ProductionPart

from typing import List


class Production:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return repr(self)


class RuleAliasProduction(Production):
    def __init__(self, rule_name: str):
        super().__init__(rule_name)

    def __repr__(self):
        return "<" + self.name + ">"


class NamedProduction(Production):
    def __init__(self, production_name: str, production_parts: List[ProductionPart]):
        super().__init__(production_name)
        self.parts = production_parts

    def __repr__(self):
        return self.name + " = " + ' '.join(map(repr, self.parts))
