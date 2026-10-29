from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from music_theory import TONICS, chord_voicing, diatonic_chords, fretboard_notes, scale_notes


BACKGROUND = "#f4f1e8"
INK = "#263238"
ACCENT = "#b65335"
SCALE_COLOR = "#e6b94f"
FRETBOARD_COLOR = "#d5a96c"


def fret_center_x(fret: int, left: float, fret_width: float) -> float:
	return left if fret == 0 else left + (fret - 0.5) * fret_width


class MusicKeyFinder:
	def __init__(self) -> None:
		self.root = tk.Tk()
		self.root.title("Guitar Key Finder")
		self.root.geometry("1180x900")
		self.root.minsize(800, 650)
		self.root.configure(background=BACKGROUND)

		style = ttk.Style(self.root)
		style.theme_use("clam")
		style.configure("TFrame", background=BACKGROUND)
		style.configure("TLabel", background=BACKGROUND, foreground=INK)
		style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
		style.configure("Section.TLabel", font=("Segoe UI", 15, "bold"))

		self.tonic = tk.StringVar(value="E")
		self.mode = tk.StringVar(value="Major")
		self._build_layout()
		self.update_view()

	def _build_layout(self) -> None:
		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)
		container = ttk.Frame(self.root, padding=18)
		container.grid(row=0, column=0, sticky="nsew")
		container.columnconfigure(0, weight=1)
		container.rowconfigure(2, weight=1)

		header = ttk.Frame(container)
		header.grid(row=0, column=0, sticky="ew")
		ttk.Label(header, text="Guitar Key Finder", style="Title.TLabel").pack(anchor="w")
		ttk.Label(
			header,
			text="Explore the notes, diatonic chords, and fretboard positions in any key.",
		).pack(anchor="w", pady=(3, 14))

		controls = ttk.Frame(container)
		controls.grid(row=1, column=0, sticky="ew", pady=(0, 14))
		ttk.Label(controls, text="Key").pack(side="left")
		key_picker = ttk.Combobox(
			controls, textvariable=self.tonic, values=TONICS, state="readonly", width=8
		)
		key_picker.pack(side="left", padx=(8, 18))
		key_picker.bind("<<ComboboxSelected>>", lambda _event: self.update_view())
		ttk.Label(controls, text="Scale").pack(side="left")
		mode_picker = ttk.Combobox(
			controls, textvariable=self.mode, values=("Major", "Natural minor"),
			state="readonly", width=16,
		)
		mode_picker.pack(side="left", padx=(8, 18))
		mode_picker.bind("<<ComboboxSelected>>", lambda _event: self.update_view())

		self.content = tk.Canvas(container, background=BACKGROUND, highlightthickness=0)
		scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.content.yview)
		self.content.configure(yscrollcommand=scrollbar.set)
		self.content.grid(row=2, column=0, sticky="nsew")
		scrollbar.grid(row=2, column=1, sticky="ns")
		self.body = ttk.Frame(self.content)
		self.body_window = self.content.create_window((0, 0), window=self.body, anchor="nw")
		self.body.bind(
			"<Configure>",
			lambda _event: self.content.configure(scrollregion=self.content.bbox("all")),
		)
		self.content.bind("<Configure>", self._resize_body)
		self.content.bind_all("<MouseWheel>", self._scroll)

	def _resize_body(self, event: tk.Event) -> None:
		self.content.itemconfigure(self.body_window, width=event.width)

	def _scroll(self, event: tk.Event) -> None:
		self.content.yview_scroll(int(-event.delta / 120), "units")

	def update_view(self) -> None:
		for child in self.body.winfo_children():
			child.destroy()

		notes = scale_notes(self.tonic.get(), self.mode.get())
		chords = diatonic_chords(notes, self.mode.get())
		ttk.Label(self.body, text=f"{self.tonic.get()} {self.mode.get()}", style="Section.TLabel").pack(anchor="w")
		ttk.Label(self.body, text="Scale notes:  " + "  ·  ".join(notes), font=("Segoe UI", 13)).pack(
			anchor="w", pady=(5, 16)
		)

		ttk.Label(self.body, text="Diatonic triads", style="Section.TLabel").pack(anchor="w")
		chord_row = ttk.Frame(self.body)
		chord_row.pack(fill="x", pady=(8, 18))
		for index, chord in enumerate(chords):
			card = ttk.Frame(chord_row, padding=8, relief="ridge")
			card.grid(row=index // 4, column=index % 4, sticky="nsew", padx=(0, 8), pady=(0, 8))
			chord_row.columnconfigure(index % 4, weight=1)
			ttk.Label(card, text=f"{chord['degree']}  {chord['name']}", font=("Segoe UI", 10, "bold")).pack()
			ttk.Label(card, text=" · ".join(chord["notes"])).pack()
			self._draw_chord(card, chord["notes"])

		ttk.Label(self.body, text="Scale notes on the guitar", style="Section.TLabel").pack(anchor="w")
		ttk.Label(
			self.body,
			text="Standard tuning · open strings through fret 12 · root notes are red",
		).pack(anchor="w", pady=(3, 8))
		self._draw_fretboard(self.body, notes)

	def _draw_fretboard(self, parent: ttk.Frame, scale: list[str]) -> None:
		notes_by_string = fretboard_notes(self.tonic.get(), self.mode.get(), 12)
		canvas = tk.Canvas(parent, width=1080, height=330, background=BACKGROUND, highlightthickness=0)
		canvas.pack(anchor="w", fill="x", pady=(0, 20))
		root_pitch = scale[0]

		def draw(_event: tk.Event | None = None) -> None:
			canvas.delete("all")
			left, top, string_gap = 58, 46, 42
			fret_width = max(30, (canvas.winfo_width() - left - 12) / 12)
			right = left + fret_width * 12
			canvas.create_rectangle(left, top, right, top + string_gap * 5, fill=FRETBOARD_COLOR, outline="")

			for fret in range(13):
				x = left + fret * fret_width
				canvas.create_line(x, top, x, top + string_gap * 5, fill="#614b38", width=3 if fret == 0 else 1)
				canvas.create_text(
					fret_center_x(fret, left, fret_width), top - 18,
					text="Open" if fret == 0 else str(fret), fill=INK,
				)
			for string_index in range(6):
				y = top + string_index * string_gap
				canvas.create_line(left, y, right, y, fill="#453a30", width=1 + string_index // 2)
				canvas.create_text(24, y, text=("E", "A", "D", "G", "B", "e")[string_index], fill=INK, font=("Segoe UI", 10, "bold"))
				for fret, note in enumerate(notes_by_string[string_index]):
					if not note:
						continue
					x = fret_center_x(fret, left, fret_width)
					canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill=ACCENT if note == root_pitch else SCALE_COLOR, outline="")
					canvas.create_text(x, y, text=note, fill="white" if note == root_pitch else INK, font=("Segoe UI", 9, "bold"))

			for fret in (3, 5, 7, 9, 12):
				x = fret_center_x(fret, left, fret_width)
				y = top + string_gap * 2.5
				if fret == 12:
					for string_index in (1, 4):
						canvas.create_oval(x - 4, top + string_gap * string_index - 4, x + 4, top + string_gap * string_index + 4, fill="#806b52", outline="")
				else:
					canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#806b52", outline="")

		canvas.bind("<Configure>", draw)
		draw()

	def _draw_chord(self, parent: ttk.Frame, notes: list[str]) -> None:
		shape = chord_voicing(notes)
		fretted = [fret for fret in shape if fret not in (None, 0)]
		first_fret = max(1, min(fretted, default=1))
		start_fret = 1 if first_fret <= 3 else first_fret
		canvas = tk.Canvas(parent, width=170, height=142, background=BACKGROUND, highlightthickness=0)
		canvas.pack(pady=(5, 0))
		left, top, string_gap, fret_gap = 28, 29, 22, 21
		for string in range(6):
			x = left + string * string_gap
			canvas.create_line(x, top, x, top + fret_gap * 4, fill=INK, width=2 if string == 0 else 1)
			fret = shape[string]
			marker = "x" if fret is None else "o" if fret == 0 else ""
			if marker:
				canvas.create_text(x, top - 14, text=marker, fill=INK, font=("Segoe UI", 10, "bold"))
			elif start_fret <= fret < start_fret + 4:
				y = top + (fret - start_fret + 0.5) * fret_gap
				canvas.create_oval(x - 7, y - 7, x + 7, y + 7, fill=ACCENT, outline="")
		for row in range(5):
			y = top + row * fret_gap
			canvas.create_line(left, y, left + string_gap * 5, y, fill=INK, width=3 if row == 0 and start_fret == 1 else 1)
		if start_fret > 1:
			canvas.create_text(10, top + fret_gap / 2, text=str(start_fret), fill=INK, font=("Segoe UI", 9))
		canvas.create_text(85, 133, text="E   A   D   G   B   e", fill=INK, font=("Segoe UI", 8))

	def run(self) -> None:
		self.root.mainloop()


if __name__ == "__main__":
	MusicKeyFinder().run()
