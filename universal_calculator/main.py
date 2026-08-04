from __future__ import annotations

import argparse
import tkinter as tk
from tkinter import ttk

from area_volume import AreaVolumeCalculator
from equations import AlgebraCalculator, CalculusCalculator, ConsoleIO, TkIO
from kinematics import DynamicsCalculator, KinematicsCalculator, StaticsCalculator


class UniversalCalculatorApp:
	def __init__(self) -> None:
		self.calculators = [
			AreaVolumeCalculator(),
			KinematicsCalculator(),
			StaticsCalculator(),
			DynamicsCalculator(),
			AlgebraCalculator(),
			CalculusCalculator(),
		]

	def run_cli(self) -> None:
		io = ConsoleIO()
		while True:
			io.tell("\nUniversal Calculator")
			io.tell("1. Area and volume")
			io.tell("2. Kinematics")
			io.tell("3. Statics")
			io.tell("4. Dynamics")
			io.tell("5. Algebra")
			io.tell("6. Calculus")
			io.tell("0. Quit")

			selection = io.ask_text("Choose a topic")
			if selection is None:
				return

			if selection == "0":
				return
			if selection == "1":
				self.calculators[0].run_cli(io)
			elif selection == "2":
				self.calculators[1].run_cli(io)
			elif selection == "3":
				self.calculators[2].run_cli(io)
			elif selection == "4":
				self.calculators[3].run_cli(io)
			elif selection == "5":
				self.calculators[4].run_cli(io)
			elif selection == "6":
				self.calculators[5].run_cli(io)
			else:
				io.error("Choose a valid topic.")

	def run_gui(self) -> None:
		root = tk.Tk()
		root.title("Universal Calculator")
		root.geometry("980x640")
		root.minsize(900, 600)

		style = ttk.Style(root)
		try:
			style.theme_use("clam")
		except tk.TclError:
			pass

		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1)

		outer = ttk.Frame(root, padding=18)
		outer.grid(sticky="nsew")
		outer.columnconfigure(0, weight=1)
		outer.rowconfigure(1, weight=1)

		header = ttk.Frame(outer)
		header.grid(row=0, column=0, sticky="ew")
		title = ttk.Label(header, text="Universal Calculator", font=("Segoe UI", 22, "bold"))
		title.grid(row=0, column=0, sticky="w")
		subtitle = ttk.Label(
			header,
			text="Menu-driven calculators with numeric input, symbolic algebra/calculus, and graphing.",
		)
		subtitle.grid(row=1, column=0, sticky="w", pady=(4, 18))

		grid = ttk.Frame(outer)
		grid.grid(row=1, column=0, sticky="nsew")
		for index in range(3):
			grid.columnconfigure(index, weight=1)
		for index in range(2):
			grid.rowconfigure(index, weight=1)

		topic_buttons = [
			("Area and Volume", self.calculators[0]),
			("Kinematics", self.calculators[1]),
			("Statics", self.calculators[2]),
			("Dynamics", self.calculators[3]),
			("Algebra", self.calculators[4]),
			("Calculus", self.calculators[5]),
		]

		for index, (label, calculator) in enumerate(topic_buttons):
			row = index // 3
			column = index % 3
			card = ttk.Frame(grid, padding=16, relief="ridge")
			card.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
			card.columnconfigure(0, weight=1)
			ttk.Label(card, text=label, font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
			ttk.Label(card, text=f"Open the {label.lower()} menu.").grid(row=1, column=0, sticky="w", pady=(6, 12))
			ttk.Button(card, text="Open", command=lambda calc=calculator: self._open_calculator_window(root, calc)).grid(
				row=2, column=0, sticky="ew"
			)

		footer = ttk.Frame(outer)
		footer.grid(row=2, column=0, sticky="ew", pady=(14, 0))
		ttk.Button(footer, text="Quit", command=root.destroy).pack(side="right")

		root.mainloop()

	def _open_calculator_window(self, root: tk.Tk, calculator) -> None:
		window = tk.Toplevel(root)
		window.title(calculator.title)
		window.geometry("760x520")
		window.columnconfigure(0, weight=1)
		window.rowconfigure(1, weight=1)

		container = ttk.Frame(window, padding=14)
		container.grid(sticky="nsew")
		container.columnconfigure(0, weight=1)
		container.rowconfigure(1, weight=1)

		ttk.Label(container, text=calculator.title, font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")

		controls = ttk.Frame(container)
		controls.grid(row=1, column=0, sticky="ew", pady=(12, 10))
		controls.columnconfigure(1, weight=1)

		ttk.Label(controls, text="Action").grid(row=0, column=0, sticky="w")
		action_values = [action.label for action in calculator.actions()]
		selected_action = tk.StringVar(value=action_values[0] if action_values else "")
		dropdown = ttk.Combobox(controls, textvariable=selected_action, values=action_values, state="readonly")
		dropdown.grid(row=0, column=1, sticky="ew", padx=(10, 10))

		log = tk.Text(container, wrap="word", height=18, state="disabled")
		log.grid(row=2, column=0, sticky="nsew")

		tk_io = TkIO(window, log)

		def run_action() -> None:
			label = selected_action.get()
			for action in calculator.actions():
				if action.label == label:
					tk_io.tell(f"Running: {label}")
					action.handler(tk_io)
					return
			tk_io.error("Choose an action first.")

		ttk.Button(controls, text="Run", command=run_action).grid(row=0, column=2, sticky="e")


def main() -> None:
	parser = argparse.ArgumentParser(description="Universal calculator for math and physics topics.")
	parser.add_argument("--gui", action="store_true", help="Launch the GUI instead of the CLI.")
	args = parser.parse_args()

	app = UniversalCalculatorApp()
	if args.gui:
		app.run_gui()
	else:
		app.run_cli()


if __name__ == "__main__":
	main()
