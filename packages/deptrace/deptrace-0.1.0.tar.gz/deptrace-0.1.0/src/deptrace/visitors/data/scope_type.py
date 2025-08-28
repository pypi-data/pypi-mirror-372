from typing import Literal


ScopeType = Literal[
    "module",
    "class",
    "function",
    "async_function",
    "lambda",
    "listcomp",
    "setcomp",
    "dictcomp",
    "genexpr",
    "match",
]
