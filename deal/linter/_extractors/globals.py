# built-in
import ast
from typing import Iterator

# external
import astroid

# app
from .common import TOKENS, Token, traverse


def get_globals(body: list) -> Iterator[Token]:
    for expr in traverse(body):
        if isinstance(expr, TOKENS.GLOBAL):
            for name in expr.names:
                yield Token(value=name, line=expr.lineno, col=expr.col_offset + 7)
            continue

        if type(expr) is ast.Import:
            for alias in expr.names:
                yield Token(value=alias.name, line=expr.lineno, col=expr.col_offset + 7)
            continue

        if type(expr) is astroid.Import:
            for name, _ in expr.names:
                yield Token(value=name, line=expr.lineno, col=expr.col_offset + 7)
            continue

        if type(expr) is ast.ImportFrom:
            yield Token(value=expr.module, line=expr.lineno, col=expr.col_offset + 5)
            continue

        if type(expr) is astroid.ImportFrom:
            yield Token(value=expr.modname, line=expr.lineno, col=expr.col_offset + 5)
            continue