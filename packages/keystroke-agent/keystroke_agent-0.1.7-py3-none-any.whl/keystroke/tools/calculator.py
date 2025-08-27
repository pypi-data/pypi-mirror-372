import math


def add(a: float, b: float) -> float:
    """
    Add two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The sum of a and b.
    """
    return a + b


def subtract(a: float, b: float) -> float:
    """
    Subtract one number from another.

    Args:
        a (float): The number to subtract from.
        b (float): The number to subtract.

    Returns:
        float: The result of a - b.
    """
    return a - b


def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The product of a and b.
    """
    return a * b


def divide(a: float, b: float) -> float:
    """
    Divide one number by another.

    Args:
        a (float): The numerator.
        b (float): The denominator.

    Returns:
        float: The result of a / b.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def power(a: float, b: float) -> float:
    """
    Raise a number to the power of another.

    Args:
        a (float): The base.
        b (float): The exponent.

    Returns:
        float: The result of a ** b.
    """
    return a**b


def square_root(a: float) -> float:
    """
    Compute the square root of a number.

    Args:
        a (float): The number.

    Returns:
        float: The square root of a.

    Raises:
        ValueError: If a is negative.
    """
    if a < 0:
        raise ValueError("Cannot compute square root of negative number")
    return math.sqrt(a)


def logarithm(a: float, base: float = math.e) -> float:
    """
    Compute the logarithm of a number with a specified base.

    Args:
        a (float): The number.
        base (float, optional): The logarithm base. Defaults to math.e.

    Returns:
        float: The logarithm of a to the given base.

    Raises:
        ValueError: If a is not positive or base is invalid.
    """
    if a <= 0:
        raise ValueError("Cannot compute logarithm of non-positive number")
    if base <= 0 or base == 1:
        raise ValueError("Invalid logarithm base")
    return math.log(a, base)


def sin(angle: float) -> float:
    """
    Compute the sine of an angle in radians.

    Args:
        angle (float): The angle in radians.

    Returns:
        float: The sine of the angle.
    """
    return math.sin(angle)


def cos(angle: float) -> float:
    """
    Compute the cosine of an angle in radians.

    Args:
        angle (float): The angle in radians.

    Returns:
        float: The cosine of the angle.
    """
    return math.cos(angle)


def tan(angle: float) -> float:
    """
    Compute the tangent of an angle in radians.

    Args:
        angle (float): The angle in radians.

    Returns:
        float: The tangent of the angle.
    """
    return math.tan(angle)


def factorial(n: int) -> int:
    """
    Compute the factorial of a non-negative integer.

    Args:
        n (int): The number.

    Returns:
        int: The factorial of n.

    Raises:
        ValueError: If n is not a non-negative integer.
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("Factorial is only defined for non-negative integers")
    return math.factorial(n)
