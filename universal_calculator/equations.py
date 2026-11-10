from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Protocol

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
	implicit_multiplication_application,
	parse_expr,
	standard_transformations,
)


TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def _make_symbol_table() -> dict[str, sp.Basic]:
	symbol_names = [
		"x",
		"y",
		"z",
		"t",
		"a",
		"b",
		"c",
		"d",
		"h",
		"u",
		"v",
		"w",
		"p",
		"q",
		"r",
		"s",
		"m",
		"n",
		"F",
		"V",
		"A",
		"R",
		"T",
		"P",
		"I",
		"Q",
		"E",
		"K",
		"W",
		"L",
		"s0",
		"x0",
		"v0",
		"theta",
		"mu",
		"rho",
		"sigma",
	]
	return {name: sp.symbols(name) for name in symbol_names}


SYMBOLS = _make_symbol_table()

SAFE_LOCAL_DICT: dict[str, sp.Basic] = {
	**SYMBOLS,
	"pi": sp.pi,
	"E": sp.E,
	"sin": sp.sin,
	"cos": sp.cos,
	"tan": sp.tan,
	"asin": sp.asin,
	"acos": sp.acos,
	"atan": sp.atan,
	"sqrt": sp.sqrt,
	"log": sp.log,
	"ln": sp.log,
	"exp": sp.exp,
	"abs": sp.Abs,
}


class IOContext(Protocol):
	def ask_text(self, prompt: str, default: str | None = None) -> str | None: ...

	def ask_float(self, prompt: str, default: float | None = None) -> float | None: ...

	def ask_int(self, prompt: str, default: int | None = None) -> int | None: ...

	def tell(self, text: str) -> None: ...

	def error(self, text: str) -> None: ...


@dataclass(frozen=True)
class Action:
	label: str
	handler: Callable[[IOContext], None]
	help_text: str = ""


class BaseCalculator(ABC):
	title: str = "Calculator"

	@abstractmethod
	def actions(self) -> list[Action]:
		raise NotImplementedError

	def run_cli(self, io: IOContext) -> None:
		while True:
			io.tell(f"\n{self.title}")
			action_items = self.actions()
			for index, action in enumerate(action_items, start=1):
				io.tell(f"{index}. {action.label}")
			io.tell("0. Back")

			selection_text = io.ask_text("Select an option")
			if selection_text is None:
				return

			try:
				selection = int(selection_text)
			except ValueError:
				io.error("Please enter a number from the menu.")
				continue

			if selection == 0:
				return
			if 1 <= selection <= len(action_items):
				action_items[selection - 1].handler(io)
			else:
				io.error("Selection out of range.")


class ConsoleIO:
	def tell(self, text: str) -> None:
		print(text)

	def ask_text(self, prompt: str, default: str | None = None) -> str | None:
		suffix = f" [{default}]" if default is not None else ""
		text = input(f"{prompt}{suffix}: ").strip()
		if not text and default is not None:
			return default
		return text if text else None

	def ask_float(self, prompt: str, default: float | None = None) -> float | None:
		while True:
			raw = self.ask_text(prompt, None if default is None else str(default))
			if raw is None:
				return None
			try:
				return float(raw)
			except ValueError:
				self.error("Enter a valid number.")

	def ask_int(self, prompt: str, default: int | None = None) -> int | None:
		while True:
			raw = self.ask_text(prompt, None if default is None else str(default))
			if raw is None:
				return None
			try:
				return int(raw)
			except ValueError:
				self.error("Enter a valid integer.")

	def error(self, text: str) -> None:
		print(f"Error: {text}")


class TkIO:
	def __init__(self, root, log_widget=None):
		self.root = root
		self.log_widget = log_widget

	def tell(self, text: str) -> None:
		if self.log_widget is not None:
			self.log_widget.configure(state="normal")
			self.log_widget.insert("end", text + "\n")
			self.log_widget.see("end")
			self.log_widget.configure(state="disabled")
		else:
			print(text)

	def ask_text(self, prompt: str, default: str | None = None) -> str | None:
		from tkinter import simpledialog

		value = simpledialog.askstring("Universal Calculator", prompt, parent=self.root)
		if value is None:
			return None
		value = value.strip()
		if not value and default is not None:
			return default
		return value if value else None

	def ask_float(self, prompt: str, default: float | None = None) -> float | None:
		while True:
			raw = self.ask_text(prompt, None if default is None else str(default))
			if raw is None:
				return None
			try:
				return float(raw)
			except ValueError:
				self.error("Enter a valid number.")

	def ask_int(self, prompt: str, default: int | None = None) -> int | None:
		while True:
			raw = self.ask_text(prompt, None if default is None else str(default))
			if raw is None:
				return None
			try:
				return int(raw)
			except ValueError:
				self.error("Enter a valid integer.")

	def error(self, text: str) -> None:
		from tkinter import messagebox

		if self.log_widget is not None:
			self.tell(f"Error: {text}")
		messagebox.showerror("Universal Calculator", text, parent=self.root)


