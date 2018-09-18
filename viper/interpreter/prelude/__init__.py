from .builtins import env as builtin_env
from .operators import env as op_env
from ..value import Value

from typing import Dict

env: Dict[str, Value] = {}
env.update(builtin_env)
env.update(op_env)
