from rejgoo.rejgoo import eqs
import pytest

systems = [
    """
    p=4000000
    h1=thermo.water(Q=0,P=1800).H
    s1=thermo.water(Q=0,P=1800).S
    s2=s1
    h2=thermo.water(S=s2,P=p).H
    h3=thermo.water(T=823.15,P=p).H
    s3=thermo.water(T=823.15,P=p).S
    s4=s3
    h4=thermo.water(S=s3,P=1800).H
    q=h3-h2
    w=h3-h4
    ef=w/q
    """,

    """
    z = thermo.humidAir(T=320.15, P=101000, R=01.0).H
    """
    ]

seeds = [47, 59]

answers = [
    {'p':4000000,
     'h1':66488.75755507716,
     's1':236.61718616624606,
     's2':236.61718616624606,
     'h2':70487.558542229,
     'h3':3560335.175671077,
     's3':7235.454221131453,
     's4':7235.454221131453,
     'h4':2089064.2895026163,
     'q':3489847.617128848,
     'w':1471270.8861684606,
     'ef':0.42158599674873426},

    {'z':237447.346420575}
    ]


@pytest.mark.parametrize("raw_eqs,seed,answer", list(zip(systems, seeds, answers)))
def test_parser(raw_eqs, seed, answer):
    assert eqs(raw_eqs, random_seed = seed).solved_vars == answer
