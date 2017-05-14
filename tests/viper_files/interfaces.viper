interface Shape:
    def get_area() -> Float

Shape Circle:
    def init(radius: Int):
        self.radius: Int = radius

    def get_area() -> Float:
        return pi * (self.radius ^ 2)

Shape Quadrilateral:
    def init(length: Int, width: Int):
        self.length: Int = length
        self.width: Int = width

    def get_area() -> Float:
        return self.length * self.width

Quadrilateral Rectangle:
    pass

Quadrilateral Square:
    def init(side: Int):
        self.length: Int = side
        self.width: Int = side
