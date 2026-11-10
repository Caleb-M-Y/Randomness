# Guitar Key Finder

A standalone Tkinter app for exploring the notes and diatonic triads in major and natural-minor keys. It also highlights the scale notes on a standard-tuned guitar fretboard through fret 12 and draws a playable chord shape for each triad. Chord diagrams use familiar open-position shapes when available, then movable versions of those shapes.

## Run

From the repository root:

```powershell
python apps/music_key_finder/music_key_finder.py
```

The app uses only the Python standard library. Choose a tonic and scale from the dropdowns; the displayed notes, chords, fretboard, and chord diagrams update immediately.

## Chord-shape reference

The C-major open-position triads are based on the [Chords in the Key of C triad chart](https://onlineguitarbooks.com/wp-content/uploads/2023/06/Chords-in-the-Key-of-C-Triads.png). For other keys, the app transposes common open-position major/minor forms and favors compact shapes with at most four fretted positions.

## Tests

```powershell
python -m unittest discover -s apps/music_key_finder/tests
```
