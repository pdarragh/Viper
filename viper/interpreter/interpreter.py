from .environment import *
from .prelude import env as prelude_env
from .store import *
from .value import *

import viper.parser.ast.nodes as ns

from viper.parser.ast.nodes import AST

from typing import Iterable, List, NamedTuple, Optional, Tuple


STARTERS = [
    ns.SingleNewline, ns.SingleLine, ns.FileInput, ns.FileNewline, ns.FileStmt
]

STMTS = [
    ns.Stmt, ns.PlainStmt, ns.IfStmt, ns.ElifStmt, ns.ElseStmt, ns.Definition, ns.Parameter, ns.Arguments, ns.StmtBlock,
]

EXPRS = [
    ns.Expr, ns.IfExpr, ns.ElifExpr, ns.ElseExpr, ns.TestExprList, ns.TestExpr, ns.OrTestExpr, ns.AndTestExpr,
    ns.NotTestExpr, ns.OpExpr, ns.SubOpExpr, ns.AtomExpr, ns.Atom, ns.Trailer, ns.ExprBlock,
    ns.LhsExpr,
]


class EvalResult(NamedTuple):
    env: Environment
    store: Store
    val: Optional[Value]


class EvalStmtResult(NamedTuple):
    env: Environment
    store: Store
    val: Optional[Value]


class EvalExprResult(NamedTuple):
    val: Value
    store: Store


class EvalLhsResult(NamedTuple):
    env: Environment
    store: Store


def start_eval(code: AST, env: Environment = None, store: Store = None,
               previous_result: EvalResult = None) -> EvalResult:
    if previous_result is not None:
        env = previous_result.env
        store = previous_result.store
    if env is None and store is None:
        env, store = bootstrap_env_and_store(prelude_env)
    if env is None:
        env = empty_env()
    if store is None:
        store = empty_store()
    if any(map(lambda s: isinstance(code, s), STARTERS)):
        return eval_starter(code, env, store)
    elif any(map(lambda s: isinstance(code, s), STMTS)):
        stmt_res = eval_stmt(code, env, store)
        return EvalResult(stmt_res.env, stmt_res.store, stmt_res.val)
    elif any(map(lambda e: isinstance(code, e), EXPRS)):
        expr_res = eval_expr(code, env, store)
        return EvalResult(env, expr_res.store, expr_res.val)
    else:
        raise NotImplementedError(f"No evaluation rules for ASTs of type: {type(code).__name__}")


def bootstrap_env_and_store(initial_env: Dict[str, Value]) -> Tuple[Environment, Store]:
    """
    Produces an initial environment and store to be used during evaluation. The `initial_env` which is passed in is a
    simple mapping from names to values, so here we allocate space in the store for each name and assign the values
    appropriately.

    :param initial_env: the "environment" to start from (usually defined in the `prelude` module)
    :return: a pair consisting of the new environment and store
    """
    env = empty_env()
    store = empty_store()
    for name, val in initial_env.items():
        env, store = bind_val(name, val, env, store)
    return env, store


def eval_starter(starter: AST, env: Environment, store: Store) -> EvalResult:
    """
    Evaluates a starting statement. These are usually just wrappers that can be used to indicate where the code came
    from.

    :param starter: the statement to evaluate
    :param env: the current environment
    :param store: the current store
    :return: an EvalResult representing the updated environment and store (and a value if necessary)
    """
    if isinstance(starter, ns.SingleNewline):
        # A blank line does not produce a value.
        return EvalResult(env, store, None)
    elif isinstance(starter, ns.SingleLine):
        return start_eval(starter.line, env, store)
    elif isinstance(starter, ns.FileInput):
        # Add __name__ to the environment.
        # TODO: Ensure this is correct for imported modules as well.
        env, store = bind_val('__name__', StringVal("__main__"), env, store)
        # Pre-allocate names in the environment so forward references work correctly.
        env, store = _pre_allocate_names(starter.lines, env, store)
        val = None
        for line in starter.lines:
            eval_res = eval_starter(line, env, store)
            val = eval_res.val
            env = eval_res.env
            store = eval_res.store
        return EvalResult(env, store, val)
    elif isinstance(starter, ns.FileNewline):
        # A blank line does not produce a value.
        return EvalResult(env, store, None)
    elif isinstance(starter, ns.FileStmt):
        return start_eval(starter.stmt, env, store)
    else:
        raise NotImplementedError(f"No evaluation rules for starters of type: {type(starter).__name__}")


