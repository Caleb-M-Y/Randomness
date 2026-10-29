from __future__ import annotations

from itertools import product


NOTE_LETTERS = ("C", "D", "E", "F", "G", "A", "B")
NATURAL_PITCHES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
TONICS = (
	"C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb",
	"G", "G#", "Ab", "A", "A#", "Bb", "B",
)
MAJOR_INTERVALS = (0, 2, 4, 5, 7, 9, 11)
MINOR_INTERVALS = (0, 2, 3, 5, 7, 8, 10)
TUNING = ("E", "A", "D", "G", "B", "E")

# Common open-position voicings; the C-major triads follow the linked chord chart.
CHORD_SHAPES = {
	"Major": (
		(0, (None, 3, 2, 0, 1, 0)),
		(5, (None, None, 3, 2, 1, 1)),
		(7, (3, 2, 0, 0, 0, 3)),
		(4, (0, 2, 2, 1, 0, 0)),
		(9, (None, 0, 2, 2, 2, 0)),
		(2, (None, None, 0, 2, 3, 2)),
	),
	"minor": (
		(2, (None, None, 0, 2, 3, 1)),
		(4, (0, 2, 2, 0, 0, 0)),
		(9, (None, 0, 2, 2, 1, 0)),
	),
	"diminished": ((11, (None, None, None, 4, 3, 1)),),
}

def _pitch_class(note: str) -> int:
	letter = note[0]
	accidental = note[1:]
	return (NATURAL_PITCHES[letter] + accidental.count("#") - accidental.count("b")) % 12


def _spell_note(letter: str, pitch: int) -> str:
	difference = (pitch - NATURAL_PITCHES[letter]) % 12
	accidental = {0: "", 1: "#", 2: "##", 10: "bb", 11: "b"}.get(difference)
	if accidental is None:
		raise ValueError(f"Cannot spell pitch {pitch} using note letter {letter}.")
	return letter + accidental


def scale_notes(tonic: str, mode: str = "Major") -> list[str]:
	"""Return the correctly spelled seven notes in a major or natural-minor scale."""
	if tonic not in TONICS:
		raise ValueError(f"Unsupported tonic: {tonic}")
	if mode not in ("Major", "Natural minor"):
		raise ValueError(f"Unsupported mode: {mode}")

	intervals = MAJOR_INTERVALS if mode == "Major" else MINOR_INTERVALS
	start_letter = NOTE_LETTERS.index(tonic[0])
	root_pitch = _pitch_class(tonic)
	return [
		_spell_note(NOTE_LETTERS[(start_letter + degree) % 7], (root_pitch + interval) % 12)
		for degree, interval in enumerate(intervals)
	]


def diatonic_chords(notes: list[str], mode: str = "Major") -> list[dict[str, object]]:
	"""Build the seven diatonic triads and their standard Roman-numeral labels."""
	if len(notes) != 7:
		raise ValueError("A diatonic scale must contain seven notes.")
	qualities = (
		("Major", "minor", "minor", "Major", "Major", "minor", "diminished")
		if mode == "Major"
		else ("minor", "diminished", "Major", "minor", "minor", "Major", "Major")
	)
	roman = ("I", "II", "III", "IV", "V", "VI", "VII")
	if mode == "Natural minor":
		roman = ("i", "ii", "iii", "iv", "v", "vi", "vii")

	chords = []
	for degree, quality in enumerate(qualities):
		chord_notes = [notes[(degree + offset) % 7] for offset in (0, 2, 4)]
		label = roman[degree]
		if quality == "minor":
			label = label.lower()
		elif quality == "diminished":
			label = label.lower() + "°"
		chords.append({
			"degree": label,
			"name": f"{chord_notes[0]} {quality}",
			"notes": chord_notes,
		})
	return chords


def fretboard_notes(tonic: str, mode: str, fret_count: int = 12) -> list[list[str]]:
	"""Return note names from the open string through fret_count for each guitar string."""
	notes = scale_notes(tonic, mode)
	pitches = {_pitch_class(note): note for note in notes}
	return [
		[
			pitches.get((_pitch_class(string) + fret) % 12, "")
			for fret in range(fret_count + 1)
		]
		for string in TUNING
	]


def chord_voicing(chord_notes: list[str], max_fret: int = 12) -> tuple[int | None, ...]:
	"""Choose a familiar chord shape or a compact, fingerable triad voicing."""
	targets = {_pitch_class(note) for note in chord_notes}
	root = _pitch_class(chord_notes[0])

	quality = next(
		(
			chord_quality
			for chord_quality, intervals in (
				("Major", (0, 4, 7)),
				("minor", (0, 3, 7)),
				("diminished", (0, 3, 6)),
			)
			if {(root + interval) % 12 for interval in intervals} == targets
		),
		None,
	)
	movable_candidates = []
	exact_candidates = []
	if quality in CHORD_SHAPES:
		for template_root, template in CHORD_SHAPES[quality]:
			root_difference = (root - template_root) % 12
			for shift in range(-12, 13):
				if shift % 12 != root_difference:
					continue
				shape = tuple(
					None if fret is None else fret + shift
					for fret in template
				)
				if any(fret is not None and not 0 <= fret <= max_fret for fret in shape):
					continue
				if _shape_pitches(shape) != targets:
					continue
				candidate = (*_shape_score(shape, root), shape)
				(exact_candidates if shift == 0 else movable_candidates).append(candidate)
	if exact_candidates:
		return min(exact_candidates, key=lambda candidate: candidate[:-1])[-1]

	options = []
	for string in TUNING:
		string_pitch = _pitch_class(string)
		options.append(
			[None] + [
				fret for fret in range(max_fret + 1)
				if (string_pitch + fret) % 12 in targets
			]
		)

	candidates = movable_candidates
	for shape in product(*options):
		sounding = [fret for fret in shape if fret is not None]
		if len(sounding) < 3 or _shape_pitches(shape) != targets:
			continue
		first_string = next(i for i, fret in enumerate(shape) if fret is not None)
		last_string = next(i for i in range(5, -1, -1) if shape[i] is not None)
		if any(fret is None for fret in shape[first_string:last_string + 1]):
			continue
		fretted = [fret for fret in shape if fret not in (None, 0)]
		if len(set(fretted)) > 4 or (
			fretted and max(fretted) - min(fretted) > 4
		):
			continue
		candidates.append((*_shape_score(shape, root), shape))

	if not candidates:
		raise ValueError(f"No playable voicing found for {', '.join(chord_notes)}.")
	return min(candidates, key=lambda candidate: candidate[:-1])[-1]


def _shape_pitches(shape: tuple[int | None, ...]) -> set[int]:
	return {
		(_pitch_class(TUNING[string]) + fret) % 12
		for string, fret in enumerate(shape)
		if fret is not None
	}


def _shape_score(shape: tuple[int | None, ...], root: int) -> tuple[int, ...]:
	fretted = [fret for fret in shape if fret not in (None, 0)]
	sounding = [fret for fret in shape if fret is not None]
	bass_string = next(i for i, fret in enumerate(shape) if fret is not None)
	bass_pitch = (_pitch_class(TUNING[bass_string]) + shape[bass_string]) % 12
	return (
		0 if bass_pitch == root else 1,
		max(fretted, default=0) - min(fretted, default=0),
		len(set(fretted)),
		max(fretted, default=0),
		-shape.count(0),
		-len(sounding),
	)
