from .production_part import ProductionPart

from typing import List


class Production:
    def __str__(self):
        return repr(self)


class RuleAliasProduction(Production):
    def __init__(self, rule_name: str):
        self.name = rule_name

    def __repr__(self):
        return "<" + self.name + ">"


class NamedProduction(Production):
    def __init__(self, production_name: str, production_parts: List[ProductionPart]):
        self.name = production_name
        self.parts = production_parts

    def __repr__(self):
        return self.name + " = " + ' '.join(map(repr, self.parts))
