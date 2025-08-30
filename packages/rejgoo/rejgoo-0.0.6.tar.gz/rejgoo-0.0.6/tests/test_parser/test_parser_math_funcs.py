from rejgoo.rejgoo import eqs
import pytest

systems = [
    "sin(5) * asin(0.3) * cos(5) * acos(0.5) = a",
    "tan(30) * cot(40) * acot(0.2) * acot(0.3) = a",
    "cosh(5) * sinh(5) * asinh(2) * acosh(3) = a",
    "tanh(5) * coth(5) * atanh(0.95) * acoth(5) = a",
    "exp(5) * log(5) = a",
    
    """
    tan(a**2) ** sin(a-5) = b
    c = sin(90)*4
    a = cos(40) / sin(c**2 - c + 4*sinh(c))
    """
    ]

answers = [
    [[['sin(5)*asin(0.3)*cos(5)*acos(0.5)=a']]],
    [[['tan(30)*cot(40)*acot(0.2)*acot(0.3)=a']]],
    [[['cosh(5)*sinh(5)*asinh(2)*acosh(3)=a']]],
    [[['tanh(5)*coth(5)*atanh(0.95)*acoth(5)=a']]],
    [[['exp(5)*log(5)=a']]],
    
    [[['c=sin(90)*4'],
      ['a=cos(40)/sin(c**2-c+4*sinh(c))'],
      ['tan(a**2)**sin(a-5)=b']]]
    ]


@pytest.mark.parametrize("raw_eqs,ordered_eqs", list(zip(systems, answers)))
def test_math_parser(raw_eqs, ordered_eqs):
    assert eqs(raw_eqs).ordered_eqs == ordered_eqs
