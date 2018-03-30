from typing import Any, Dict


class ASTNode:
    def __init__(self, production_name: str, params: Dict[str, Any]):
        self._name = production_name
        self._params = params

    def __repr__(self):
        return "AST_" + self._name + "(" + repr(self._params) + ")"

    def __getattr__(self, item):
        if item in self._params:
            return self._params[item]
        else:
            return super().__getattribute__(item)
