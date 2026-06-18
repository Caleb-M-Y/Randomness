"""
Python Learning Journey
======================
This single file is a guided walkthrough from absolute basics to advanced topics.

How to use this file:
1) Read one section at a time.
2) Run the file and inspect the output.
3) Comment/uncomment lines to experiment.
4) Modify examples and break things on purpose to learn faster.

Run with:
    python python_learning_journey.py
"""

# -----------------------------
# SECTION 1: HELLO, WORLD!
# -----------------------------
# print(...) sends text to the console.
# This is the traditional first program in most languages.
print("\n=== Section 1: Hello, World! ===")
print("Hello, World!")


# -----------------------------
# SECTION 2: VARIABLES + BASIC TYPES
# -----------------------------
# A variable is a named label that points to a value in memory.
# In Python, you do NOT declare type explicitly for basic variables.
# Python is dynamically typed: types are checked at runtime.
print("\n=== Section 2: Variables and Types ===")
name = "Ada"               # str (string)
age = 28                    # int (integer)
height_m = 1.67             # float (decimal number)
is_engineer = True          # bool (True/False)
complex_number = 2 + 3j     # complex (advanced math type)

print(name, age, height_m, is_engineer, complex_number)
print(type(name), type(age), type(height_m), type(is_engineer), type(complex_number))

# Common conversions (casting):
# int("42") -> 42
# float("3.14") -> 3.14
# str(99) -> "99"
converted_age = int("42")
print("Converted age:", converted_age)