def eval_stmt(stmt: AST, env: Environment, store: Store) -> EvalStmtResult:
    """
    Evaluates a statement.

    Statements are used for side-effects. They can manipulate the environment and store, but generally do not produce
    values (except for Return statements).

    :param stmt: the statement to evaluate
    :param env: the current environment
    :param store: the current store
    :return: an EvalStmtResult representing the updated environment and store (and a value if necessary)
    """
    if isinstance(stmt, ns.SimpleStmt):
        return eval_stmt(stmt.stmt, env, store)
    elif isinstance(stmt, ns.ReturnStmt):
        if stmt.tests is None:
            return EvalStmtResult(env, store, UnitVal())
        else:
            val, store = eval_expr(stmt.tests, env, store)
            return EvalStmtResult(env, store, val)
    elif isinstance(stmt, ns.AssignStmt):
        # Evaluate right-hand side first.
        val, store = eval_expr(stmt.expr, env, store)
        # Pass the value to the left-hand side evaluation.
        env, store = eval_lhs_expr(stmt.lhs, env, store, val)
        return EvalStmtResult(env, store, None)
    elif isinstance(stmt, ns.CallStmt):
        val, store = eval_expr(stmt.atom, env, store)
        args, store = accumulate_values_from_exprs(stmt.call.args, env, store)
        # Evaluate the call and dispose of the return value.
        _, store = eval_function_call(val, args, store)
        return EvalStmtResult(env, store, None)
    elif isinstance(stmt, ns.EmptyStmt):
        return EvalStmtResult(env, store, None)
    elif isinstance(stmt, ns.IfStmt):
        # Evaluate the condition and store the result in a new store. A new store must be used in case the condition is
        # false, in which case the original store should be used for evaluation of any alternative (elif) conditions.
        val, store2 = eval_expr(stmt.cond, env, store)
        if isinstance(val, TrueVal):
            return eval_stmt(stmt.then_body, env, store2)
        elif isinstance(val, FalseVal):
            for elif_stmt in stmt.elif_stmts:
                val, store3 = eval_expr(elif_stmt.cond, env, store)
                if isinstance(val, TrueVal):
                    return eval_stmt(elif_stmt.elif_body, env, store3)
            if stmt.else_stmt is not None:
                return eval_stmt(stmt.else_stmt.else_body, env, store)
            else:
                return EvalStmtResult(env, store, None)
        else:
            raise RuntimeError(f"Not a boolean value: {val}")  # TODO: Use a custom error.
    elif isinstance(stmt, ns.FuncDef):
        closure = CloVal(stmt.params, stmt.body, env)
        env, store = bind_val(stmt.name.text, closure, env, store)
        return EvalStmtResult(env, store, None)
    elif isinstance(stmt, ns.ClassDef):
        # To define a class, the static members must first be found and evaluated and then the instance members must be
        # saved for later use during each instantiation.
        parents = []
        static_fields = {}
        static_methods = {}
        instance_fields = []
        instance_methods = []

        def handle_field(field: ns.Field):
            modifier = field.modifier
            if isinstance(modifier, ns.StaticModifier):
                nonlocal store
                addr = store.next_addr
                store = extend_store(store, BottomVal())
                static_fields[field.name.text] = InstantiatedField(addr)
            elif isinstance(modifier, ns.NonstaticModifier):
                instance_fields.append(UninstantiatedField(field.name.text))
            else:
                raise NotImplementedError(f"No implementation for field modifier of type: {type(modifier).__name__}")

        def handle_method(method: ns.Method):
            modifier = method.modifier
            if isinstance(modifier, ns.StaticModifier):
                nonlocal store
                addr = store.next_addr
                store = extend_store(store, CloVal(method.func.params, method.func.body, env))
                static_methods[method.func.name.text] = InstantiatedMethod(addr)
            elif isinstance(modifier, ns.NonstaticModifier):
                instance_methods.append(UninstantiatedMethod(method.func))
            else:
                raise NotImplementedError(f"No implementation for method modifier of type: {type(modifier).__name__}")

        # If there are parents (superclasses), find them.
        if stmt.args is not None:
            parents = stmt.args.parents

        # Find all fields and methods and categorize them for later use based on whether they are static.
        if isinstance(stmt.body, ns.SimpleEmptyClassStmt):
            pass
        elif isinstance(stmt.body, ns.CompoundEmptyClassStmt):
            pass
        elif isinstance(stmt.body, ns.CompoundClassStmtBlock):
            for sub_stmt in stmt.body.stmts:
                if isinstance(sub_stmt, ns.Field):
                    handle_field(sub_stmt)
                elif isinstance(sub_stmt, ns.Method):
                    handle_method(sub_stmt)
                else:
                    raise NotImplementedError(f"No implementation for class body sub-statement of type: "
                                              f"{type(sub_stmt).__name__}")
        elif isinstance(stmt.body, ns.Field):
            handle_field(stmt.body)
        elif isinstance(stmt.body, ns.Method):
            handle_method(stmt.body)
        else:
            raise NotImplementedError(f"No implementation for class body of type: {type(stmt.body).__name__}")

        class_decl = ClassDeclVal(parents, static_fields, static_methods, instance_fields, instance_methods, env)
        env, store = bind_val(stmt.name.text, class_decl, env, store)
        return EvalStmtResult(env, store, None)
    elif isinstance(stmt, ns.InterfaceDef):
        # TODO: Implement this.
        raise NotImplementedError
    elif isinstance(stmt, ns.DataDef):
        # TODO: Implement this.
        raise NotImplementedError
    elif isinstance(stmt, ns.Arguments):
        # TODO: Implement this.
        raise NotImplementedError
    elif isinstance(stmt, ns.SimpleStmtBlock):
        return eval_stmt(stmt.stmt, env, store)
    elif isinstance(stmt, ns.CompoundStmtBlock):
        # Pre-allocate names in the environment so forward references work correctly.
        env, store = _pre_allocate_names(stmt.stmts, env, store)
        # Then evaluate the statements.
        for sub_stmt in stmt.stmts:
            stmt_res = eval_stmt(sub_stmt, env, store)
            if stmt_res.val is not None:
                # A value is only present if this is a `return` statement, so return immediately.
                return stmt_res
            # Since we did not return, record the (potentially) modified environment and store and continue.
            env = stmt_res.env
            store = stmt_res.store
        return EvalStmtResult(env, store, None)
    else:
        raise NotImplementedError(f"No implementation for statement of type: {type(stmt).__name__}")


