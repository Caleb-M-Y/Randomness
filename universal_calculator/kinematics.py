from __future__ import annotations

import sympy as sp

from equations import Action, BaseCalculator, IOContext, format_result, parse_symbol


class KinematicsCalculator(BaseCalculator):
	title = "Kinematics Calculator"

	def actions(self) -> list[Action]:
		return [
			Action("v = v0 + at", self.velocity_equation),
			Action("x = x0 + v0t + 1/2 at^2", self.displacement_equation),
			Action("v^2 = v0^2 + 2a(x - x0)", self.timeless_equation),
			Action("x = x0 + 1/2(v0 + v)t", self.average_displacement_equation),
		]

	def _solve_single(self, io: IOContext, equation: sp.Eq, target_name: str, inputs: list[str]) -> None:
		target = parse_symbol(target_name)
		values: dict[sp.Symbol, float] = {}
		for name in inputs:
			symbol = parse_symbol(name)
			value = io.ask_float(f"Enter {name}")
			if value is None:
				return
			values[symbol] = value
		solution = sp.solve(equation.subs(values), target)
		if not solution:
			io.tell("No solution found.")
			return
		io.tell(f"{target_name} = {', '.join(format_result(item) for item in solution)}")

	def velocity_equation(self, io: IOContext) -> None:
		target = io.ask_text("Solve for which variable? (v, v0, a, t)", "v") or "v"
		equation = sp.Eq(parse_symbol("v"), parse_symbol("v0") + parse_symbol("a") * parse_symbol("t"))
		if target == "v":
			self._solve_single(io, equation, "v", ["v0", "a", "t"])
		elif target == "v0":
			self._solve_single(io, equation, "v0", ["v", "a", "t"])
		elif target == "a":
			self._solve_single(io, equation, "a", ["v", "v0", "t"])
		elif target == "t":
			self._solve_single(io, equation, "t", ["v", "v0", "a"])
		else:
			io.error("Choose v, v0, a, or t.")

	def displacement_equation(self, io: IOContext) -> None:
		x = parse_symbol("x")
		x0 = parse_symbol("x0")
		v0 = parse_symbol("v0")
		a = parse_symbol("a")
		equation = sp.Eq(x, x0 + v0 * parse_symbol("t") + sp.Rational(1, 2) * a * parse_symbol("t") ** 2)
		target = io.ask_text("Solve for which variable? (x, x0, v0, a, t)", "x") or "x"
		if target == "x":
			self._solve_single(io, equation, "x", ["x0", "v0", "a", "t"])
		elif target == "x0":
			self._solve_single(io, equation, "x0", ["x", "v0", "a", "t"])
		elif target == "v0":
			self._solve_single(io, equation, "v0", ["x", "x0", "a", "t"])
		elif target == "a":
			self._solve_single(io, equation, "a", ["x", "x0", "v0", "t"])
		elif target == "t":
			self._solve_single(io, equation, "t", ["x", "x0", "v0", "a"])
		else:
			io.error("Choose x, x0, v0, a, or t.")

	def timeless_equation(self, io: IOContext) -> None:
		x = parse_symbol("x")
		x0 = parse_symbol("x0")
		v = parse_symbol("v")
		v0 = parse_symbol("v0")
		a = parse_symbol("a")
		equation = sp.Eq(v**2, v0**2 + 2 * a * (x - x0))
		target = io.ask_text("Solve for which variable? (v, v0, a, x, x0)", "v") or "v"
		if target == "v":
			self._solve_single(io, equation, "v", ["v0", "a", "x", "x0"])
		elif target == "v0":
			self._solve_single(io, equation, "v0", ["v", "a", "x", "x0"])
		elif target == "a":
			self._solve_single(io, equation, "a", ["v", "v0", "x", "x0"])
		elif target == "x":
			self._solve_single(io, equation, "x", ["v", "v0", "a", "x0"])
		elif target == "x0":
			self._solve_single(io, equation, "x0", ["v", "v0", "a", "x"])
		else:
			io.error("Choose v, v0, a, x, or x0.")

	def average_displacement_equation(self, io: IOContext) -> None:
		x = parse_symbol("x")
		x0 = parse_symbol("x0")
		v = parse_symbol("v")
		v0 = parse_symbol("v0")
		t = parse_symbol("t")
		equation = sp.Eq(x, x0 + sp.Rational(1, 2) * (v0 + v) * t)
		target = io.ask_text("Solve for which variable? (x, x0, v0, v, t)", "x") or "x"
		if target == "x":
			self._solve_single(io, equation, "x", ["x0", "v0", "v", "t"])
		elif target == "x0":
			self._solve_single(io, equation, "x0", ["x", "v0", "v", "t"])
		elif target == "v0":
			self._solve_single(io, equation, "v0", ["x", "x0", "v", "t"])
		elif target == "v":
			self._solve_single(io, equation, "v", ["x", "x0", "v0", "t"])
		elif target == "t":
			self._solve_single(io, equation, "t", ["x", "x0", "v0", "v"])
		else:
			io.error("Choose x, x0, v0, v, or t.")


