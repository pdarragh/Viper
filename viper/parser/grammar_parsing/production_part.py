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
        return "'" + self.token + "'"


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


class SeparatedRepeatPart(ProductionPart):
    def __init__(self, separator: ProductionPart, rule_part: ProductionPart):
        self.separator = separator
        self.rule = rule_part

    def __repr__(self):
        return repr(self.rule) + "{" + repr(self.separator) + "}&"


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


class LiftedParameterPart(ProductionPart):
    def __init__(self, rule_part: ProductionPart):
        self.rule = rule_part

    def __repr__(self):
        return "@" + repr(self.rule)
