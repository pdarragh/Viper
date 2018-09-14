from ..value import ForeignCloVal


def _print(s: str):
    print(s)


env = {
    'print': ForeignCloVal(_print, {})
}
