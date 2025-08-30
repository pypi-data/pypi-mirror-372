from rejgoo.rejgoo import eqs
import pytest

systems = [
    """
    a+b+c=10
    x**2 + 7*x +10=0
    x + z = 21
    z * y = 7
    a + b = 5
    a - b = 3
    """,

    """
    a**3 - 3*a**2 + 5*a = 9
    exp(a) = b
    sin(b) ** 2 + cos(b) ** 2 = c
    """
    ]

seeds = [47, 59]

answers = [
    {'a':4,
     'b':1,
     'c':5,
     'x':-1.9999999999999998,
     'z':23,
     'y':0.30434782608695654},

    {'a': 2.4561642461359083,
     'b': 11.660000760390158,
     'c': 1}
    ]


@pytest.mark.parametrize("raw_eqs,seed,answer", list(zip(systems, seeds, answers)))
def test_parser(raw_eqs, seed, answer):
    assert eqs(raw_eqs, random_seed = seed).solved_vars == answer
