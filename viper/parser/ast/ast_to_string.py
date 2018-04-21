from .nodes import AST

from typing import List


FINAL_FIRST = '└─'
FINAL_REST = '  '
INTMD_FIRST = '├─'
INTMD_REST = '│ '


def ast_to_string(ast: AST, condensed=True) -> str:
    lines = node_to_lines(ast, condensed)
    return '\n'.join(lines)


def node_to_lines(node: AST, condensed: bool) -> List[str]:
    lines = [node.__class__.__name__]
    params = vars(node)
    i = 0
    for param, val in params.items():
        i += 1
        if i == len(params):
            first = FINAL_FIRST
            rest = FINAL_REST
        else:
            first = INTMD_FIRST
            rest = INTMD_REST
        if not condensed:
            first = first + param + ': '
        val_lines = handle_sub_node(val, first, rest, condensed)
        lines += val_lines
    return lines


def handle_sub_node(val, first: str, rest: str, condensed: bool) -> List[str]:
    if isinstance(val, AST):
        val_lines = node_to_lines(val, condensed)
        val_lines[0] = first + val_lines[0]
        for i in range(1, len(val_lines)):
            val_lines[i] = rest + val_lines[i]
        return val_lines
    elif isinstance(val, list):
        val_lines = [first + '[]']
        i = 0
        for sub_val in val:
            i += 1
            if i == len(val):
                sub_first = rest + FINAL_FIRST
                sub_rest = rest + FINAL_REST
            else:
                sub_first = rest + INTMD_FIRST
                sub_rest = rest + INTMD_REST
            val_lines += handle_sub_node(sub_val, sub_first, sub_rest, condensed)
        return val_lines
    else:
        return [first + repr(val)]
