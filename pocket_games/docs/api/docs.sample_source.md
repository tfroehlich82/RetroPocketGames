# docs/sample_source.py

Sample module demonstrating documentation formatting.

This module shows how docstrings and inline comments are parsed into Sphinx-ready documentation.

## hello_world

`def hello_world(message: str) -> str`

Generates a welcome message based on input.

This function takes a string and returns a formatted greeting with the provided message.

Args:
    message: The greeting message to echo.

Returns:
    A "Hello, {message}!" greeting.

Example:
    >>> hello_world("User")
  

## add_numbers

`def add_numbers(a: int, b: int) -> int`

Adds two numbers together using addition.

Simple function that computes the sum of a and b.

Args:
    a: First integer to add.
    b: Second integer to add.

Returns:
    Sum of a and b as an integer.

Example:
    >>> add_numbers(2, 3)
  

## multiply_vectors

`def multiply_vectors(a: list[float], b: list[float]) -> list[float]`

Calculates element-wise product of two vectors.

## Calculator

`class Calculator`

A utility class for basic arithmetic operations.

This class provides methods for common mathematical calculations.
Supports addition, subtraction, multiplication, and division.

### add

`def add(cls, a: int, b: int) -> int`

Adds two numbers using the class method.

### multiply

`def multiply(a: int, b: int) -> int`

Multiplies two numbers using static method syntax.

### subtract

`def subtract(self, a: int, b: int) -> int`

Subtracts b from a.

## GeometryCalculator

`class GeometryCalculator(Calculator)`

A specialized calculator for geometric calculations.

Extends the Calculator class with geometry-specific operations.
Includes methods for calculating area and perimeter of shapes.

### calculate_area

`def calculate_area(self, shape_name: str, width: float, height: float) -> float`

Calculates area based on shape type.
