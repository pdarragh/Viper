from .operators import env as op_env
from ..value import Value

from typing import Dict

env: Dict[str, Value] = {}
env.update(op_env)