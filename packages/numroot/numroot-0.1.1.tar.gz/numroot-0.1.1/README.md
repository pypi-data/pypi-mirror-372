# NumRoot

[![PyPI version](https://badge.fury.io/py/numroot.svg)](https://badge.fury.io/py/numroot)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Python package for numerical resolution of nonlinear equations with several numerical analysis methods.

## 🚀 Installation

```bash
pip install numroot
```

### Development installation

```bash
pip install numroot[dev]
```

## 📖 Quick use

```python
from numroot import NonlinearSolver

# Create a solver object
solver = NonlinearSolver()

# Define a function to analyse (example: x² - 2 = 0)
def f(x):
    return x**2 - 2

# Bissection method
result = solver.bisection(f, x_a=0, x_b=2, epsilon=1e-6)
print(f"Root found: {result.root}")  # ≈ 1.414
print(f"Number of iterations: {result.iterations}")

# Newton-Raphson method
def df(x):
    return 2*x

result = solver.newton_raphson(f, df, x_0=1.5, epsilon=1e-6)
print(f"Root found: {result.root}")  # ≈ 1.414
print(f"Number of iterations: {result.iterations}")

# Secant method
result = solver.secant(f, x_0=1.0, x_1=2.0, epsilon=1e-6)
print(f"Root found: {result.root}")  # ≈ 1.414
print(f"Number of iterations: {result.iterations}")
```

## 🔧 Available methods

### Bissection method
- **Advantages**: Always convergent, robust
- **Disadvantages**: Slow convergence
- **Usage**: When you have an interval [a,b] where f(a) and f(b) have opposite signs

```python
result = solver.bisection(func, a, b, epsilon=1e-6, maxiter=100)
```

### Newton-Raphson method
- **Advantages**: Very fast quadratic convergence
- **Disadvantages**: Requires derivative, may diverge
- **Usage**: When you know the derivative and have a good initial estimate

```python
result = solver.newton_raphson(func, dfunc, x0, epsilon=1e-6, maxiter=100)
```

### Secant method
- **Advantages**: No derivative needed, super-linear convergence
- **Disadvantages**: Can be unstable with bad initial points.
- **Uses**: Compromise between bisection and Newton-Raphson

```python
result = solver.secant(func, x0, x1, epsilon=1e-6, maxiter=100)
```

## 🎯 Typical use cases

- Solving physical equations (trajectories, oscillations)
- Engineering calculations (balance points, intersections)
- Mathematical modeling (zeros of complex functions)
- Research and education in numerical analysis

## 📋 Requirements

- Python 3.8+
- NumPy >= 1.20.0

## 🔗 Links

- [Documentation complète](https://numroot.readthedocs.io/)
- [PyPI](https://pypi.org/project/numroot/)
- [Issues GitHub](https://github.com/Onniryss/numroot/issues)
- [Code source](https://github.com/Onniryss/numroot)

## 📈 Roadmap

- [ ] Systems of non-linear equations
- [ ] Ordinary differential equations
- [ ] Numerical optimization
- [ ] Graphical interface
- [ ] Interactive visualizations

## 📚 References

- [Geeks for Geeks - Secant method](https://www.geeksforgeeks.org/secant-method-of-numerical-analysis/)
- [Math Libretexts - Bisection Method](https://math.libretexts.org/Workbench/Numerical_Methods_with_Applications_(Kaw)/3:_Nonlinear_Equations/3.03:_Bisection_Methods_for_Solving_a_Nonlinear_Equation)
- [Math Libretexts - Newton-Raphson Method](https://math.libretexts.org/Workbench/Numerical_Methods_with_Applications_(Kaw)/3:_Nonlinear_Equations/3.04:_Newton-Raphson_Method_for_Solving_a_Nonlinear_Equation)