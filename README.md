# Viper

Viper is a statically-typed language similar to (and inspired by) Python. It provides many of the same features as
Python, and compiles to Python, but it isn't Python.

## Motive

I like Python a lot, but there are some areas where I find it to be lacking. In particular, I miss static types and
recursively-defined data structures. I decided to start this project to address these "needs" (if they can be so
called).

## Features

Viper has:

* Static typing, without inference
  - Inference may come later... undecided as yet
* Whitespace-delimiting, like Python
  - But unlike Python, Viper will only allow certain styles of indentation
* Parameter names and argument labels, like Swift
  - But argument labels are optional
* Recursively-defined data structures
