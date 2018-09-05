class Vehicle:
    wheels: Int
    doors: Int

    def init(wheels: Int, doors: Int) -> None:
        self.wheels = wheels
        self.doors = doors

    static private def get_wheels() -> Int:
        return self.wheels


class Car(Vehicle):
    def init(doors: Int) -> None:
        _ = super.init(4, doors)

    def is_sedan() -> Int:
        return self.doors == 4


class Blah:
    pass


class Other: pass


class Another: thing: Int
