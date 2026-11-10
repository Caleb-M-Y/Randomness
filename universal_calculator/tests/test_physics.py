import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from physics import PhysicsCalculator


class ScriptedIO:
	def __init__(self, texts, numbers=()):
		self.texts = iter(texts)
		self.numbers = iter(numbers)
		self.messages = []

	def ask_text(self, prompt, default=None):
		return next(self.texts, default)

	def ask_float(self, prompt, default=None):
		return next(self.numbers, default)

	def ask_int(self, prompt, default=None):
		return default

	def tell(self, text):
		self.messages.append(text)

	def error(self, text):
		raise AssertionError(text)


class PhysicsCalculatorTests(unittest.TestCase):
	def setUp(self):
		self.physics = PhysicsCalculator()

	def test_catalog_is_textbook_ordered_and_contains_kinematics(self):
		titles = [chapter.title for chapter in self.physics.chapters]
		self.assertEqual(titles[:3], [
			"Measurement, units, and uncertainty",
			"Vectors",
			"Kinematics: motion in one and two dimensions",
		])
		self.assertGreaterEqual(sum(len(chapter.formulas) for chapter in self.physics.chapters), 45)

	def test_formula_can_calculate_a_rearranged_variable(self):
		# Newton's second law: F=20 N and m=4 kg, solve for a.
		io = ScriptedIO(["2", "a"], [20, 4])
		forces = self.physics.chapters[3]
		forces._use_formula(io, forces.formulas[0])
		self.assertEqual(io.messages[-1], "a = 5")

	def test_custom_equation_can_be_rearranged(self):
		io = ScriptedIO(["F = m*a", "a"])
		self.physics.custom_equation(io)
		self.assertEqual(io.messages[-1], "a = F/m")


if __name__ == "__main__":
	unittest.main()