def eval_lhs_expr(expr: AST, env: Environment, store: Store, val: Value) -> EvalLhsResult:
    """
    Evaluates a left-hand side (LHS).
    
    An LHS is a pattern which is used for binding values to variables. If the shape of the value and the shape of the
    LHS pattern are compatible (i.e. same arguments and types), the binding is performed. An error is raised otherwise.

    :param expr: the left-hand side expression to evaluate
    :param env: the current environment
    :param store: the current store
    :param val: the value to bind
    :return: an EvalLhsResult representing the updated environment and store
    """
    if isinstance(expr, ns.Pattern):
        if isinstance(expr, ns.TypedVariablePattern):
            # >>> x: Type = {val}
            name = expr.id.id.text
            env, store = bind_val(name, val, env, store)
            return EvalLhsResult(env, store)
        elif isinstance(expr, ns.TypedAnonymousPattern):
            # >>> _: Type = {val}
            return EvalLhsResult(env, store)
        elif isinstance(expr, ns.TypedFieldPattern):
            # >>> foo.bar: Type = {val}
            class_val, store = eval_expr(expr.root, env, store)
            addr = _eval_field_lookup(class_val, expr.field.id.text)
            store = extend_store(store, val, addr)
            return EvalLhsResult(env, store)
        elif isinstance(expr, ns.SimpleVariablePattern):
            # >>> x = {val}
            name = expr.id.id.text
            env, store = bind_val(name, val, env, store)
            return EvalLhsResult(env, store)
        elif isinstance(expr, ns.SimpleAnonymousPattern):
            # >>> _ = {val}
            return EvalLhsResult(env, store)
        elif isinstance(expr, ns.SimpleFieldPattern):
            # >>> foo.bar = {val}
            class_val, store = eval_expr(expr.root, env, store)
            addr = _eval_field_lookup(class_val, expr.field.id.text)
            store = extend_store(store, val, addr)
            return EvalLhsResult(env, store)
        elif isinstance(expr, ns.SimpleParenPattern):
            if len(expr.patterns) == 1:
                # >>> (a) = 2
                # >>> (a) = 3, 4
                return eval_lhs_expr(expr.patterns[0], env, store, val)
            if not isinstance(val, TupleVal):
                # >>> (a, b) = 3
                raise RuntimeError(f"Not enough values to unpack into pattern.")
            if len(expr.patterns) != len(val.vals):
                # >>> (a, b, c) = 2, 3
                raise RuntimeError(f"Incompatible number of values to unpack into pattern.")
            # >>> (a, b, c) = (2, 3, 4)
            for sub_pattern, sub_val in zip(expr.patterns, val.vals):
                env, store = eval_lhs_expr(sub_pattern, env, store, sub_val)
            return EvalLhsResult(env, store)
        else:
            raise NotImplementedError(f"No implementation for pattern of type: {type(expr).__name__}")
    else:
        raise NotImplementedError(f"No implementation for left-hand-side expression of type: {type(expr).__name__}")