# -----------------------------
# SECTION 3: OPERATORS
# -----------------------------
# Arithmetic operators: + - * / // % **
# Comparison operators: == != > < >= <=
# Logical operators: and or not
print("\n=== Section 3: Operators ===")
a = 10
b = 3
print("a + b =", a + b)
print("a - b =", a - b)
print("a * b =", a * b)
print("a / b =", a / b)    # True division (float result)
print("a // b =", a // b)  # Floor division (integer-like quotient)
print("a % b =", a % b)    # Remainder
print("a ** b =", a ** b)  # Exponentiation (10^3)

print("a > b:", a > b)
print("a == b:", a == b)
print("(a > 5) and (b < 5):", (a > 5) and (b < 5))


# -----------------------------
# SECTION 4: STRINGS
# -----------------------------
# Strings are sequences of Unicode characters.
# You can use single quotes '...' or double quotes "...".
print("\n=== Section 4: Strings ===")
first = "Grace"
last = "Hopper"
full = first + " " + last  # Concatenation
print(full)

# f-strings (formatted strings) are the modern and clean way to format text.
language = "Python"
version = 3.12
print(f"Learning {language} version {version}")

# Useful string methods:
text = "  python is fun  "
print(text.strip())         # Removes leading/trailing spaces
print(text.upper())         # UPPERCASE
print(text.replace("fun", "powerful"))
print("py" in text)         # Membership check


# -----------------------------
# SECTION 5: COLLECTIONS (LIST, TUPLE, SET, DICT)
# -----------------------------
# List: ordered, mutable, allows duplicates
# Tuple: ordered, immutable
# Set: unordered, mutable, unique values only
# Dict: key-value mapping
print("\n=== Section 5: Collections ===")

# LIST
fruits = ["apple", "banana", "apple"]
fruits.append("orange")
print("List:", fruits)
print("First fruit:", fruits[0])

# TUPLE
coordinates = (10.0, 20.0)
print("Tuple:", coordinates)

# SET
unique_numbers = {1, 2, 2, 3, 4}
print("Set removes duplicates:", unique_numbers)

# DICT
person = {"name": "Linus", "age": 35, "role": "developer"}
person["age"] = 36
print("Dict:", person)
print("Name from dict:", person["name"])


# -----------------------------
# SECTION 6: CONTROL FLOW (if, for, while)
# -----------------------------
print("\n=== Section 6: Control Flow ===")
score = 87

# if / elif / else chooses branches based on conditions.
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C or below"

print("Grade:", grade)

# for loop iterates over an iterable (like list, range, string, etc.)
print("for loop over range(3):")
for i in range(3):
    print(" i =", i)

# while loop repeats while condition is True.
print("while loop countdown:")
count = 3
while count > 0:
    print(" count =", count)
    count -= 1

# break exits loop early, continue skips current iteration.
print("break/continue demo:")
for n in range(1, 6):
    if n == 2:
        continue
    if n == 5:
        break
    print(" n =", n)


# -----------------------------
# SECTION 7: FUNCTIONS
# -----------------------------
# Functions package reusable logic.
# def defines a function. return sends a value back to the caller.
print("\n=== Section 7: Functions ===")

def greet(user_name):
    """Return a greeting string for the user."""
    return f"Hello, {user_name}!"


def add(x, y=0):
    """Add two numbers. y has a default value."""
    return x + y

print(greet("Sam"))
print("add(5, 7) =", add(5, 7))
print("add(5) =", add(5))

# Variable-length arguments:
def summarize(*numbers, **metadata):
    """Example of *args and **kwargs usage."""
    total = sum(numbers)
    return {"total": total, "count": len(numbers), "metadata": metadata}

print(summarize(1, 2, 3, source="demo", verified=True))


# -----------------------------
# SECTION 8: SCOPE + LAMBDA + HIGHER-ORDER FUNCTIONS
# -----------------------------
print("\n=== Section 8: Scope and Functional Tools ===")

# Scope: where a variable is visible/accessible.
global_value = "I am global"


def scope_demo():
    local_value = "I am local"
    print(global_value)
    print(local_value)

scope_demo()

# lambda creates a small anonymous function.
square = lambda x: x * x
print("square(6) =", square(6))

# map/filter are functional tools.
nums = [1, 2, 3, 4, 5]
squared_nums = list(map(lambda n: n * n, nums))
even_nums = list(filter(lambda n: n % 2 == 0, nums))
print("map squares:", squared_nums)
print("filter evens:", even_nums)


# -----------------------------
# SECTION 9: COMPREHENSIONS
# -----------------------------
# Comprehensions are concise ways to build collections.
print("\n=== Section 9: Comprehensions ===")

list_comp = [n * 2 for n in range(5)]
set_comp = {n % 3 for n in range(10)}
dict_comp = {n: n * n for n in range(4)}
print("List comprehension:", list_comp)
print("Set comprehension:", set_comp)
print("Dict comprehension:", dict_comp)


# -----------------------------
# SECTION 10: EXCEPTIONS (ERROR HANDLING)
# -----------------------------
# try/except lets your program recover from expected runtime issues.
print("\n=== Section 10: Exceptions ===")

def safe_divide(x, y):
    try:
        return x / y
    except ZeroDivisionError:
        # A specific exception branch is preferred over broad except.
        return "Cannot divide by zero"

print("10 / 2 ->", safe_divide(10, 2))
print("10 / 0 ->", safe_divide(10, 0))

# finally runs no matter what, useful for cleanup.
try:
    result = int("123")
finally:
    print("finally: this always runs")


# -----------------------------
# SECTION 11: FILE I/O
# -----------------------------
# with open(...) uses a context manager to auto-close the file.
print("\n=== Section 11: File I/O ===")
sample_path = "sample_output.txt"

with open(sample_path, "w", encoding="utf-8") as f:
    f.write("First line\n")
    f.write("Second line\n")

with open(sample_path, "r", encoding="utf-8") as f:
    contents = f.read()

print("File contents:\n" + contents)


# -----------------------------
# SECTION 12: MODULES + IMPORTS
# -----------------------------
# A module is a Python file. A package is a folder of modules.
# import lets you reuse existing code.
print("\n=== Section 12: Modules and Imports ===")
import math
import random
from datetime import datetime

print("math.sqrt(81) =", math.sqrt(81))
print("random.randint(1, 10) =", random.randint(1, 10))
print("Current timestamp:", datetime.now().isoformat(timespec="seconds"))


# -----------------------------
# SECTION 13: OBJECT-ORIENTED PROGRAMMING (CLASSES)
# -----------------------------
print("\n=== Section 13: OOP Basics ===")

class BankAccount:
    """Simple class to demonstrate encapsulation and methods."""

    def __init__(self, owner, balance=0.0):
        # self refers to this instance of the class.
        self.owner = owner
        self.balance = float(balance)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount

    def __repr__(self):
        # __repr__ is a developer-friendly string representation.
        return f"BankAccount(owner={self.owner!r}, balance={self.balance:.2f})"

acct = BankAccount("Taylor", 100)
acct.deposit(50)
acct.withdraw(30)
print(acct)


# -----------------------------
# SECTION 14: DATACLASSES (LESS BOILERPLATE FOR DATA OBJECTS)
# -----------------------------
print("\n=== Section 14: Dataclasses ===")
from dataclasses import dataclass


@dataclass
class Point:
    # Dataclass auto-generates __init__, __repr__, __eq__, etc.
    x: float
    y: float

    def distance_from_origin(self):
        return (self.x**2 + self.y**2) ** 0.5

p = Point(3, 4)
print(p, "distance:", p.distance_from_origin())


# -----------------------------
# SECTION 15: ITERATORS + GENERATORS
# -----------------------------
print("\n=== Section 15: Iterators and Generators ===")

# A generator yields values lazily (one at a time), saving memory.
def countdown(start):
    while start > 0:
        yield start
        start -= 1

for value in countdown(3):
    print("Generated:", value)


# -----------------------------
# SECTION 16: DECORATORS
# -----------------------------
# Decorators wrap/modify function behavior without editing the function body.
print("\n=== Section 16: Decorators ===")

def log_call(fn):
    def wrapper(*args, **kwargs):
        print(f"Calling {fn.__name__} with args={args}, kwargs={kwargs}")
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} returned {result}")
        return result

    return wrapper


