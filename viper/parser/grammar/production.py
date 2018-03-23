from .production_part import ProductionPart

from typing import List


class Production:
    pass


class RuleAliasProduction(Production):
    def __init__(self, rule_name: str):
        self.name = rule_name


class NamedProduction(Production):
    def __init__(self, production_name: str, production_parts: List[ProductionPart]):
        self.name = production_name
        self.parts = production_parts
