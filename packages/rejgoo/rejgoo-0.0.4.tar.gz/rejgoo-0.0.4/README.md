# REJGOO the equation solver

[![PyPi](https://img.shields.io/pypi/v/rejgoo.svg)](https://pypi.python.org/pypi/rejgoo)
[![PyPi](https://readthedocs.org/projects/rejgoo/badge/?version=latest)](https://rejgoo.readthedocs.io/en/latest/?version=latest)

Rejgoo is a Python package that solves mathematical equations!
The main aim of rejgoo is too be the fastest and simplest way to solve system of mathematical equations.
You can solve any number of equation with just one line of code!  
Rejgoo is also capable of handling thermodynamic equations🔥: [Thermodynamic Properties Documentation](https://github.com/mertomax/rejgoo/blob/main/docs/thermo.rst)

CREDITS:
--------

This project is developed by Mahdi Hajebi, based on the original version developed as his bachelor final project,
titled "Thermodynamics Equation Set Solver", to fulfill for his BSc in mechanical engineering
at University of Hormozgan under the supervision of Inst. Abdulhamid N.M. Ansari.

HOW TO USE:
-----------

At first the ``eqs`` class needs to be imported.
This class handle the process of solving equations.

Then an instance of ``eqs`` class is created. The instance takes a string that contains equations as parameter.

A simple code sample is shown below:

```python
from rejgoo.rejgoo import eqs

text = """
x**2 + x  = 2
3*a + 2*b = 16
-5*a + 5 = -b
sin(3*b*a) + cos(60) = d
"""

equations = eqs(x)
```

After running the code, The results will be printed automatically:


```
Total number of equations: 4
Total number of variables: 4
Number of isolated systems of equations: 2

system number: _1_
number of equations in this system: 3

solve
order     residual       equations
--------------------------------------------------------------------
1       0.00000       3*a+2*b=16
1       0.00000       -5*a+5=-b
2       0.00000       sin(3*b*a)+cos(60)=d
-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

system number: _2_
number of equations in this system: 1

solve
order     residual       equations
--------------------------------------------------------------------
1       0.00000       x**2+x=2
-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

Values of variables:

a:    2.0
b:    5.0
d:    1.0
x:    1.0
```

The results can be accesed by ``solved_vars`` attribute as an dictionary:
``equations.solved_vars``


Keyword arguments:
------------------

You can also provide folowing kwargs to ``eqs`` calls:

* verbose:

verbose is a boolean, By default verbose is set to True.
If you don't like the results to be printed, just set ``verbose = False``

``eqs(text, verbose=False)``

* init_vals:

init_vals is a dictionary that contains initial guesses for variables.

``eqs(text, init_vals={'x':3})``

* max_iter

max_iter is an integer that shows number of iteration that newton raphson will do.
By default it is set to 100.

``eqs(text, max_iter=200)``

* learning_rate

learning rate is a float number that is multiplied to newton raphson step sizes.
learning_rate by default is 1, which means that steps are not changed!
By using smaler numbers, we can prevent over shooting!

``eqs(text, learning_rate=0.8)``

* random_state:

random_state is an integer that can guarantee reproducible initial guesses.

``eqs(text, random_state=42)``