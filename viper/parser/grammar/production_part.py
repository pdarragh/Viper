class ProductionPart:
    def __str__(self):
        return repr(self)


class LiteralPart(ProductionPart):
    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return "'" + self.text + "'"


class SpecialPart(ProductionPart):
    def __init__(self, special_token: str):
        self.token = special_token

    def __repr__(self):
        return self.token


class RulePart(ProductionPart):
    def __init__(self, rule_name: str):
        self.name = rule_name

    def __repr__(self):
        return "<" + self.name + ">"


class RepeatPart(ProductionPart):
    def __init__(self, repeated_part: ProductionPart):
        self.part = repeated_part

    def __repr__(self):
        return repr(self.part) + "*"


class OptionPart(ProductionPart):
    def __init__(self, optional_part: ProductionPart):
        self.part = optional_part

    def __repr__(self):
        return repr(self.part) + "?"


class ParameterPart(ProductionPart):
    def __init__(self, name: str, matched_part: ProductionPart):
        self.name = name
        self.part = matched_part

    def __repr__(self):
        return self.name + ": " + repr(self.part)


class ExpandedParameterPart(ProductionPart):
    def __init__(self, rule_part: ProductionPart):
        self.rule = rule_part

    def __repr__(self):
        return "@" + repr(self.rule)


class SpecialExpandedParameterPart(ProductionPart):
    def __init__(self, name: str, single_param: str, list_param: str, rule_part: ProductionPart):
        self.name = name
        self.single = single_param
        self.list = list_param
        self.rule = rule_part

    def __repr__(self):
        return "&" + self.name + "{" + self.single + ", " + self.list + "}: " + repr(self.rule)
