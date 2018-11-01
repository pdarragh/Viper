# Viper [![Build Status](https://travis-ci.org/pdarragh/Viper.svg?branch=master)](https://travis-ci.org/pdarragh/Viper) [![Coverage Status](https://coveralls.io/repos/github/pdarragh/Viper/badge.svg?branch=master&service=github)](https://coveralls.io/github/pdarragh/Viper?branch=master)

Viper is a statically-typed imperative programming language similar to (and inspired by) Python. It is designed to feel
familiar to users of Python, but with added features (and some differences). 

Eventually, Viper will be compiled. At the moment, it is implemented as an interpreter.

All documentation about the language will be present in this repository and in the associated [wiki](/wiki) and
[projects](/projects). However, I intend to chronicle much of the thought behind the development on my personal site.
You can find Viper-specific blog posts [here](https://pdarragh.github.io/blog/categories/viper). (Note that I'm actually
pretty terrible about updating the blog, so... don't count on seeing much there.)

## Features

I keep track of all language features I consider in [a project on GitHub](https://github.com/pdarragh/Viper/projects/1).
None of the decisions are necessarily final, and the absence of a feature from the list doesn't mean it won't end up in
Viper.

However, some features I believe to be integral to the Viper design. Those are:

* A static type system. Python's dynamic type system leaves much to be desired when it comes to larger projects.
  - Note that at the current time, Viper is *untyped*, but the type system is the next major goal.
* An imperative style. Although I love functional programming, Viper is meant to be a spiritual successor to Python.
* External and internal parameter names, a la Swift. I believe good names are of tantamount importance in good design.
* First-class functions. Any modern general-purpose language should support functions-as-values.
* Indentation-sensitive parsing. Again, Viper is meant to feel very much like Python, so this is necessary.

Some other features that I feel strongly but which are not inherent in Viper's identity:

* Algebraic data types (ADTs). Being able to define the shape of some data without having to write a whole class is
  wonderful.
* Pattern matching, and more specifically: *exhaustive* pattern matching over ADTs.
* Custom operator definition. This enables greater freedom of expression.
* Names with symbols, a la Scheme. Being able to name functions things like `valid?` is also incredibly expressive.

Additional features are sure to find their way into the language, but these are the primary considerations in guiding
the design for me.

## Running the REPL

As of this writing, Viper features a REPL. Its use requires Python 3.7.0+. First, clone this repository and open a shell
into its root directory. Then:

```
$ ./viper.py
>>> 
```

That's it! You're now in the REPL, just like Python's.

The REPL supports various commands and options,
[which are detailed in the wiki](https://github.com/pdarragh/Viper/wiki/REPL).
