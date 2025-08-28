# midi_notes

Provides various tables (dicts) and functions for looking up / converting note
names, scales, midi note pitch, frequencies, an a "Note" class which allows you
constuct / represent Notes by MIDI pitch, note name or frequency.

## Note class

You can construct a Note with either a (str) note name, (int) midi pitch, or
(float) frequency.

	from midi_notes import *

	>>> note = Note('C4')
	>>> print(f'"{note.name}" has midi pitch {note.pitch}')
	"C4" has MIDI pitch 60

	>>> print(f'"{note.name}" is in octave {note.octave}, and has a value of {note.interval_above_c}')
	"C4" is in octave 4, and has a value of 0

	>>> print(f'"{note.name}" has a frequency of {note.frequency}Hz')
	"C4" has a frequency of 261.626Hz

	>>> frequency = 444.4
	>>> note = Note(frequency)
	>>> print(f'"{note.name}" with a frequency of {note.frequency}Hz is closest to {frequency}Hz')
	"A4" with a frequency of 440.0Hz is closest to 444.4Hz

### Sharps and Flats

When getting the "name" property of a Note which is an incidental, you can
decide whether to retrieve the "sharp" or "flat" version of the note name
("D♯" is the same pitch as "E♭") by setting the "prefer_flats" property.

	>>> note = Note('D#5')
	>>> print(f'MIDI pitch {note.pitch} is "{note.name}"')
	MIDI pitch 75 is "D#5"

	>>> note.prefer_flats = True
	>>> print(f'MIDI pitch {note.pitch} is also "{note.name}"')
	MIDI pitch 75 is also "Eb5"


### Incidentals styles

You can also choose how to render incidentals:

	>>> note = Note('D#5')

	>>> note.incidentals_style = Note.INCIDENTAL_ASCII
	>>> print(f'INCIDENTAL_ASCII: "{note.name}"')
	INCIDENTAL_ASCII: "Eb5"

	>>> note.incidentals_style = Note.INCIDENTAL_UNICODE
	>>> print(f'INCIDENTAL_UNICODE: "{note.name}"')
	INCIDENTAL_UNICODE: "E♭5"

	>>> note.incidentals_style = Note.INCIDENTAL_NAMES
	>>> print(f'INCIDENTAL_NAMES: "{note.name}"')
	INCIDENTAL_NAMES: "E flat 5"


## Constants

The following constants are defined:

	MIDDLE_C

	CHAR_FLAT
	CHAR_FLAT_ASCII
	CHAR_FLAT_UNICODE
	CHAR_SHARP
	CHAR_SHARP_ASCII
	CHAR_SHARP_UNICODE

	NOTE_TABLE
	NOTE_NAMES
	NOTE_PITCHES
	NOTE_FREQUENCIES
	NOTE_OFFSETS
	NOTE_NAME_SHARPS
	NOTE_NAME_FLATS

	MAJOR_SCALE_INTERVALS
	MINOR_SCALE_INTERVALS
	COMMON_MAJOR_KEYS
	MAJOR_SCALES
	COMMON_MINOR_KEYS
	MINOR_SCALES

	DURATION_NAMES
	DURATION_SYMBOLS
	DURATION_FRACTIONS

	MIDI_NOTE_OFF
	MIDI_NOTE_ON
	MIDI_POLY_PRESSURE
	MIDI_CONTROL_CHANGE
	MIDI_PROGRAM_SELECT
	MIDI_PRESSURE
	MIDI_PITCH_BEND
	MIDI_PROGRAM_NAMES

	MIDI_DRUM_IDS
	MIDI_DRUM_PITCHES
	MIDI_DRUM_NAMES
