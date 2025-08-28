"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2023 - 2025.
All rights reserved.
"""

import sympy


def sympy_expression_to_json(expression: sympy.Expr) -> dict:
    """
    Converts the sympy.Expr to json.

    :return: the sympy.Expr in json-serializable format

    :param expression: sympy.Expr.
    :return: dict of terms where values are the coefficients of the terms and
             keys are the string version of the terms (coefficients not included).
    """
    coefficient_dict = expression.as_coefficients_dict()
    return {str(key): value for key, value in coefficient_dict.items()}


def sympy_expression_from_json(data: dict) -> sympy.Expr:
    """
    Constructs a sympy.Expr object from JSON data.

    :param data: list of args in string format
    :return: a sympy.Expr object.
    """
    list_of_terms = [value * sympy.sympify(key) for key, value in data.items()]
    return _concatenate_list_of_sympy_expressions(list_of_terms)


def _concatenate_list_of_sympy_expressions(expressions: list[sympy.Expr]):
    concatenated_expression = expressions[0]
    for expression in expressions[1:]:
        concatenated_expression += expression
    return concatenated_expression
