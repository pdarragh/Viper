from .environment import *
from .store import *
from .value import *

import viper.parser.ast.nodes as ns

from viper.parser.ast.nodes import AST

from typing import NamedTuple, Tuple, Union


STMTS = [
    ns.Stmt, ns.PlainStmt, ns.IfStmt, ns.ElifStmt, ns.ElseStmt, ns.Definition, ns.Parameter, ns.Arguments, ns.StmtBlock,
]

EXPRS = [
    ns.Expr, ns.IfExpr, ns.ElifExpr, ns.ElseExpr, ns.TestExprList, ns.TestExpr, ns.OrTestExpr, ns.AndTestExpr,
    ns.NotTestExpr, ns.OpExpr, ns.SubOpExpr, ns.AtomExpr, ns.Atom, ns.Trailer, ns.ExprBlock,
    ns.LhsExpr,
]


class EvalResult:
    pass


class EvalStmtResult(NamedTuple, EvalResult):
    env: Environment
    store: Store


class EvalExprResult(NamedTuple, EvalResult):
    val: Value
    store: Store


class EvalLhsResult(NamedTuple, EvalResult):
    maybe_env: Union[Environment, None]
    store: Store


def start_eval(code: AST, env: Environment = None, store: Store = None) -> EvalResult:
    if env is None:
        env = empty_env()
    if store is None:
        store = empty_store()
    if any(map(lambda s: isinstance(code, s), STMTS)):
        return eval_stmt(code, env, store)
    elif any(map(lambda e: isinstance(code, e), EXPRS)):
        return eval_expr(code, env, store)
    else:
        raise NotImplementedError(f"No evaluation rules for ASTs of type: {type(code).__name__}")


def eval_stmt(stmt: AST, env: Environment, store: Store) -> EvalStmtResult:
    if isinstance(stmt, ns.SimpleStmt):
        return eval_stmt(stmt.stmt, env, store)
    elif isinstance(stmt, ns.AssignStmt):
        # Evaluate right-hand side first.
        val, store = eval_expr(stmt.expr, env, store)
        # Pass the value to the left-hand side evaluation.
        maybe_env, store = eval_lhs_expr(stmt.lhs, env, store, val)
        if maybe_env is not None:
            env = maybe_env
        return EvalStmtResult(env, store)
    elif isinstance(stmt, ns.EmptyStmt):
        return EvalStmtResult(env, store)
    elif isinstance(stmt, ns.IfStmt):
        val, store2 = eval_expr(stmt.cond, env, store)
        if isinstance(val, TrueVal):
            return eval_stmt(stmt.then_body, env, store2)
        elif isinstance(val, FalseVal):
            for elif_stmt in stmt.elif_stmts:
                val, store2 = eval_expr(elif_stmt.cond, env, store)
                if isinstance(val, TrueVal):
                    return eval_stmt(elif_stmt.elif_body, env, store2)
            if stmt.else_stmt is not None:
                return eval_stmt(stmt.else_stmt.else_body, env, store)
            else:
                return EvalStmtResult(env, store)
        else:
            raise RuntimeError(f"Not a boolean value: {val}")  # TODO: Use a custom error.
    elif isinstance(stmt, ns.SimpleStmtBlock):
        return eval_stmt(stmt.stmt, env, store)
    elif isinstance(stmt, ns.CompoundStmtBlock):
        for sub_stmt in stmt.stmts:
            env, store = eval_stmt(sub_stmt, env, store)
        return EvalStmtResult(env, store)
    else:
        raise NotImplementedError(f"No implementation for statement type: {type(stmt).__name__}")


