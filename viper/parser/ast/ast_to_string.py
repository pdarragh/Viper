from .nodes import AST

from typing import List


def ast_to_string(ast: AST, condensed=True) -> str:
    if condensed:
        lines = node_to_lines_condensed(ast)
    else:
        lines = node_to_lines_full(ast)
    return '\n'.join(lines)


def node_to_lines_condensed(node: AST) -> List[str]:
    lines = [node.__class__.__name__]
    params = vars(node)
    i = 0
    for param, val in params.items():
        i += 1
        if i == len(params):
            first = '└─'
            rest = '  '
        else:
            first = '├─'
            rest = '│ '
        val_lines = handle_sub_node_condensed(val, first, rest)
        lines += val_lines
    return lines


def node_to_lines_full(node: AST) -> List[str]:
    pass


def handle_sub_node_condensed(val, first, rest) -> List[str]:
    if isinstance(val, AST):
        val_lines = node_to_lines_condensed(val)
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
                sub_first = rest + '└─'
                sub_rest = rest + '  '
            else:
                sub_first = rest + '├─'
                sub_rest = rest + '│ '
            val_lines += handle_sub_node_condensed(sub_val, sub_first, sub_rest)
        return val_lines
    else:
        return [first + repr(val)]
