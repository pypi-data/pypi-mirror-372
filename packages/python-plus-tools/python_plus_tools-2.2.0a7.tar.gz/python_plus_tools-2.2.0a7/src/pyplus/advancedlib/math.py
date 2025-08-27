from decimal import Decimal as long
from fractions import Fraction as fraction
from functools import cache
from pyplus.tools.dec import dint, Calc

import matplotlib.pyplot as plt
import numpy as np
import numpy, sympy, scipy, numba, matplotlib, math

from deprecated import deprecated
from typing_extensions import List, Tuple, Union, Dict


def solve_equations(
    *equations, variables=None
) -> List[dict[sympy.Symbol, Union[int, float]]]:
    """
    Solve equations.

    :param equations: The equations to solve.
    :param variables: The variables to solve for.
    :return: A list of solutions.
    """
    if not equations:
        return []

    if variables is None:
        variables = set()
        for eq in equations:
            variables.update([c for c in eq if c.isalpha()])
        variables = sorted(variables)

    sym_vars = sympy.symbols(" ".join(variables))
    sym_equations = []

    for eq_str in equations:
        left, right = eq_str.split("=") if "=" in eq_str else (eq_str, "0")
        sym_equations.append(
            sympy.Eq(
                eval(left, {v: sym_vars[i] for i, v in enumerate(variables)}),
                eval(right, {v: sym_vars[i] for i, v in enumerate(variables)}),
            )
        )

    solutions = sympy.solve(sym_equations, sym_vars, dict=True)
    return solutions


def solve_formula(formula_str: str, **kwargs) -> Union[int, float]:
    """
    Solve a mathematical formula.

    :param formula_str: The formula to solve.
    :param kwargs: The variables to substitute in the formula.
    :return: The result of the formula.
    """
    sym_vars = sympy.symbols(list(kwargs.keys()))
    expr = sympy.sympify(formula_str)
    return expr.subs({k: v for k, v in zip(sym_vars, kwargs.values())})


def solve_formulas(formula_strs: List[str], **kwargs) -> List[Union[int, float]]:
    """
    Solve multiple mathematical formulas.

    :param formula_strs: The formulas to solve.
    :param kwargs: The variables to substitute in the formulas.
    :return: A list of the results of the formulas.
    """
    formula_outputs = []
    for formula_str in formula_strs:
        formula_outputs.append(solve_formula(formula_str, **kwargs))

    return formula_outputs


def decompose_fraction(numerator: int, denominator: int) -> Tuple[int, int]:
    """
    Decompose a fraction into its numerator and denominator.

    :param numerator: The numerator of the fraction.
    :param denominator: The denominator of the fraction.
    :return: A tuple containing the numerator and denominator of the fraction.
    """
    if numerator == 0:
        return 0, 1
    elif denominator == 0:
        return 1, 0
    else:
        gcd = math.gcd(numerator, denominator)
        return numerator // gcd, denominator // gcd


def decompose_prime(n: int, expand: bool = False) -> Union[List[int], Dict[int, int]]:
    decompose_prime_factors = sympy.factorint(n)
    if expand:
        decompose_prime_factors_temp = []
        for k, v in decompose_prime_factors.items():
            decompose_prime_factors_temp.extend([k] * v)
        decompose_prime_factors = decompose_prime_factors_temp
    return decompose_prime_factors


def joseph_problem(n: int, k: int=2) -> int:
    """
    Joseph problem is a classic problem in computer science. It is a problem of finding the last person standing in a circle of people. The problem is named after the Greek mathematician Josephus. The problem can be solved using a simple algorithm called the Josephus problem. The algorithm works as follows:

    1. Start with a list of n people numbered from 1 to n.
    2. Start with a pointer to the first person in the list.
    3. Remove the person pointed to by the pointer.
    4. Move the pointer n-1 positions ahead in the list.
    5. Repeat steps 3 and 4 until there is only one person left in the list.
    6. The last person remaining in the list is the last person standing in the circle.

    The Josephus problem is a classic example of a mathematical problem that can be solved using a simple algorithm. The algorithm is simple and easy to understand, but it can be improved by using more advanced techniques such as dynamic programming or memoization.
    Args:
        n (int): The number of people in the circle.
    Returns:
        int: The number of the last person standing in the circle.
    """
    if n == 1:
        return 1
    else:
        return (joseph_problem(n - 1, k) + k - 1) % n + 1


@cache
def fib(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def is_palindrome(n: int) -> bool:
    return str(n) == str(n)[::-1]


def is_even(n: int) -> bool:
    return n % 2 == 0


def is_odd(n: int) -> bool:
    return n % 2 == 1


def c(n: int, r: int) -> int:
    return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))


@deprecated(
    "Function 'prime_factors' is deprecated in 2.2.0.It will be removed in 3.0.0. Use 'decompose_prime' instead."
)
def prime_factors(n: int) -> List[int]:
    factors = []
    d = 2
    while d * d <= n:
        while (n % d) == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def prime_divisors(n: int) -> List[int]:
    factors = decompose_prime(n)
    divisors = []
    for factor in factors:
        divisors.append(c(n, factor))
    return divisors


def p(n: int, r: int) -> int:
    return c(n, r) // math.factorial(r)


def is_prime(n: int) -> bool:
    """检查一个数是否为素数"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w
    return True


def get_primes(n: int) -> int:
    primes = []
    i = 2
    while len(primes) < n:
        if is_prime(i):
            primes.append(i)
        i += 1
    return primes[-1]


def perfect_number(n: int) -> int:
    count = 0
    p = 2
    while True:
        mersenne = (1 << p) - 1
        if is_prime(p) and is_prime(mersenne):
            perfect_num = (1 << (p - 1)) * mersenne
            count += 1
            if count == n:
                return perfect_num
        p += 1


def is_perfect_number(num: int) -> bool:
    if num % 2 != 0:
        return False

    p = 2
    while True:
        mersenne = (1 << p) - 1
        perfect_num = (1 << (p - 1)) * mersenne

        if perfect_num == num:
            return is_prime(p) and is_prime(mersenne)
        elif perfect_num > num:
            return False
        p += 1


def short_div(divisor: int, *dividends) -> List[Tuple[int, int]]:
    """
    Short division is a method of dividing a number by a divisor by repeatedly subtracting the divisor from the dividend until the dividend is less than the divisor.

    The method is named after the French mathematician Gauss. The method is useful for computing the remainder of a division and is used in cryptography.

    :param divisor: The divisor to divide by.
    :param dividends: The dividends to divide by the divisor.
    :return: The remainder of the division.
    """
    if not dividends:
        raise ValueError("No dividends provided")
    if divisor == 0:
        raise ZeroDivisionError("Division by zero")

    results = []
    for dividend in dividends:
        quotient, remainder = divmod(dividend, divisor)
        results.append((quotient, remainder))
    return results


def common_factors(a: int, b: int) -> List[int]:
    """
    Compute the common factors of two integers.
    :param a: The first integer.
    :param b: The second integer.
    :return: A list of the common factors of the two integers.
    """
    gcd_val = math.gcd(abs(a), abs(b))

    if gcd_val == 0:
        return []

    factors = set()
    for i in range(1, int(math.sqrt(gcd_val)) + 1):
        if gcd_val % i == 0:
            factors.add(i)
            factors.add(gcd_val // i)

    return sorted(factors)

def no_recursion_fib(n: int) -> int:
    if n == 0:
        return 0
        
    if n == 1:
        return 1
    elif n == 2:
        return 1
    
    a,b = 0,1
    for _ in range(3,n+1):
        a, b = b, a+b
    return b
    

del deprecated, List, Tuple, Union, Dict