def _prepare_expression(text: str) -> str:
	return text.replace("^", "**").strip()


def parse_symbol(name: str) -> sp.Symbol:
	cleaned = name.strip()
	if cleaned in SYMBOLS:
		return SYMBOLS[cleaned]
	return sp.symbols(cleaned)


def parse_expression(text: str) -> sp.Expr:
	return parse_expr(_prepare_expression(text), local_dict=SAFE_LOCAL_DICT, transformations=TRANSFORMATIONS)


def parse_equation(text: str) -> sp.Eq:
	if "=" in text:
		left_text, right_text = text.split("=", 1)
		return sp.Eq(parse_expression(left_text), parse_expression(right_text))
	expression = parse_expression(text)
	return sp.Eq(expression, 0)


def format_result(value: sp.Expr | float | int) -> str:
	if isinstance(value, (float, int)):
		return f"{value:.12g}" if isinstance(value, float) else str(value)
	simplified = sp.simplify(value)
	if simplified.is_Number:
		return f"{float(simplified):.12g}"
	return sp.sstr(simplified)


def evaluate_expression(text: str, substitutions: dict[str, float] | None = None) -> sp.Expr:
	expr = parse_expression(text)
	if substitutions:
		subs = {parse_symbol(name): value for name, value in substitutions.items()}
		expr = expr.subs(subs)
	return sp.simplify(expr)


def solve_equation_text(equation_text: str, target: str = "x") -> list[sp.Expr]:
	equation = parse_equation(equation_text)
	target_symbol = parse_symbol(target)
	solutions = sp.solve(equation, target_symbol)
	if isinstance(solutions, dict):
		return [solutions[target_symbol]]
	return list(solutions)


def differentiate_expression(expression_text: str, variable_name: str = "x", order: int = 1) -> sp.Expr:
	expression = parse_expression(expression_text)
	variable = parse_symbol(variable_name)
	return sp.diff(expression, variable, order)


def integrate_expression(expression_text: str, variable_name: str = "x") -> sp.Expr:
	expression = parse_expression(expression_text)
	variable = parse_symbol(variable_name)
	return sp.integrate(expression, variable)


def definite_integral(expression_text: str, variable_name: str, lower: float, upper: float) -> sp.Expr:
	expression = parse_expression(expression_text)
	variable = parse_symbol(variable_name)
	return sp.integrate(expression, (variable, lower, upper))


def limit_expression(expression_text: str, variable_name: str, approach: str, direction: str = "+") -> sp.Expr:
	expression = parse_expression(expression_text)
	variable = parse_symbol(variable_name)
	target = parse_expression(approach)
	return sp.limit(expression, variable, target, dir=direction)


def plot_expression(expression_text: str, variable_name: str = "x", start: float = -10.0, stop: float = 10.0) -> None:
	expression = parse_expression(expression_text)
	variable = parse_symbol(variable_name)
	function = sp.lambdify(variable, expression, modules=["numpy"])
	x_values = np.linspace(start, stop, 500)
	y_values = function(x_values)

	plt.figure(figsize=(8, 5))
	plt.axhline(0, color="black", linewidth=0.8)
	plt.axvline(0, color="black", linewidth=0.8)
	plt.plot(x_values, y_values, label=sp.sstr(expression))
	plt.xlabel(variable_name)
	plt.ylabel("y")
	plt.title(f"Graph of {sp.sstr(expression)}")
	plt.grid(True, alpha=0.3)
	plt.legend()
	plt.tight_layout()
	plt.show()


