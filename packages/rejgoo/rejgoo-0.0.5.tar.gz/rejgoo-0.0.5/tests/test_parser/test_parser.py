from rejgoo.rejgoo import eqs
import pytest

systems = [
    "x=5",
    "3=x",
    "x**2 + 3*x = 32",
    "x = 1/x",
    "x**2+3*x=39",

    """
    2*x + 3*y = 54
    4*x - 5*y = 43
    """,

    """
    x**2 + y**2 = 56
    x - y = 3
    """,

    """
    x**2 + 3*x = 32
    a - x + b = 23
    b * x * a = b - a
    """,

    """
    8*e = e**2 + 16
    d + c = e**e
    b*a = c*d
    b = a * a
    a = 2
    """
    ]

answers = [
    [[['x=5']]],
    [[['3=x']]],
    [[['x**2+3*x=32']]],
    [[['x=1/x']]],
    [[['x**2+3*x=39']]],
    [[['2*x+3*y=54', '4*x-5*y=43']]],
    [[['x**2+y**2=56', 'x-y=3']]],
    [[['x**2+3*x=32'], ['a-x+b=23', 'b*x*a=b-a']]],
    [[['8*e=e**2+16'], ['a=2'], ['b=a*a'], ['d+c=e**e', 'b*a=c*d']]]
    ]


@pytest.mark.parametrize("raw_eqs,ordered_eqs", list(zip(systems, answers)))
def test_parser(raw_eqs, ordered_eqs):
    assert eqs(raw_eqs).ordered_eqs == ordered_eqs
