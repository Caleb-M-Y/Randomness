"""Textbook-ordered physics reference and solver.

Every formula is intentionally represented as a symbolic equation.  This makes
the calculator useful as a reference first, while still allowing a user to
substitute values or rearrange the equation for any of its variables.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import sympy as sp

from equations import Action, BaseCalculator, IOContext, format_result, parse_equation, parse_symbol


@dataclass(frozen=True)
class Formula:
	name: str
	equation: sp.Eq
	variables: tuple[str, ...]
	units: str
	description: str = ""

	def display(self) -> str:
		return sp.sstr(self.equation)


def symbols(*names: str) -> tuple[sp.Symbol, ...]:
	return sp.symbols(" ".join(names))


class FormulaCalculator(BaseCalculator):
	"""A reusable calculator chapter whose formulae can be viewed or solved."""

	def __init__(self, title: str, formulas: Iterable[Formula]) -> None:
		self.title = title
		self.formulas = tuple(formulas)

	def actions(self) -> list[Action]:
		return [
			Action(formula.name, lambda io, current=formula: self._use_formula(io, current), formula.description)
			for formula in self.formulas
		]

	def _use_formula(self, io: IOContext, formula: Formula) -> None:
		io.tell(f"\n{formula.name}")
		io.tell(f"Equation: {formula.display()}")
		if formula.description:
			io.tell(formula.description)
		io.tell(f"Variables / SI units: {formula.units}")
		mode = io.ask_text("Choose 1 to view, 2 to calculate or rearrange", "1")
		if mode in (None, "1", "view", "show"):
			return
		if mode not in ("2", "solve", "calculate"):
			io.error("Choose 1 or 2.")
			return

		target_name = io.ask_text(f"Solve for ({', '.join(formula.variables)})", formula.variables[0])
		if not target_name:
			return
		target_name = target_name.strip()
		if target_name not in formula.variables:
			io.error(f"Choose one of: {', '.join(formula.variables)}.")
			return
		target = sp.Symbol(target_name)
		values: dict[sp.Symbol, float] = {}
		for name in formula.variables:
			if name == target_name:
				continue
			value = io.ask_float(f"Enter {name}")
			if value is None:
				return
			values[sp.Symbol(name)] = value

		try:
			solutions = sp.solve(formula.equation.subs(values), target)
		except (ValueError, TypeError, NotImplementedError) as error:
			io.error(f"Could not solve this input: {error}")
			return
		if not solutions:
			io.tell("No solution found for those values.")
			return
		io.tell(f"{target_name} = {', '.join(format_result(solution) for solution in solutions)}")


class PhysicsCalculator(BaseCalculator):
	"""Physics topics in the usual introductory-textbook progression."""
	title = "Physics - textbook sequence"

	def __init__(self) -> None:
		self.chapters: tuple[FormulaCalculator, ...] = (
			_measurement_chapter(),
			_vectors_chapter(),
			_kinematics_chapter(),
			_forces_chapter(),
			_energy_chapter(),
			_momentum_chapter(),
			_rotation_chapter(),
			_gravitation_fluids_chapter(),
			_oscillations_waves_chapter(),
			_thermal_chapter(),
			_electricity_chapter(),
			_magnetism_chapter(),
			_optics_modern_chapter(),
		)

	def actions(self) -> list[Action]:
		actions = [
			Action("Physics equation index", self.show_index),
			Action("Custom physics equation: show or rearrange", self.custom_equation),
		]
		for number, chapter in enumerate(self.chapters, start=1):
			actions.append(Action(f"{number}. {chapter.title}", lambda io, current=chapter: current.run_cli(io)))
		return actions

	def show_index(self, io: IOContext) -> None:
		io.tell("\nPhysics equation index (select a chapter to view, calculate, or rearrange):")
		for number, chapter in enumerate(self.chapters, start=1):
			io.tell(f"\n{number}. {chapter.title}")
			for formula in chapter.formulas:
				io.tell(f"  - {formula.name}: {formula.display()}")

	def custom_equation(self, io: IOContext) -> None:
		"""Use the symbolic engine for a relation not yet in the reference."""
		text = io.ask_text("Enter an equation, for example F = m*a")
		if not text:
			return
		try:
			equation = parse_equation(text)
		except (SyntaxError, TypeError, ValueError) as error:
			io.error(f"Could not read that equation: {error}")
			return
		io.tell(f"Equation: {sp.sstr(equation)}")
		target_name = io.ask_text("Solve for which variable? Leave blank to only view it")
		if not target_name:
			return
		try:
			solutions = sp.solve(equation, parse_symbol(target_name))
		except (ValueError, TypeError, NotImplementedError) as error:
			io.error(f"Could not rearrange this equation: {error}")
			return
		if not solutions:
			io.tell("No solution found.")
			return
		io.tell(f"{target_name} = {', '.join(format_result(solution) for solution in solutions)}")


def _measurement_chapter() -> FormulaCalculator:
	L, dL, percent = symbols("L dL percent")
	return FormulaCalculator("Measurement, units, and uncertainty", [
		Formula("Percent uncertainty", sp.Eq(percent, 100 * dL / L), ("percent", "dL", "L"), "percent (%), dL and L (same unit)"),
	])


def _vectors_chapter() -> FormulaCalculator:
	Ax, Ay, A, theta = symbols("Ax Ay A theta")
	return FormulaCalculator("Vectors", [
		Formula("Vector magnitude", sp.Eq(A, sp.sqrt(Ax**2 + Ay**2)), ("A", "Ax", "Ay"), "A, Ax, Ay (same unit)"),
		Formula("x component", sp.Eq(Ax, A * sp.cos(theta)), ("Ax", "A", "theta"), "Ax, A (same unit); theta (radians)"),
		Formula("y component", sp.Eq(Ay, A * sp.sin(theta)), ("Ay", "A", "theta"), "Ay, A (same unit); theta (radians)"),
	])


def _kinematics_chapter() -> FormulaCalculator:
	x, x0, v, v0, a, t, vx, vy, g, R, h, theta = symbols("x x0 v v0 a t vx vy g R h theta")
	return FormulaCalculator("Kinematics: motion in one and two dimensions", [
		Formula("Average velocity", sp.Eq(v, (x - x0) / t), ("v", "x", "x0", "t"), "v (m/s); x, x0 (m); t (s)"),
		Formula("Constant-acceleration velocity", sp.Eq(v, v0 + a * t), ("v", "v0", "a", "t"), "v, v0 (m/s); a (m/s^2); t (s)"),
		Formula("Constant-acceleration position", sp.Eq(x, x0 + v0 * t + sp.Rational(1, 2) * a * t**2), ("x", "x0", "v0", "a", "t"), "x, x0 (m); v0 (m/s); a (m/s^2); t (s)"),
		Formula("Velocity without time", sp.Eq(v**2, v0**2 + 2 * a * (x - x0)), ("v", "v0", "a", "x", "x0"), "v, v0 (m/s); a (m/s^2); x, x0 (m)"),
		Formula("Position from average velocity", sp.Eq(x, x0 + (v0 + v) * t / 2), ("x", "x0", "v0", "v", "t"), "x, x0 (m); v0, v (m/s); t (s)"),
		Formula("Projectile horizontal position", sp.Eq(x, vx * t), ("x", "vx", "t"), "x (m); vx (m/s); t (s)"),
		Formula("Projectile vertical position", sp.Eq(h, vy * t - g * t**2 / 2), ("h", "vy", "g", "t"), "h (m); vy (m/s); g (m/s^2); t (s)"),
		Formula("Projectile range (level ground)", sp.Eq(R, v0**2 * sp.sin(2 * theta) / g), ("R", "v0", "theta", "g"), "R (m); v0 (m/s); theta (radians); g (m/s^2)"),
	])


def _forces_chapter() -> FormulaCalculator:
	F, m, a, weight, g, friction, mu, N, torque, r, theta = symbols("F m a weight g friction mu N torque r theta")
	return FormulaCalculator("Forces and Newton's laws", [
		Formula("Newton's second law", sp.Eq(F, m * a), ("F", "m", "a"), "F (N); m (kg); a (m/s^2)"),
		Formula("Weight near Earth", sp.Eq(weight, m * g), ("weight", "m", "g"), "weight (N); m (kg); g (m/s^2)"),
		Formula("Static / kinetic friction magnitude", sp.Eq(friction, mu * N), ("friction", "mu", "N"), "friction, N (N); mu (unitless)"),
		Formula("Torque magnitude", sp.Eq(torque, r * F * sp.sin(theta)), ("torque", "r", "F", "theta"), "torque (N*m); r (m); F (N); theta (radians)"),
	])


def _energy_chapter() -> FormulaCalculator:
	K, m, v, U, g, h, W, F, d, theta, P, t = symbols("K m v U g h W F d theta P t")
	return FormulaCalculator("Work, energy, and power", [
		Formula("Kinetic energy", sp.Eq(K, m * v**2 / 2), ("K", "m", "v"), "K (J); m (kg); v (m/s)"),
		Formula("Gravitational potential energy", sp.Eq(U, m * g * h), ("U", "m", "g", "h"), "U (J); m (kg); g (m/s^2); h (m)"),
		Formula("Work by a constant force", sp.Eq(W, F * d * sp.cos(theta)), ("W", "F", "d", "theta"), "W (J); F (N); d (m); theta (radians)"),
		Formula("Average power", sp.Eq(P, W / t), ("P", "W", "t"), "P (W); W (J); t (s)"),
	])


def _momentum_chapter() -> FormulaCalculator:
	p, m, v, J, F, t, m1, v1, m2, v2 = symbols("p m v J F t m1 v1 m2 v2")
	return FormulaCalculator("Linear momentum and collisions", [
		Formula("Linear momentum", sp.Eq(p, m * v), ("p", "m", "v"), "p (kg*m/s); m (kg); v (m/s)"),
		Formula("Impulse", sp.Eq(J, F * t), ("J", "F", "t"), "J (N*s); F (N); t (s)"),
		Formula("One-dimensional momentum conservation", sp.Eq(m1 * v1 + m2 * v2, p), ("p", "m1", "v1", "m2", "v2"), "p (kg*m/s); m1, m2 (kg); v1, v2 (m/s)"),
	])


def _rotation_chapter() -> FormulaCalculator:
	omega, omega0, theta, alpha, t, r, v, ac, I, torque, L = symbols("omega omega0 theta alpha t r v ac I torque L")
	return FormulaCalculator("Rotational motion", [
		Formula("Angular velocity", sp.Eq(omega, theta / t), ("omega", "theta", "t"), "omega (rad/s); theta (rad); t (s)"),
		Formula("Constant-angular-acceleration velocity", sp.Eq(omega, omega0 + alpha * t), ("omega", "omega0", "alpha", "t"), "omega, omega0 (rad/s); alpha (rad/s^2); t (s)"),
		Formula("Tangential speed", sp.Eq(v, r * omega), ("v", "r", "omega"), "v (m/s); r (m); omega (rad/s)"),
		Formula("Centripetal acceleration", sp.Eq(ac, v**2 / r), ("ac", "v", "r"), "ac (m/s^2); v (m/s); r (m)"),
		Formula("Rotational Newton's law", sp.Eq(torque, I * alpha), ("torque", "I", "alpha"), "torque (N*m); I (kg*m^2); alpha (rad/s^2)"),
		Formula("Angular momentum", sp.Eq(L, I * omega), ("L", "I", "omega"), "L (kg*m^2/s); I (kg*m^2); omega (rad/s)"),
	])


def _gravitation_fluids_chapter() -> FormulaCalculator:
	F, G, m1, m2, r, P, rho, g, h, Fb, V = symbols("F G m1 m2 r P rho g h Fb V")
	return FormulaCalculator("Gravitation and fluids", [
		Formula("Universal gravitation", sp.Eq(F, G * m1 * m2 / r**2), ("F", "G", "m1", "m2", "r"), "F (N); G (N*m^2/kg^2); m1, m2 (kg); r (m)"),
		Formula("Hydrostatic pressure", sp.Eq(P, rho * g * h), ("P", "rho", "g", "h"), "P (Pa); rho (kg/m^3); g (m/s^2); h (m)"),
		Formula("Buoyant force", sp.Eq(Fb, rho * V * g), ("Fb", "rho", "V", "g"), "Fb (N); rho (kg/m^3); V (m^3); g (m/s^2)"),
	])


def _oscillations_waves_chapter() -> FormulaCalculator:
	T, f, omega, m, k, v, wavelength = symbols("T f omega m k v wavelength")
	return FormulaCalculator("Oscillations and waves", [
		Formula("Period and frequency", sp.Eq(T, 1 / f), ("T", "f"), "T (s); f (Hz)"),
		Formula("Angular frequency", sp.Eq(omega, 2 * sp.pi * f), ("omega", "f"), "omega (rad/s); f (Hz)"),
		Formula("Mass-spring period", sp.Eq(T, 2 * sp.pi * sp.sqrt(m / k)), ("T", "m", "k"), "T (s); m (kg); k (N/m)"),
		Formula("Wave speed", sp.Eq(v, f * wavelength), ("v", "f", "wavelength"), "v (m/s); f (Hz); wavelength (m)"),
	])


def _thermal_chapter() -> FormulaCalculator:
	Q, m, c, dT, P, V, n, R, T, W, dU = symbols("Q m c dT P V n R T W dU")
	return FormulaCalculator("Thermal physics and thermodynamics", [
		Formula("Heat transfer", sp.Eq(Q, m * c * dT), ("Q", "m", "c", "dT"), "Q (J); m (kg); c (J/(kg*K)); dT (K)"),
		Formula("Ideal gas law", sp.Eq(P * V, n * R * T), ("P", "V", "n", "R", "T"), "P (Pa); V (m^3); n (mol); R (J/(mol*K)); T (K)"),
		Formula("First law of thermodynamics", sp.Eq(dU, Q - W), ("dU", "Q", "W"), "dU (J change in internal energy); Q, W (J)"),
	])


def _electricity_chapter() -> FormulaCalculator:
	F, k, q1, q2, r, Efield, q, V, U, I, R, P = symbols("F k q1 q2 r Efield q V U I R P")
	return FormulaCalculator("Electrostatics and electric circuits", [
		Formula("Coulomb's law", sp.Eq(F, k * q1 * q2 / r**2), ("F", "k", "q1", "q2", "r"), "F (N); k (N*m^2/C^2); q1, q2 (C); r (m)"),
		Formula("Electric field", sp.Eq(Efield, F / q), ("Efield", "F", "q"), "Efield (N/C); F (N); q (C)"),
		Formula("Electric potential energy", sp.Eq(U, q * V), ("U", "q", "V"), "U (J); q (C); V (V)"),
		Formula("Ohm's law", sp.Eq(V, I * R), ("V", "I", "R"), "V (V); I (A); R (ohm)"),
		Formula("Electric power", sp.Eq(P, V * I), ("P", "V", "I"), "P (W); V (V); I (A)"),
	])


def _magnetism_chapter() -> FormulaCalculator:
	F, q, v, B, theta, r, m = symbols("F q v B theta r m")
	return FormulaCalculator("Magnetism and induction", [
		Formula("Magnetic force on a charge", sp.Eq(F, q * v * B * sp.sin(theta)), ("F", "q", "v", "B", "theta"), "F (N); q (C); v (m/s); B (T); theta (radians)"),
		Formula("Charged-particle orbit radius", sp.Eq(r, m * v / (q * B)), ("r", "m", "v", "q", "B"), "r (m); m (kg); v (m/s); q (C); B (T)"),
	])


def _optics_modern_chapter() -> FormulaCalculator:
	f, do, di, c, wavelength, nu, E, h = symbols("f do di c wavelength nu E h")
	return FormulaCalculator("Optics and modern physics", [
		Formula("Thin lens / mirror equation", sp.Eq(1 / f, 1 / do + 1 / di), ("f", "do", "di"), "f, do, di (m)"),
		Formula("Wave speed of light", sp.Eq(c, wavelength * nu), ("c", "wavelength", "nu"), "c (m/s); wavelength (m); nu (Hz)"),
		Formula("Photon energy", sp.Eq(E, h * nu), ("E", "h", "nu"), "E (J); h (J*s); nu (Hz)"),
	])