class AlgebraCalculator(BaseCalculator):
	title = "Algebra Calculator"

	def actions(self) -> list[Action]:
		return [
			Action("Evaluate expression", self.evaluate_expression_action),
			Action("Simplify expression", self.simplify_expression_action),
			Action("Factor expression", self.factor_expression_action),
			Action("Expand expression", self.expand_expression_action),
			Action("Solve equation", self.solve_equation_action),
			Action("Solve 2x2 system", self.solve_system_action),
		]

	def evaluate_expression_action(self, io: IOContext) -> None:
		expression_text = io.ask_text("Enter an expression to evaluate")
		if not expression_text:
			return
		result = evaluate_expression(expression_text)
		io.tell(f"Result: {format_result(result)}")

	def simplify_expression_action(self, io: IOContext) -> None:
		expression_text = io.ask_text("Enter an expression to simplify")
		if not expression_text:
			return
		result = sp.simplify(parse_expression(expression_text))
		io.tell(f"Simplified: {format_result(result)}")

	def factor_expression_action(self, io: IOContext) -> None:
		expression_text = io.ask_text("Enter an expression to factor")
		if not expression_text:
			return
		result = sp.factor(parse_expression(expression_text))
		io.tell(f"Factored: {format_result(result)}")

	def expand_expression_action(self, io: IOContext) -> None:
		expression_text = io.ask_text("Enter an expression to expand")
		if not expression_text:
			return
		result = sp.expand(parse_expression(expression_text))
		io.tell(f"Expanded: {format_result(result)}")

	def solve_equation_action(self, io: IOContext) -> None:
		equation_text = io.ask_text("Enter an equation, for example x^2 - 4 = 0")
		if not equation_text:
			return
		target = io.ask_text("Which variable should be solved for?", "x") or "x"
		solutions = solve_equation_text(equation_text, target)
		if not solutions:
			io.tell("No solution found.")
			return
		io.tell(f"Solutions for {target}: {', '.join(format_result(solution) for solution in solutions)}")

	def solve_system_action(self, io: IOContext) -> None:
		first = io.ask_text("Enter the first equation, for example 2x + y = 7")
		if not first:
			return
		second = io.ask_text("Enter the second equation, for example x - y = 1")
		if not second:
			return
		first_equation = parse_equation(first)
		second_equation = parse_equation(second)
		x_symbol = parse_symbol(io.ask_text("Solve for variable x name", "x") or "x")
		y_symbol = parse_symbol(io.ask_text("Solve for variable y name", "y") or "y")
		solutions = sp.solve((first_equation, second_equation), (x_symbol, y_symbol), dict=True)
		if not solutions:
			io.tell("No solution found.")
			return
		solution = solutions[0]
		io.tell(", ".join(f"{symbol} = {format_result(solution[symbol])}" for symbol in (x_symbol, y_symbol) if symbol in solution))


class CalculusCalculator(BaseCalculator):
	title = "Calculus Calculator"

	def actions(self) -> list[Action]:
		return [
			Action("Differentiate", self.differentiate_action),
			Action("Integrate", self.integrate_action),
			Action("Definite integral", self.definite_integral_action),
			Action("Limit", self.limit_action),
			Action("Tangent line", self.tangent_line_action),
			Action("Plot function", self.plot_action),
		]

	def differentiate_action(self, io: IOContext) -> None:
		expression_text = io.ask_text("Enter a function to differentiate, for example x^3 + 2x")
		if not expression_text:
			return
		variable = io.ask_text("Differentiate with respect to which variable?", "x") or "x"
		order = io.ask_int("Derivative order", 1) or 1
		result = differentiate_expression(expression_text, variable, order)
		io.tell(f"Derivative: {format_result(result)}")

	def integrate_action(self, io: IOContext) -> None:
		expression_text = io.ask_text("Enter a function to integrate")
		if not expression_text:
			return
		variable = io.ask_text("Integrate with respect to which variable?", "x") or "x"
		result = integrate_expression(expression_text, variable)
		io.tell(f"Integral: {format_result(result)} + C")

	def definite_integral_action(self, io: IOContext) -> None:
		expression_text = io.ask_text("Enter a function for the definite integral")
		if not expression_text:
			return
		variable = io.ask_text("Variable", "x") or "x"
		lower = io.ask_float("Lower bound")
		upper = io.ask_float("Upper bound")
		if lower is None or upper is None:
			return
		result = definite_integral(expression_text, variable, lower, upper)
		io.tell(f"Definite integral: {format_result(result)}")

	def limit_action(self, io: IOContext) -> None:
		expression_text = io.ask_text("Enter a function for the limit")
		if not expression_text:
			return
		variable = io.ask_text("Variable", "x") or "x"
		approach = io.ask_text("Approach value", "0") or "0"
		direction = io.ask_text("Direction (+, -, or both)", "+") or "+"
		result = limit_expression(expression_text, variable, approach, direction)
		io.tell(f"Limit: {format_result(result)}")

	def tangent_line_action(self, io: IOContext) -> None:
		expression_text = io.ask_text("Enter a function for the tangent line")
		if not expression_text:
			return
		variable_name = io.ask_text("Variable", "x") or "x"
		point = io.ask_float("Point of tangency")
		if point is None:
			return
		variable = parse_symbol(variable_name)
		expression = parse_expression(expression_text)
		derivative = sp.diff(expression, variable)
		slope = sp.simplify(derivative.subs(variable, point))
		y_value = sp.simplify(expression.subs(variable, point))
		tangent_line = sp.expand(slope * (variable - point) + y_value)
		io.tell(f"Tangent line: y = {format_result(tangent_line)}")

	def plot_action(self, io: IOContext) -> None:
		expression_text = io.ask_text("Enter a function to graph")
		if not expression_text:
			return
		variable = io.ask_text("Variable", "x") or "x"
		start = io.ask_float("Graph start value", -10.0) or -10.0
		stop = io.ask_float("Graph stop value", 10.0) or 10.0
		plot_expression(expression_text, variable, start, stop)