def eval_expr(expr: AST, env: Environment, store: Store) -> EvalExprResult:
    """
    Evaluates an expression.

    Expressions are used to compute new values. There is no expression which can modify the environment, but expressions
    can have an affect on the store and always produce a value.

    :param expr: the expression to evaluate
    :param env: the current environment
    :param store: the current store
    :return: an EvalExprResult representing the updated store and the computed value
    """
    if isinstance(expr, ns.IfExpr):
        # Evaluate the condition and store the result in a new store. A new store must be used in case the condition is
        # false, in which case the original store should be used for evaluation of any alternative (elif) conditions.
        val, store2 = eval_expr(expr.cond, env, store)
        if isinstance(val, TrueVal):
            return eval_expr(expr.then_body, env, store2)
        elif isinstance(val, FalseVal):
            for elif_expr in expr.elif_exprs:
                val, store3 = eval_expr(elif_expr.cond, env, store)
                if isinstance(val, TrueVal):
                    return eval_expr(elif_expr.elif_body, env, store3)
            if expr.else_expr is not None:
                return eval_expr(expr.else_expr.else_body, env, store)
            else:
                return EvalExprResult(UnitVal(), store)
    elif isinstance(expr, ns.TestExprList):
        vals, store = accumulate_values_from_exprs(expr.tests, env, store)
        return wrap_values(vals, store)
    elif isinstance(expr, ns.TestExpr):
        return eval_expr(expr.test, env, store)
    elif isinstance(expr, ns.OrTestExpr):
        if len(expr.tests) == 1:
            # There is only one test, so evaluate it and don't care if it's a boolean.
            return eval_expr(expr.tests[0], env, store)
        else:
            # There are multiple tests, so they should all be boolean values.
            vals, store = accumulate_values_from_exprs(expr.tests, env, store)
            if not len(vals) == len(expr.tests):
                raise RuntimeError(f"Expected {len(expr.tests)} or-test values, but received {len(vals)}")
            for val in vals:
                if not isinstance(val, BoolVal):
                    raise RuntimeError(f"Expected boolean value in or-test but received: {val}")  # TODO: Use a custom error.
                if isinstance(val, TrueVal):
                    return EvalExprResult(TrueVal(), store)
            return EvalExprResult(FalseVal(), store)
    elif isinstance(expr, ns.AndTestExpr):
        if len(expr.tests) == 1:
            # There is only one test, so evaluate it and don't care if it's a boolean.
            return eval_expr(expr.tests[0], env, store)
        else:
            # There are multiple tests, so they should all be boolean values.
            vals, store = accumulate_values_from_exprs(expr.tests, env, store)
            if not len(vals) == len(expr.tests):
                raise RuntimeError(f"Expected {len(expr.tests)} and-test values, but received {len(vals)}")
            for val in vals:
                if not isinstance(val, BoolVal):
                    raise RuntimeError(f"Expected boolean value in and-test but received: {val}")  # TODO: Use a custom error.
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
        val, store = eval_expr(expr.atom, env, store)
        if expr.left_op is not None:
            val, store = eval_prefix_operator(expr.left_op.text, val, env, store)
        for sub_op_expr in expr.sub_op_exprs:
            r_val, store = eval_expr(sub_op_expr.atom, env, store)
            val, store = eval_infix_operator(sub_op_expr.op.text, val, r_val, env, store)
        if expr.right_op is not None:
            val, store = eval_postfix_operator(expr.right_op.text, val, env, store)
        return EvalExprResult(val, store)
    elif isinstance(expr, ns.AtomExpr):
        val, store = eval_expr(expr.atom, env, store)
        for trailer in expr.trailers:
            if isinstance(trailer, ns.Call):
                args, store = accumulate_values_from_exprs(trailer.args, env, store)
                val, store = eval_function_call(val, args, store)
            elif isinstance(trailer, ns.FieldAccess):
                addr = _eval_field_lookup(val, trailer.field.text)
                val = store[addr]
            else:
                raise NotImplementedError(f"No implementation for trailer of type: {type(trailer).__name__}")
        return EvalExprResult(val, store)
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
            raise RuntimeError(f"No such name in environment: {name}")  # TODO: Use a custom error.
    elif isinstance(expr, ns.ClassAtom):
        name = expr.name.text
        if name in env:
            return EvalExprResult(store[env[name]], store)
        else:
            raise RuntimeError(f"No such name in environment: {name}")  # TODO: Use a custom error.
    elif isinstance(expr, ns.IntAtom):
        return EvalExprResult(IntVal(expr.num.text), store)
    elif isinstance(expr, ns.FloatAtom):
        return EvalExprResult(FloatVal(expr.num.text), store)
    elif isinstance(expr, ns.StringAtom):
        return EvalExprResult(StringVal(expr.string.text), store)
    elif isinstance(expr, ns.EllipsisAtom):
        return EvalExprResult(EllipsisVal(), store)
    elif isinstance(expr, ns.TrueAtom):
        return EvalExprResult(TrueVal(), store)
    elif isinstance(expr, ns.FalseAtom):
        return EvalExprResult(FalseVal(), store)
    elif isinstance(expr, ns.SimpleExprBlock):
        return eval_expr(expr.expr, env, store)
    elif isinstance(expr, ns.IndentedExprBlock):
        return eval_expr(expr.expr, env, store)
    else:
        raise NotImplementedError(f"No implementation for expression of type: {type(expr).__name__}")