def eval_expr(expr: AST, env: Environment, store: Store) -> EvalExprResult:
    if isinstance(expr, ns.IfExpr):
        raise NotImplementedError
    elif isinstance(expr, ns.TestExprList):
        values = []
        for test in expr.tests:
            val, store = eval_expr(test, env, store)
            values.append(val)
        if len(values) == 1:
            return EvalExprResult(values[0], store)
        else:
            return EvalExprResult(TupleVal(*values), store)
    elif isinstance(expr, ns.TestExpr):
        return eval_expr(expr.test, env, store)
    elif isinstance(expr, ns.OrTestExpr):
        values = []
        for test in expr.tests:
            val, store = eval_expr(test, env, store)
            values.append(val)
        if len(values) == 1:
            return EvalExprResult(values[0], store)
        else:
            for val in values:
                if not isinstance(val, BoolVal):
                    raise RuntimeError(f"Not a boolean value: {val}")  # TODO: Use a custom error.
                if isinstance(val, TrueVal):
                    return EvalExprResult(TrueVal(), store)
            return EvalExprResult(FalseVal(), store)
    elif isinstance(expr, ns.AndTestExpr):
        values = []
        for test in expr.tests:
            val, store = eval_expr(test, env, store)
            values.append(val)
        if len(values) == 1:
            return EvalExprResult(values[0], store)
        else:
            for val in values:
                if not isinstance(val, BoolVal):
                    raise RuntimeError(f"Not a boolean value: {val}")  # TODO: Use a custom error.
                if isinstance(val, FalseVal):
                    return EvalExprResult(FalseVal(), store)
            return EvalExprResult(TrueVal(), store)
    elif isinstance(expr, ns.NegatedTestExpr):
        val, store = eval_expr(expr.op_expr, env, store)
        if not isinstance(val, BoolVal):
            raise RuntimeError(f"Not a boolean value: {val}")  # TODO: Use a custom error.
        if isinstance(val, TrueVal):
            return EvalExprResult(FalseVal(), store)
        else:
            return EvalExprResult(TrueVal(), store)
    elif isinstance(expr, ns.NotNegatedTestExpr):
        return eval_expr(expr.op_expr, env, store)
    elif isinstance(expr, ns.OpExpr):
        if expr.left_op is not None:
            raise NotImplementedError
        if expr.right_op is not None:
            raise NotImplementedError
        if expr.sub_op_exprs:
            raise NotImplementedError
        return eval_expr(expr.atom, env, store)
    elif isinstance(expr, ns.AtomExpr):
        if expr.trailers:
            raise NotImplementedError
        return eval_expr(expr.atom, env, store)
    elif isinstance(expr, ns.ParenAtom):
        if expr.tests is None:
            return EvalExprResult(UnitVal(), store)
        else:
            return eval_expr(expr.tests, env, store)
    elif isinstance(expr, ns.NameAtom):
        name = expr.name.text
        if name in env:
            return EvalExprResult(store[env[name]], store)
        else:
            raise RuntimeError(f"No such name in environment: {name}")
    elif isinstance(expr, ns.NumberAtom):
        return EvalExprResult(NumVal(expr.num.text), store)
    elif isinstance(expr, ns.EllipsisAtom):
        return EvalExprResult(EllipsisVal(), store)
    elif isinstance(expr, ns.TrueAtom):
        return EvalExprResult(TrueVal(), store)
    elif isinstance(expr, ns.FalseAtom):
        return EvalExprResult(FalseVal(), store)
    else:
        raise NotImplementedError


def eval_lhs_expr(expr: AST, env: Environment, store: Store, val: Value) -> EvalLhsResult:
    """
    Attempts to perform a binding of a value. If the shape of the value and the shape of the left-hand side
    are compatible, the binding is performed. An environment and store are returned. If the shapes are not
    compatible, only the store is returned and the environment will be a None.

    :param expr: a left-hand side expression
    :param env: an environment
    :param store: a store
    :param val: a value to bind
    :return: a tuple of a Maybe(env) (as an Environment or a None) and a store
    """
    if isinstance(expr, ns.Pattern):
        return eval_pattern(expr, env, store, val)
    else:
        raise NotImplementedError


def eval_pattern(ptrn: ns.Pattern, env: Environment, store: Store, val: Value) -> EvalLhsResult:
    """
    Binds a value to a pattern, if the value's type and the pattern's shape align.

    :param ptrn: a pattern to match against
    :param env: an environment
    :param store: a store
    :param val: a value to bind
    :return: a tuple of a Maybe(env) (as an Environment or a None) and a store
    """
    if isinstance(ptrn, ns.TypedVariablePattern):
        ...
    elif isinstance(ptrn, ns.TypedAnonymousPattern):
        ...
    elif isinstance(ptrn, ns.TypedFieldPattern):
        ...
    elif isinstance(ptrn, ns.SimpleVariablePattern):
        name = ptrn.id.id.text
        env, store = bind_val(name, val, env, store)
        return EvalLhsResult(env, store)
    elif isinstance(ptrn, ns.SimpleAnonymousPattern):
        return EvalLhsResult(env, store)
    elif isinstance(ptrn, ns.SimpleFieldPattern):
        ...
    elif isinstance(ptrn, ns.SimpleParenPattern):
        ...
    elif isinstance(ptrn, ns.PatternList):
        ...
    else:
        raise NotImplementedError


def bind_val(name: str, val: Value, env: Environment, store: Store) -> Tuple[Environment, Store]:
    """
    Binds a value to a name. If the name exists in the environment, the previous binding is overwritten.
    Otherwise, a new binding is created.
    """
    if name in env:
        store = extend_store(store, val, env[name])
    else:
        env = extend_env(env, name, store.next_addr)
        store = extend_store(store, val)
    return env, store
