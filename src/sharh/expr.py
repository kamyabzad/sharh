from __future__ import annotations

from functools import reduce
from typing import List

def add_literal_literal(l1: Literal, l2: Literal):
    return Disjunction([l1, l2])


def add_literal_conjunction(
    literal: Literal, conjunction: Conjunction, literal_first=True
):
    return Conjunction(
        list(
            map(
                lambda d: add_literal_disjunction(
                    literal=literal, disjunction=d, literal_first=literal_first
                ),
                conjunction.disjunctions,
            )
        )
    )


def add_literal_disjunction(
    literal: Literal, disjunction: Disjunction, literal_first=True
):
    if literal_first:
        return Disjunction([literal, *disjunction.literals])
    return Disjunction([*disjunction.literals, literal])


def add_conjunction_conjunction(c1: Conjunction, c2: Conjunction):
    return reduce(
        lambda i, j: Conjunction([*i.disjunctions, *j.disjunctions]),
        map(
            lambda d: add_conjunction_disjunction(c1, d, conjunction_first=False),
            c2.disjunctions,
        ),
        Conjunction([]),
    )


def add_conjunction_disjunction(
    conjunction: Conjunction, disjunction: Disjunction, conjunction_first=True
):

    if conjunction_first:
        return Conjunction(
            list(
                map(
                    lambda d: add_disjunction_disjunction(d, disjunction),
                    conjunction.disjunctions,
                )
            )
        )

    return Conjunction(
        list(
            map(
                lambda d: add_disjunction_disjunction(disjunction, d),
                conjunction.disjunctions,
            )
        )
    )


def add_disjunction_disjunction(d1: Disjunction, d2: Disjunction):
    return Disjunction([*d1.literals, *d2.literals])


def mul_literal_literal(l1: Literal, l2: Literal):
    return Conjunction([Disjunction([l1]), Disjunction([l2])])


def mul_literal_conjunction(
    literal: Literal, conjunction: Conjunction, literal_first=True
):
    if literal_first:
        return Conjunction([Disjunction([literal]), *conjunction.disjunctions])
    return Conjunction([*conjunction.disjunctions, Disjunction([literal])])


def mul_literal_disjunction(
    literal: Literal, disjunction: Disjunction, literal_first=True
):
    if literal_first:
        return Conjunction([Disjunction([literal]), disjunction])
    return Conjunction([disjunction, Disjunction([literal])])


def mul_conjunction_conjunction(c1: Conjunction, c2: Conjunction):
    return Conjunction([*c1.disjunctions, *c2.disjunctions])


def mul_conjunction_disjunction(
    conjunction: Conjunction, disjunction: Disjunction, conjunction_first=True
):
    if conjunction_first:
        return Conjunction([disjunction, *conjunction.disjunctions])
    return Conjunction([*conjunction.disjunctions, disjunction])


def mul_disjunction_disjunction(d1: Disjunction, d2: Disjunction):
    return Conjunction([d1, d2])


class Literal:
    def __init__(self, left, op, right):
        self.op = op
        self.left = left
        self.right = right

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return str([self.left, self.op, self.right])

    def __repr__(self):
        return f"Literal <{str(self)}>"

    def __eq__(self, other):
        return str(self) == str(other)

    def __mul__(self, other):
        if isinstance(other, Literal):
            return mul_literal_literal(self, other)
        if isinstance(other, Conjunction):
            return mul_literal_conjunction(self, other)
        if isinstance(other, Disjunction):
            return mul_literal_disjunction(self, other)

    def __add__(self, other):
        if isinstance(other, Literal):
            return add_literal_literal(self, other)
        if isinstance(other, Conjunction):
            return add_literal_conjunction(self, other)
        if isinstance(other, Disjunction):
            return add_literal_disjunction(self, other)

    def get_op(self):
        return self.op

    def get_lvalue(self):
        return self.left

    def get_rvalue(self):
        return self.right

    def to_expr_notation(self):
        return [self.get_lvalue(), self.get_op(), self.get_rvalue()]


class Disjunction:
    def __init__(self, literals: List[Literal]):
        self.literals = literals

    def __str__(self):
        return f"( {' or '.join(map(lambda i: str(i), self.literals))} )"

    def __repr__(self):
        return f"Disjunction <{str(self)}>"

    def __mul__(self, other):
        if isinstance(other, Literal):
            return mul_literal_disjunction(other, self, literal_first=False)
        if isinstance(other, Conjunction):
            return mul_conjunction_disjunction(other, self, conjunction_first=True)
        if isinstance(other, Disjunction):
            return mul_disjunction_disjunction(self, other)

    def __add__(self, other):
        if isinstance(other, Literal):
            return add_literal_disjunction(other, self, literal_first=False)
        if isinstance(other, Conjunction):
            return add_conjunction_disjunction(other, self, conjunction_first=False)
        if isinstance(other, Disjunction):
            return add_disjunction_disjunction(self, other)

    def to_expr_notation(self):
        if len(self.literals) == 0:
            return []
        elif len(self.literals) == 1:
            return self.literals[0].to_expr_notation()

        return ["OR", *map(lambda literal: literal.to_expr_notation(), self.literals)]


class Conjunction:
    def __init__(self, disjunctions: List[Disjunction]):
        self.disjunctions = disjunctions

    def __repr__(self):
        return f"Conjunction <{str(self)}>"

    def __str__(self):
        return f"( {' AND '.join(map(lambda i: str(i), self.disjunctions))} )"

    def __mul__(self, other):
        if isinstance(other, Literal):
            return mul_literal_conjunction(other, self, literal_first=False)
        if isinstance(other, Conjunction):
            return mul_conjunction_conjunction(other, self)
        if isinstance(other, Disjunction):
            return mul_conjunction_disjunction(self, other)

    def __add__(self, other):
        if isinstance(other, Literal):
            return add_literal_conjunction(other, self, literal_first=False)
        if isinstance(other, Conjunction):
            return add_conjunction_conjunction(other, self)
        if isinstance(other, Disjunction):
            return add_conjunction_disjunction(self, other)

    def to_expr_notation(self):
        if len(self.disjunctions) == 0:
            return []
        elif len(self.disjunctions) == 1:
            return self.disjunctions[0].to_expr_notation()

        return [
            "AND",
            *map(lambda disjunction: disjunction.to_expr_notation(), self.disjunctions),
        ]
