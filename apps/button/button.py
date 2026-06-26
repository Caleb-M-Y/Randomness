from __future__ import annotations

import json
import random
from pathlib import Path
from tkinter import Button, Label, Tk

import winsound


APP_TITLE = "Random Button"
SOUNDS_FILE = Path(__file__).with_name("sounds.json")
SOUNDS_DIR = Path(__file__).with_name("sounds")


def load_enabled_sounds() -> list[Path]:
	"""Load enabled sound paths from the local JSON catalog."""
	if not SOUNDS_FILE.exists():
		return []

	try:
		data = json.loads(SOUNDS_FILE.read_text(encoding="utf-8"))
	except json.JSONDecodeError:
		return []

	sounds = data.get("sounds", [])
	enabled_files: list[Path] = []
	for item in sounds:
		if item.get("enabled"):
			filename = item.get("file")
			if isinstance(filename, str) and filename.strip():
				enabled_files.append(SOUNDS_DIR / filename)
	return enabled_files


def play_random_sound(status_label: Label) -> None:
	"""Play a random enabled sound, or a beep if no sound file is available."""
	sound_paths = load_enabled_sounds()
	existing = [path for path in sound_paths if path.exists()]

	if existing:
		chosen = random.choice(existing)
		# SND_ASYNC keeps the UI responsive while the sound plays.
		winsound.PlaySound(str(chosen), winsound.SND_FILENAME | winsound.SND_ASYNC)
		status_label.config(text=f"Played: {chosen.name}")
		return

	winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
	status_label.config(text="No valid .wav files found. Added fallback beep.")


def main() -> None:
	root = Tk()
	root.title(APP_TITLE)
	root.geometry("420x640")
	root.configure(bg="white")

	button = Button(
		root,
		text="press me if you dare",
		bg="#d72626",
		fg="white",
		activebackground="#a80f0f",
		activeforeground="white",
		font=("Segoe UI", 18, "bold"),
		padx=24,
		pady=20,
		bd=0,
		relief="flat",
		command=lambda: play_random_sound(status),
	)
	button.place(relx=0.5, rely=0.5, anchor="center")

	status = Label(
		root,
		text="Ready. Add .wav files to apps/button/sounds.",
		bg="white",
		fg="#333333",
		font=("Segoe UI", 10),
	)
	status.place(relx=0.5, rely=0.88, anchor="center")

	root.mainloop()


if __name__ == "__main__":
	main()
