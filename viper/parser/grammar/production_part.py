class ProductionPart:
    pass


class LiteralPart(ProductionPart):
    def __init__(self, text: str):
        self.text = text


class SpecialPart(ProductionPart):
    def __init__(self, special_token: str):
        self.token = special_token


class RulePart(ProductionPart):
    def __init__(self, rule_name: str):
        self.name = rule_name


class RepeatPart(ProductionPart):
    def __init__(self, repeated_part: ProductionPart):
        self.part = repeated_part


class OptionPart(ProductionPart):
    def __init__(self, optional_part: ProductionPart):
        self.part = optional_part


class ParameterPart(ProductionPart):
    def __init__(self, name: str, matched_part: ProductionPart):
        self.name = name
        self.part = matched_part


class ExpandedParameterPart(ProductionPart):
    def __init__(self, rule_part: ProductionPart):
        self.rule = rule_part


class SpecialExpandedParameterPart(ProductionPart):
    def __init__(self, name: str, single_param: str, list_param: str, rule_part: ProductionPart):
        self.name = name
        self.single = single_param
        self.list = list_param
        self.rule = rule_part