def eval_prefix_operator(op: str, operand: Value, env: Environment, store: Store) -> EvalExprResult:
    return _eval_operator(op, [operand], env, store)


def eval_infix_operator(op: str, left_operand: Value, right_operand: Value,
                        env: Environment, store: Store) -> EvalExprResult:
    return _eval_operator(op, [left_operand, right_operand], env, store)


def eval_postfix_operator(op: str, operand: Value, env: Environment, store: Store) -> EvalExprResult:
    return _eval_operator(op, [operand], env, store)


def _eval_operator(op: str, operands: List[Value], env: Environment, store: Store) -> EvalExprResult:
    if op in env:
        val = store[env[op]]
        return eval_function_call(val, operands, store)
    else:
        raise RuntimeError(f"No implementation for operator: {op}")  # TODO: Use a custom error.


def eval_function_call(val: Value, args: List[Value], store: Store) -> EvalExprResult:
    if isinstance(val, CloVal):
        return _eval_function_call(val, args, store)
    elif isinstance(val, ForeignCloVal):
        return _eval_foreign_function_call(val, args, store)
    elif isinstance(val, ClassDeclVal):
        return _eval_class_instantiation(val, args, store)
    else:
        raise RuntimeError(f"Cannot apply arguments to non-closure value of type: {type(val).__name__}")  # TODO: Use a custom error.


