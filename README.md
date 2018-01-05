# Viper [![Build Status](https://travis-ci.org/pdarragh/Viper.svg?branch=master)](https://travis-ci.org/pdarragh/Viper) [![Coverage Status](https://coveralls.io/repos/github/pdarragh/Viper/badge.svg?branch=master&service=github)](https://coveralls.io/github/pdarragh/Viper?branch=master)

Viper is a statically-typed language similar to (and inspired by) Python. It provides many of the same features as
Python, and compiles to Python, but it isn't Python.

All documentation about the language will be present in this repository and in the associated [wiki](/wiki) and
[projects](/projects). However, I intend to chronicle much of the thought behind the development on my personal site.
You can find Viper-specific blog posts [here](https://pdarragh.github.io/blog/categories/viper).

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
* Algebraic data types
  - Possibly GADTs, but we'll see about that
