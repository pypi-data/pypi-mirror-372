# ctypespec

**ctypespec** is a Python utility that parses C language type definitions and automatically generates equivalent `ctypes` structures. It is useful when integrating C libraries into Python projects through the `ctypes` module.

## Features

-   Parses C type definitions, including structs and typedefs.
-   Converts C declarations to Python `ctypes` classes.
-   Utilizes AST parsing and Clang tooling for accurate analysis.

## Installation

Install from source using pip:

```bash
pip install ctypespec
```