def _eval_function_call(clo: CloVal, args: List[Value], store: Store) -> EvalExprResult:
    if len(clo.params) != len(args):
        if len(args) > len(clo.params):
            raise RuntimeError(f"Too many arguments specified for call to function: {clo}")  # TODO: Use a custom error.
        else:
            # TODO: Automatic currying could be implemented here.
            raise RuntimeError(f"Not enough arguments specified for call to function: {clo}")  # TODO: Use a custom error.
    inner_env = clo.env
    for i in range(len(clo.params)):
        param = clo.params[i]
        arg = args[i]
        inner_env, store = bind_val(param.internal.text, arg, inner_env, store)
    stmt_res = eval_stmt(clo.code, inner_env, store)
    return EvalExprResult(stmt_res.val, stmt_res.store)


def _eval_foreign_function_call(clo: ForeignCloVal, args: List[Value], store: Store) -> EvalExprResult:
    if len(clo.params) != len(args):
        raise RuntimeError(f"Foreign function call expected {len(clo.params)} arguments but received {len(args)}")  # TODO: Use a custom error.
    inner_env = {}
    for i in range(len(clo.params)):
        param = clo.params[i]
        arg = args[i]
        inner_env[param] = val_to_python(arg)
    # TODO: This is incredibly unsafe and should be handled specially.
    eval_str = 'func(' + ', '.join([k + '=' + stringify_python_val(v) for k, v in inner_env.items()]) + ')'
    val = eval(eval_str, {}, {'func': clo.func})
    val = python_to_val(val)
    return EvalExprResult(val, store)


def _eval_class_instantiation(cls: ClassDeclVal, args: List[Value], store: Store) -> EvalExprResult:
    if len(cls.instance_fields) != len(args):
        raise RuntimeError(f"Class instantiation expected {len(cls.instance_fields)} arguments but received {len(args)}")  # TODO: Use a custom error.
    # Initialize the fields.
    instance_fields = {}
    for i in range(len(cls.instance_fields)):
        # TODO: It is assumed that the args and fields are in the same order. Validate this assumption.
        field = cls.instance_fields[i]
        arg = args[i]
        addr = store.next_addr
        store = extend_store(store, arg)
        instance_fields[field.name] = InstantiatedField(addr)
    # Allocate each method.
    instance_methods = {}
    for method in cls.instance_methods:
        func = method.func
        addr = store.next_addr
        closure = CloVal(func.params, func.body, cls.env)
        store = extend_store(store, closure)
        instance_methods[func.name.text] = InstantiatedMethod(addr)
    # Create the instance.
    instance = ClassInstanceVal(cls, instance_fields, instance_methods)
    return EvalExprResult(instance, store)


