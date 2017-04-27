# Samples

Here I provide some samples of the language I intend to support.

## Sample 1

A recursive fibonacci number generator. This is almost just Python, but the types are capitalized.

```viper
def fibonacci(n: Int) -> Int:
    if n == 1 or n == 2:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)
```

## Sample 2

A recursively-defined data structure.

```viper
recdat Tree a:
    Leaf a
    Branch (Tree a) (Tree a)
```

## Sample 3

Interfaces can be used as types.

```viper
interface Shape:
    def get_area() -> Float
    
Shape Circle:
    def init(radius: Int):
        self.radius = radius
    
    def get_area() -> Float:
        return PI * (self.radius ^ 2)

Shape Quadrilateral:
    def init(length: Int, width: Int):
        self.length = length
        self.width = width
        
    def get_area() -> Float:
        return self.length * self.width

Quadrilateral Rectangle:
    pass

Quadrilateral Square:
    def init(side: Int):
        self.length = side
        self.width = side
```

## Sample 4

Parameter names and argument labels make reading code more natural.

```viper
def greet(person: String, from hometown: String) -> String:
    return "Hello {person} from {hometown}!"
    
greet("Jake", from: "State Farm")
```

Note that argument labels in a function (`from` in the above example) are *required*.

## Sample 5

Argument labels do not have to be given in function definitions, though:

```viper
def greet(person: String, hometown: String) -> String:
    return "Hello {person} from {hometown}!"
    
greet("Jake", "State Farm")
```
