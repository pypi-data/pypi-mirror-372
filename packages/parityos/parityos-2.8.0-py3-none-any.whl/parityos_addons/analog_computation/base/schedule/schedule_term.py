"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023 - 2025.
All rights reserved.
"""

from dataclasses import dataclass

import sympy

from parityos_addons.analog_computation import Observable
from parityos_addons.analog_computation.base.schedule.utils.sympy_utils import (
    sympy_expression_from_json,
    sympy_expression_to_json,
)


@dataclass(frozen=True)
class ScheduleTerm:
    """
    ScheduleTerm = coefficient * observable, where
    :param observable: Observable instance.
    :param coefficient: sympy.Expr representing a parameterized (or constant) coefficient.
    """

    observable: Observable
    coefficient: sympy.Expr

    @property
    def parameters(self) -> set:
        """
        :return: the parameters of the ScheduleTerm.
        """
        return self.coefficient.free_symbols

    def to_json(self) -> dict:
        """
        Converts the ScheduleTerm to json.

        :return: the ScheduleTerm in json-serializable format.
        """
        return {
            "observable": self.observable.to_json(),
            "coefficient": sympy_expression_to_json(self.coefficient),
        }

    @classmethod
    def from_json(cls, data) -> "ScheduleTerm":
        """
        Constructs a ScheduleTerm object from JSON data.

        :param data: a JSON-like dictionary with the corresponding fields.
        :return: a ScheduleTerm object.
        """
        return cls(
            Observable.from_json(data["observable"]),
            sympy_expression_from_json(data["coefficient"]),
        )

    def subs_parameters(self, args) -> "ScheduleTerm":
        """
        Substitutes parameters and returns a new Schedule.

        Passes the args to the Sympy's subs methods. From Sympy's docstrings:
        :param args:`args` is either:
                      - two arguments, e.g. foo.subs(old, new)
                      - one iterable argument, e.g. foo.subs(iterable). The iterable may be
                         o an iterable container with (old, new) pairs. In this case the
                           replacements are processed in the order given with successive
                           patterns possibly affecting replacements already made.
                         o a dict or set whose key/value items correspond to old/new pairs.
                           In this case the old/new pairs will be sorted by op count and in
                           case of a tie, by number of args and the default_sort_key. The
                           resulting sorted list is then processed as an iterable container
                           (see previous).
        :return: a new Schedule.
        """
        new_coefficient = self.coefficient.subs(args)

        return ScheduleTerm(self.observable, new_coefficient)

    def __str__(self) -> str:
        sympy_str = str(self.coefficient)
        if " - " in sympy_str or " + " in sympy_str:
            sympy_str = f"({sympy_str})"
        return sympy_str + " * [" + str(self.observable).replace("\n", "\n    ") + "]"