class StaticsCalculator(BaseCalculator):
	title = "Statics Calculator"

	def actions(self) -> list[Action]:
		return [
			Action("Resultant force from x/y components", self.resultant_force_action),
			Action("Moment / torque", self.moment_action),
			Action("Friction force", self.friction_action),
			Action("Equilibrium check", self.equilibrium_action),
		]

	def resultant_force_action(self, io: IOContext) -> None:
		fx = io.ask_float("Force component in x")
		fy = io.ask_float("Force component in y")
		if fx is None or fy is None:
			return
		magnitude = sp.sqrt(fx**2 + fy**2)
		angle = sp.atan2(fy, fx) * 180 / sp.pi
		io.tell(f"Resultant force: {format_result(magnitude)}")
		io.tell(f"Direction from +x axis: {format_result(angle)} degrees")

	def moment_action(self, io: IOContext) -> None:
		force = io.ask_float("Force")
		if force is None:
			return
		distance = io.ask_float("Perpendicular distance")
		if distance is None:
			return
		io.tell(f"Moment: {format_result(force * distance)}")

	def friction_action(self, io: IOContext) -> None:
		coefficient = io.ask_float("Coefficient of friction")
		normal_force = io.ask_float("Normal force")
		if coefficient is None or normal_force is None:
			return
		io.tell(f"Friction force: {format_result(coefficient * normal_force)}")

	def equilibrium_action(self, io: IOContext) -> None:
		sum_fx = io.ask_float("Sum of forces in x")
		sum_fy = io.ask_float("Sum of forces in y")
		if sum_fx is None or sum_fy is None:
			return
		if abs(sum_fx) < 1e-9 and abs(sum_fy) < 1e-9:
			io.tell("The system is in translational equilibrium.")
		else:
			io.tell(f"Not in equilibrium. Net force magnitude: {format_result(sp.sqrt(sum_fx**2 + sum_fy**2))}")


class DynamicsCalculator(BaseCalculator):
	title = "Dynamics Calculator"

	def actions(self) -> list[Action]:
		return [
			Action("Force and acceleration", self.force_action),
			Action("Momentum", self.momentum_action),
			Action("Impulse", self.impulse_action),
			Action("Kinetic energy", self.kinetic_energy_action),
			Action("Work", self.work_action),
			Action("Power", self.power_action),
		]

	def force_action(self, io: IOContext) -> None:
		mass = io.ask_float("Mass")
		acceleration = io.ask_float("Acceleration")
		if mass is None or acceleration is None:
			return
		io.tell(f"Force: {format_result(mass * acceleration)}")

	def momentum_action(self, io: IOContext) -> None:
		mass = io.ask_float("Mass")
		velocity = io.ask_float("Velocity")
		if mass is None or velocity is None:
			return
		io.tell(f"Momentum: {format_result(mass * velocity)}")

	def impulse_action(self, io: IOContext) -> None:
		force = io.ask_float("Force")
		time = io.ask_float("Time")
		if force is None or time is None:
			return
		io.tell(f"Impulse: {format_result(force * time)}")

	def kinetic_energy_action(self, io: IOContext) -> None:
		mass = io.ask_float("Mass")
		velocity = io.ask_float("Velocity")
		if mass is None or velocity is None:
			return
		io.tell(f"Kinetic energy: {format_result(0.5 * mass * velocity**2)}")

	def work_action(self, io: IOContext) -> None:
		force = io.ask_float("Force")
		distance = io.ask_float("Distance")
		if force is None or distance is None:
			return
		io.tell(f"Work: {format_result(force * distance)}")

	def power_action(self, io: IOContext) -> None:
		work = io.ask_float("Work")
		time = io.ask_float("Time")
		if work is None or time is None:
			return
		io.tell(f"Power: {format_result(work / time)}")