@log_call
def multiply(x, y):
    return x * y

multiply(6, 7)


# -----------------------------
# SECTION 17: CONTEXT MANAGERS
# -----------------------------
# Context managers manage setup/teardown around a code block.
print("\n=== Section 17: Context Managers ===")
from contextlib import contextmanager


@contextmanager
def managed_resource(name):
    print(f"Opening resource: {name}")
    try:
        yield {"name": name}
    finally:
        print(f"Closing resource: {name}")


with managed_resource("demo-resource") as resource:
    print("Using resource:", resource)


# -----------------------------
# SECTION 18: TYPE HINTS
# -----------------------------
# Type hints improve readability, editor assistance, and static analysis.
print("\n=== Section 18: Type Hints ===")
from typing import List, Dict


def average(values: List[float]) -> float:
    if not values:
        raise ValueError("values cannot be empty")
    return sum(values) / len(values)


stats: Dict[str, float] = {"mean": average([2.0, 4.0, 6.0])}
print("Typed stats:", stats)


# -----------------------------
# SECTION 19: ASYNC PROGRAMMING (ADVANCED)
# -----------------------------
# async/await handles concurrent I/O tasks efficiently.
# This section simulates waiting with asyncio.sleep.
print("\n=== Section 19: Async Basics ===")
import asyncio


async def async_task(task_name, delay):
    print(f"{task_name} started")
    await asyncio.sleep(delay)
    print(f"{task_name} finished after {delay}s")
    return task_name


async def run_async_demo():
    results = await asyncio.gather(
        async_task("task-A", 0.2),
        async_task("task-B", 0.1),
    )
    print("Async results:", results)


# Running async code from a normal script:
asyncio.run(run_async_demo())


# -----------------------------
# SECTION 20: TESTING BASICS (UNITTEST)
# -----------------------------
# In real projects, tests usually live in separate files.
# This inline demo shows the core idea quickly.
print("\n=== Section 20: Testing Basics ===")
import unittest


class TestMathHelpers(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_average(self):
        self.assertAlmostEqual(average([1.0, 2.0, 3.0]), 2.0)


# Build and run tests programmatically so this tutorial stays one-file.
suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMathHelpers)
result = unittest.TextTestRunner(verbosity=1).run(suite)
print("All tests passed:", result.wasSuccessful())


# -----------------------------
# SECTION 21: PYTHONIC TIPS + NEXT STEPS
# -----------------------------
print("\n=== Section 21: Pythonic Tips ===")

# 1) Prefer clear names over short cryptic names.
# 2) Keep functions small and focused.
# 3) Use list/dict comprehensions where they improve readability.
# 4) Catch specific exceptions.
# 5) Write tests for business logic.
# 6) Use virtual environments for project isolation.
# 7) Use linting/formatting tools (ruff, black, mypy) in real projects.

print("You now saw Python from beginner to advanced concepts in one file.")
print("Next: split concepts into separate modules and build a small project.")
