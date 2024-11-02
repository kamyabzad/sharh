import re
from sharh.expr import Literal, Conjunction, Disjunction


class ParseError(Exception):
    pass

class ExpressionTree:
    def __init__(self):
        self.tree = []
        self.stack = []
        self.expressions = {}

    def push(self, expr_args):
        self.stack.append(Literal(*expr_args))

    def commit(self, operator):
        right = self.stack.pop()
        left = self.stack.pop()

        if re.match(t_AND, operator):
            self.stack.append(left * right)
        elif re.match(t_OR, operator):
            self.stack.append(left + right)


tree = ExpressionTree()


tokens = (
    "IDENTIFIER",
    "VALUE",
    "OP",
    "AND",
    "OR",
    "LPAREN",
    "RPAREN",
)

t_IDENTIFIER = r"[^and|or][a-zA-Z0-9]+"
t_VALUE = r"'[a-zA-Z0-9\/\-\.:,%\?=\s]+'"
t_OP = r"==|!==|<=|in|!in|has|!has|contains|!contains"
t_AND = r"(and)|(AND)"
t_OR = r"(or)|(OR)"
t_LPAREN = r"\("
t_RPAREN = r"\)"

# Ignored characters
t_ignore = " \t\n"

precedence = (
    ("left", "OR"),
    ("left", "AND"),
)


def t_error(t):
    t.lexer.skip(1)


import ply.lex as lex

lexer = lex.lex()


def p_error(t):
    raise ParseError()


def p_expression_unit(t):
    """expression : IDENTIFIER OP VALUE"""

    identifier = t[1]
    operation = t[2]
    value = t[3]

    value = value[1:-1]

    try:
        tree.push([identifier, operation, value])
    except ValueError as e:
        raise ParseError(*e.args)
    t[0] = [[t[1], t[2], t[3]]]


def p_expression_binop(t):
    """expression : expression AND expression
    | expression OR expression"""

    tree.commit(t[2])


def p_expression_group(t):
    "expression : LPAREN expression RPAREN"
    t[0] = t[2]


import ply.yacc as yacc

parser = yacc.yacc()


def parse(s):
    if not s.strip():
        return Disjunction([])

    global tree
    tree = ExpressionTree()
    parser.parse(s)

    try:
        parsed = tree.stack.pop()
    except IndexError:
        raise ParseError()

    if isinstance(parsed, Literal):
        parsed = Disjunction([parsed])
    if isinstance(parsed, Disjunction):
        parsed = Conjunction([parsed])

    return parsed
