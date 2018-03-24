class ProductionPart:
    pass


class LiteralPart(ProductionPart):
    def __init__(self, text: str):
        self.text = text


class SpecialPart(ProductionPart):
    def __init__(self, text: str):
        self.text = text


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
