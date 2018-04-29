class AST:
    def __eq__(self, other):
        if not type(other) == type(self):
            return False
        my_vars = vars(self)
        other_vars = vars(other)
        for var, val in my_vars.items():
            if not var in other_vars:
                return False
            if val != other_vars[var]:
                return False
        return True

    def __repr__(self):
        my_vars = vars(self)
        return self.__class__.__name__ + '(' + ', '.join(k + '=' + repr(v) for k, v in my_vars.items()) + ')'

    def __str__(self):
        return repr(self)
