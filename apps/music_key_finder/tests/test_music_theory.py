import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from music_theory import (
	TUNING,
	chord_voicing,
	diatonic_chords,
	fretboard_notes,
	scale_notes,
)
from music_key_finder import fret_center_x


class MusicTheoryTests(unittest.TestCase):
	def test_e_major_scale_and_diatonic_triads(self):
		notes = scale_notes("E", "Major")
		self.assertEqual(notes, ["E", "F#", "G#", "A", "B", "C#", "D#"])
		chords = diatonic_chords(notes)
		self.assertEqual([chord["name"] for chord in chords], [
			"E Major", "F# minor", "G# minor", "A Major", "B Major", "C# minor", "D# diminished",
		])
		self.assertEqual(chords[0]["notes"], ["E", "G#", "B"])

	def test_b_flat_major_scale_uses_flat_spelling(self):
		self.assertEqual(scale_notes("Bb"), ["Bb", "C", "D", "Eb", "F", "G", "A"])

	def test_natural_minor_triads(self):
		notes = scale_notes("A", "Natural minor")
		self.assertEqual(notes, ["A", "B", "C", "D", "E", "F", "G"])
		self.assertEqual([chord["name"] for chord in diatonic_chords(notes, "Natural minor")], [
			"A minor", "B diminished", "C Major", "D minor", "E minor", "F Major", "G Major",
		])

	def test_fretboard_marks_the_scale_and_repeats_octave_notes(self):
		board = fretboard_notes("E", "Major", 12)
		self.assertEqual(len(board), 6)
		self.assertEqual(len(board[0]), 13)
		self.assertEqual(board[0][0], "E")
		self.assertEqual(board[0][12], "E")
		self.assertEqual(board[0][1], "")
		self.assertEqual(board[0][4], "G#")
		self.assertEqual(board[0][11], "D#")

	def test_fretboard_x_positions_continue_through_fret_twelve(self):
		self.assertEqual(fret_center_x(0, 58, 60), 58)
		self.assertEqual(fret_center_x(1, 58, 60), 88)
		self.assertEqual(fret_center_x(12, 58, 60), 748)

	def test_c_major_shapes_match_common_open_position_voicings(self):
		expected = (
			(None, 3, 2, 0, 1, 0),
			(None, None, 0, 2, 3, 1),
			(0, 2, 2, 0, 0, 0),
			(None, None, 3, 2, 1, 1),
			(3, 2, 0, 0, 0, 3),
			(None, 0, 2, 2, 1, 0),
			(None, None, None, 4, 3, 1),
		)
		for chord, expected_shape in zip(diatonic_chords(scale_notes("C")), expected):
			with self.subTest(chord=chord["name"]):
				self.assertEqual(chord_voicing(chord["notes"]), expected_shape)

	def test_transposed_shapes_are_playable_and_contain_the_chord_tones(self):
		for tonic in ("E", "Bb", "F#"):
			for mode in ("Major", "Natural minor"):
				for chord in diatonic_chords(scale_notes(tonic, mode), mode):
					with self.subTest(tonic=tonic, mode=mode, chord=chord["name"]):
						shape = chord_voicing(chord["notes"])
						self.assertEqual(len(shape), 6)
						self.assertTrue(all(fret is None or 0 <= fret <= 12 for fret in shape))
						self.assertEqual(_voiced_pitches(shape), {
							_note_pitch(note) for note in chord["notes"]
						})
						self.assertLessEqual(len({
							fret for fret in shape if fret not in (None, 0)
						}), 4)


def _note_pitch(note):
	natural_pitches = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
	pitch = natural_pitches[note[0]]
	return (pitch + note[1:].count("#") - note[1:].count("b")) % 12


def _voiced_pitches(shape):
	return {
		(_note_pitch(note) + fret) % 12
		for note, fret in zip(TUNING, shape)
		if fret is not None
	}


if __name__ == "__main__":
	unittest.main()
