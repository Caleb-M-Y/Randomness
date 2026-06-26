from __future__ import annotations

import random
from pathlib import Path
from tkinter import Button, Label, StringVar, Tk
from tkinter import ttk

import winsound


APP_TITLE = "Fake Loading Button"
WINDOW_SIZE = "500x360"
LOAD_DURATION_MS = 20_000
UPDATE_INTERVAL_MS = 100
MAX_PROGRESS = LOAD_DURATION_MS // UPDATE_INTERVAL_MS
SOUND_DIR = Path(__file__).resolve().parents[1] / "button" / "sounds"


class FakeLoadingApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg="white")

        self.status_text = StringVar(value="Press the button if you dare.")
        self.progress_value = 0
        self.loading = False

        self.press_button = Button(
            self.root,
            text="do not press",
            bg="#d72626",
            fg="white",
            activebackground="#a80f0f",
            activeforeground="white",
            font=("Segoe UI", 20, "bold"),
            padx=24,
            pady=18,
            bd=0,
            relief="flat",
            command=self.start_loading,
        )
        self.press_button.place(relx=0.5, rely=0.35, anchor="center")

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            mode="determinate",
            length=360,
            maximum=MAX_PROGRESS,
        )
        self.progress.place(relx=0.5, rely=0.60, anchor="center")
        self.progress.place_forget()

        self.status_label = Label(
            self.root,
            textvariable=self.status_text,
            bg="white",
            fg="#333333",
            font=("Segoe UI", 11),
        )
        self.status_label.place(relx=0.5, rely=0.78, anchor="center")

    def start_loading(self) -> None:
        if self.loading:
            return

        self.loading = True
        self.progress_value = 0
        self.progress["value"] = 0
        self.progress.place(relx=0.5, rely=0.60, anchor="center")
        self.press_button.configure(state="disabled")
        self.status_text.set("Loading... 0%")
        self.root.after(UPDATE_INTERVAL_MS, self.tick_loading)

    def tick_loading(self) -> None:
        if not self.loading:
            return

        self.progress_value += 1
        self.progress["value"] = self.progress_value

        percent = int((self.progress_value / MAX_PROGRESS) * 100)
        self.status_text.set(f"Loading... {percent}%")

        if self.progress_value >= MAX_PROGRESS:
            self.finish_loading()
            return

        self.root.after(UPDATE_INTERVAL_MS, self.tick_loading)

    def finish_loading(self) -> None:
        self.loading = False
        self.play_random_sound()
        self.status_text.set("Done. Sound played. Press again for another one.")
        self.press_button.configure(state="normal")

    def play_random_sound(self) -> None:
        wav_files = [
            path
            for path in SOUND_DIR.glob("*.wav")
            if path.is_file()
        ]

        if not wav_files:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            self.status_text.set("No .wav files found in apps/button/sounds.")
            return

        chosen = random.choice(wav_files)
        winsound.PlaySound(str(chosen), winsound.SND_FILENAME | winsound.SND_ASYNC)


def main() -> None:
    root = Tk()
    FakeLoadingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
