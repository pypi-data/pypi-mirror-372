"""Rejgoo is a Python package that solves mathematical equations!
The main aim of rejgoo is too be the fastest and simplest way to solve system of mathematical equations.
You can solve any number of equation with just one line of code!  
Rejgoo is also capable of handling thermodynamic equations


HOW TO USE:

At first the ``eqs`` class needs to be imported.
This class handle the process of solving equations.

Then an instance of ``eqs`` class is created. The instance takes a string that contains equations as parameter.

A simple code sample is shown below:

from rejgoo.rejgoo import eqs

text = '''
x**2 + x  = 2
3*a + 2*b = 16
-5*a + 5 = -b
sin(3*b*a) + cos(60) = d
'''

equations = eqs(x)
"""

__author__ = """Mahdi Hajebi"""
__email__ = 'merto071@yahoo.com'
__version__ = '0.0.5'
