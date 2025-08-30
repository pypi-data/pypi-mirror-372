# Coding Guidelines

## Naming

We use Pascal case for classes, e.g. `MyClass` and snake case for everything else e.g. `my_function`, `my_argument`, `my_property`, `my_variable`. When naming stuff, please consider meaningful names over short code.

## Indenting

All code and documentation uses 4 space indenting. Be sure to select the correct indenting in your editor and **dont't use TABs**.

## Typing

Typing is very important, especially for ACore functions. It can be a useful tool to minimize automatic casting and speed up code. Furthermore, it's great documentation for the user. Please use typing on function arguments, return types, externally accessed variables and properties. Complex types should be abbreviated and are stored in `typing.py`.

## Properties

Too many properties can clutter things, so not every externally accessed variable needs to go in a property. However, it is good practice to use them in the following cases:

- When a variable should only be read and not written to
- In abstract classes, when a property should be overwritten by the child
- If some function calls are necessary, when the value is changed
- When a variable needs additional documentation

## Docstrings

All classes, function, and properties should be documented by Google-style docstrings (see example below). Types must not be stated in the docstring, as they are automatically extracted from the given typing information.

!!! example
    ````py
    """Class/Function/Property description.

    Args:
        name: Argument description

    Notes:
        Some additional information.

    Returns:
        Description of the returned value(S).

    Raises:
        ExceptionName: Description of the raised Exception.

    Example: Example title
        Some description.
        ```python
        print("Wello Worlds")
        ```

    """
    ````

For classes, the class documentation is written in the `__init__()` function. For the different processors, there are some key properties that need to be stated at the end of the general description:

**Generator**

- `It is a multi output generator[, ... ].` and
    - `Output-update is [not] supported.` or
- `It is a single output generator, therefore output-update is not supported.` 

**Effect**

- `It is a multi input multi output effect[, ...].` and
    - `Input-update is [not] supported and output-update is [not] supported.` or
- `It is a multi input single output effect, therefore output-update is not supported.` and
    - `Input-update is [not] supported.` or
- `It is a single input multi output effect, therefore input-update is not supported.` and
    - `Output-update is [not] supported.`

**Analyzer**

- `It is a multi input analyzer[, ... ].` and
    - `Input-update is [not] supported.` or
- `It is a single input analyzer, therefore input-update is not supported.` 