def _eval_field_lookup(val: Value, field: str) -> Address:
    if isinstance(val, ClassDeclVal):
        if field in val.static_fields:
            field = val.static_fields[field]
            return field.addr
        elif field in val.static_methods:
            method = val.static_methods[field]
            return method.addr
        else:
            raise RuntimeError(f"No such field in class: {field}")
    elif isinstance(val, ClassInstanceVal):
        if field in val.instance_fields:
            field = val.instance_fields[field]
            return field.addr
        elif field in val.instance_methods:
            method = val.instance_methods[field]
            return method.addr
        else:
            return _eval_field_lookup(val.super, field)
    else:
        raise RuntimeError(f"Cannot perform field lookup in value of type: {type(val).__name__}")


def bind_val(name: str, val: Value, env: Environment, store: Store) -> Tuple[Environment, Store]:
    """
    Binds a value to a name. If the name exists in the environment, the previous binding is overwritten.
    Otherwise, a new binding is created.

    :param name: the name to bind to
    :param val: the value to be bound
    :param env: the current environment
    :param store: the current store
    :return: a pair constituting the updated environment and store
    """
    if name in env:
        store = extend_store(store, val, env[name])
    else:
        env = extend_env(env, name, store.next_addr)
        store = extend_store(store, val)
    return env, store


def accumulate_values_from_exprs(exprs: List[AST], env: Environment, store: Store) -> Tuple[List[Value], Store]:
    """
    Evaluates a list of expressions. The values resulting from these evaluations are accumulated into a single list.

    :param exprs: the list of expressions to evaluate
    :param env: the current environment
    :param store: the current store
    :return: a pair consisting of the list of values and the updated store
    """
    values: List[Value] = []
    for expr in exprs:
        val, store = eval_expr(expr, env, store)
        values.append(val)
    return values, store


def wrap_values(values: List[Value], store: Store) -> EvalExprResult:
    """
    Wraps a list of values. If the list has only one element, then it is extracted and produces separately. If the list
    has multiple elements, they are wrapped into a TupleVal.

    :param values: the list of values to wrap
    :param store: the current store
    :return: an EvalExprResult representing the wrapped value and the updated store
    """
    if len(values) == 1:
        return EvalExprResult(values[0], store)
    else:
        return EvalExprResult(TupleVal(*values), store)


def _find_names(stmts: List[AST]) -> Iterable[str]:
    """
    Finds all names htat will be bound in a list of statements and yields them one at a time.

    :param stmts: the list of statements to search
    :return: a generator of strings representing the names that will be bound to
    """
    for stmt in stmts:
        name = _find_name(stmt)
        if name is None:
            continue
        else:
            yield name


def _find_name(stmt: AST) -> Optional[str]:
    """
    Determines whether a statement is of the kind that will bind a name, and returns that name. If the statement would
    not bind a name, a None is returned instead.

    :param stmt: the statement to try to axtract a name from
    :return: either an extracted name or None
    """
    if isinstance(stmt, ns.FuncDef):
        return stmt.name.text
    elif isinstance(stmt, ns.ClassDef):
        return stmt.name.text
    elif isinstance(stmt, ns.InterfaceDef):
        # TODO: Implement this.
        raise NotImplementedError
    elif isinstance(stmt, ns.DataDef):
        # TODO: Implement this.
        raise NotImplementedError
    elif isinstance(stmt, ns.FileStmt):
        return _find_name(stmt.stmt)
    else:
        return None


def _pre_allocate_names(stmts: List[AST], env: Environment, store: Store) -> Tuple[Environment, Store]:
    """
    Allocates names in the environment and space in the store for names which will be bound to by the list of statements
    passed in. This is useful for allowing forward declarations among functions, classes, etc. within a single scope.

    :param stmts: the list of statements to search
    :param env: the current environment
    :param store: the current store
    :return: a pair constituting the updated environment and store after pre-allocating space for the names
    """
    for name in _find_names(stmts):
        env, store = bind_val(name, BottomVal(), env, store)
    return env, store
