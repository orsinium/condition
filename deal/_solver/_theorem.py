import enum
import typing
from textwrap import dedent

import astroid
import z3

from ._context import Context
from ._exceptions import UnsupportedError, ProveError
from ._eval_stmt import eval_stmt
from .._cached_property import cached_property


class Conclusion(enum.Enum):
    OK = 'proved!'
    SKIP = 'skipped'
    FAIL = 'failed'


z3.Z3_DEBUG = False


class Theorem:
    _func: astroid.FunctionDef
    conclusion: typing.Optional[Conclusion] = None
    error: typing.Optional[Exception] = None
    example: typing.Optional[z3.ModelRef] = None

    def __init__(self, node: astroid.FunctionDef) -> None:
        self._func = node

    @classmethod
    def from_text(cls, content: str) -> typing.Iterator['Theorem']:
        content = dedent(content)
        module = astroid.parse(content)
        yield from cls.from_astroid(module)

    @classmethod
    def from_astroid(cls, module: astroid.Module) -> typing.Iterator['Theorem']:
        for node in module.values():
            if isinstance(node, astroid.FunctionDef):
                yield cls(node=node)

    @property
    def name(self) -> str:
        return self._func.name or 'unknown_function'

    @cached_property
    def context(self) -> Context:
        return Context.make_empty()

    @cached_property
    def constraint(self) -> z3.BoolRef:
        post_goal = z3.Goal(ctx=self.context.z3_ctx)
        for constraint in eval_stmt(node=self._func, ctx=self.context):
            post_goal.add(constraint)
        return z3.Not(post_goal.as_expr())

    @cached_property
    def solver(self) -> z3.Solver:
        solver = z3.Solver(ctx=self.context.z3_ctx)
        solver.add(self.constraint)
        return solver

    def reset(self) -> None:
        func = self._func
        self.__dict__.clear()
        self._func = func

    def prove(self) -> None:
        if self.conclusion is not None:
            raise RuntimeError('already proved')
        try:
            result = self.solver.check()
        except UnsupportedError as exc:
            self.conclusion = Conclusion.SKIP
            self.error = exc
            return

        if result == z3.unsat:
            self.conclusion = Conclusion.OK
            return

        if result == z3.unknown:
            self.conclusion = Conclusion.SKIP
            self.error = ProveError('cannot validate theorem')
            return

        if result == z3.sat:
            self.conclusion = Conclusion.FAIL
            self.example = self.solver.model()
            return

        raise RuntimeError('unreachable')