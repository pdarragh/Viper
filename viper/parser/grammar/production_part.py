class ProductionPart:
    pass


class LiteralPart(ProductionPart):
    def __init__(self, text: str):
        self.text = text
