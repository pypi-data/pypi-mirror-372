from rejgoo.rejgoo import eqs
import pytest
import math

situations = [
    ("sin(30) = a", 0.49999999999999994),
    ("sin(210) = a", -0.5000000000000001),
    ("cos(-60) = a", 0.5000000000000001),
    ("cos(120) = a", -0.4999999999999998),
    ("tan(45) = a", 0.9999999999999999),
    ("cot(225) = a", 1.0000000000000002),
    ("asin(-0.5) = a", -30.000000000000004),
    ("acos(-1) = a", 180),
    ("atan(-1) = a", -45),
    ("acot(-2) = a", -26.56505117707799),
    ("sinh(0) = a", 0.0),
    ("sinh(10) = a", 11013.232874703393),
    ("cosh(-0.1) = a", 1.0050041680558035),
    ("cosh(-20) = a", 242582597.70489514),
    ("tanh(2) = a", 0.9640275800758169),
    ("coth(-2) = a", -1.03731472072754820),
    ("exp(1) = a", 2.718281828459045),
    ("exp(5) = a", 148.4131591025766),
    ("log(2.71828) = a", 0.999999327347282),
    ("log(55) = a", 4.007333185232471)
    ]


@pytest.mark.parametrize("raw_eqs,answer", situations)
def test_math_funcs_values(raw_eqs, answer):
    assert eqs(raw_eqs).solved_vars['a'] == answer
