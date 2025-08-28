#  midi_notes/__init__.py
#
#  Copyright 2024 liyang <liyang@veronica>
#
"""
Various tables (dicts) and functions for converting between note names, midi
note numbers, frequencies, plus a single "Note" class which allows you to
switch seamlessly between pitch/note name/frequency representations.
"""
import re
from math import floor
from bisect import bisect_left

__version__ = "1.1.0"

MIDDLE_C = 60
CHAR_FLAT = '♭'
CHAR_FLAT_ASCII = 'b'
CHAR_FLAT_UNICODE = '\u266D'
CHAR_SHARP = '♯'
CHAR_SHARP_ASCII = '#'
CHAR_SHARP_UNICODE = '\u266F'

NOTE_TABLE = {
	0:		('C-1', 'C', -1, 8.176),
	1:		('C#-1', 'C#', -1, 8.662),
	2:		('D-1', 'D', -1, 9.177),
	3:		('D#-1', 'D#', -1, 9.723),
	4:		('E-1', 'E', -1, 10.301),
	5:		('F-1', 'F', -1, 10.913),
	6:		('F#-1', 'F#', -1, 11.562),
	7:		('G-1', 'G', -1, 12.250),
	8:		('G#-1', 'G#', -1, 12.978),
	9:		('A-1', 'A', -1, 13.750),
	10:		('A#-1', 'A#', -1, 14.568),
	11:		('B-1', 'B', -1, 15.434),
	12:		('C0', 'C', 0, 16.352),
	13:		('C#0', 'C#', 0, 17.324),
	14:		('D0', 'D', 0, 18.354),
	15:		('D#0', 'D#', 0, 19.445),
	16:		('E0', 'E', 0, 20.602),
	17:		('F0', 'F', 0, 21.827),
	18:		('F#0', 'F#', 0, 23.125),
	19:		('G0', 'G', 0, 24.500),
	20:		('G#0', 'G#', 0, 25.957),
	21:		('A0', 'A', 0, 27.500),
	22:		('A#0', 'A#', 0, 29.135),
	23:		('B0', 'B', 0, 30.868),
	24:		('C1', 'C', 1, 32.703),
	25:		('C#1', 'C#', 1, 34.648),
	26:		('D1', 'D', 1, 36.708),
	27:		('D#1', 'D#', 1, 38.891),
	28:		('E1', 'E', 1, 41.203),
	29:		('F1', 'F', 1, 43.654),
	30:		('F#1', 'F#', 1, 46.249),
	31:		('G1', 'G', 1, 48.999),
	32:		('G#1', 'G#', 1, 51.913),
	33:		('A1', 'A', 1, 55.000),
	34:		('A#1', 'A#', 1, 58.270),
	35:		('B1', 'B', 1, 61.735),
	36:		('C2', 'C', 2, 65.406),
	37:		('C#2', 'C#', 2, 69.296),
	38:		('D2', 'D', 2, 73.416),
	39:		('D#2', 'D#', 2, 77.782),
	40:		('E2', 'E', 2, 82.407),
	41:		('F2', 'F', 2, 87.307),
	42:		('F#2', 'F#', 2, 92.499),
	43:		('G2', 'G', 2, 97.999),
	44:		('G#2', 'G#', 2, 103.826),
	45:		('A2', 'A', 2, 110.000),
	46:		('A#2', 'A#', 2, 116.541),
	47:		('B2', 'B', 2, 123.471),
	48:		('C3', 'C', 3, 130.813),
	49:		('C#3', 'C#', 3, 138.591),
	50:		('D3', 'D', 3, 146.832),
	51:		('D#3', 'D#', 3, 155.563),
	52:		('E3', 'E', 3, 164.814),
	53:		('F3', 'F', 3, 174.614),
	54:		('F#3', 'F#', 3, 184.997),
	55:		('G3', 'G', 3, 195.998),
	56:		('G#3', 'G#', 3, 207.652),
	57:		('A3', 'A', 3, 220.000),
	58:		('A#3', 'A#', 3, 233.082),
	59:		('B3', 'B', 3, 246.942),
	60:		('C4', 'C', 4, 261.626),
	61:		('C#4', 'C#', 4, 277.183),
	62:		('D4', 'D', 4, 293.665),
	63:		('D#4', 'D#', 4, 311.127),
	64:		('E4', 'E', 4, 329.628),
	65:		('F4', 'F', 4, 349.228),
	66:		('F#4', 'F#', 4, 369.994),
	67:		('G4', 'G', 4, 391.995),
	68:		('G#4', 'G#', 4, 415.305),
	69:		('A4', 'A', 4, 440.000),
	70:		('A#4', 'A#', 4, 466.164),
	71:		('B4', 'B', 4, 493.883),
	72:		('C5', 'C', 5, 523.251),
	73:		('C#5', 'C#', 5, 554.365),
	74:		('D5', 'D', 5, 587.330),
	75:		('D#5', 'D#', 5, 622.254),
	76:		('E5', 'E', 5, 659.255),
	77:		('F5', 'F', 5, 698.456),
	78:		('F#5', 'F#', 5, 739.989),
	79:		('G5', 'G', 5, 783.991),
	80:		('G#5', 'G#', 5, 830.609),
	81:		('A5', 'A', 5, 880.000),
	82:		('A#5', 'A#', 5, 932.328),
	83:		('B5', 'B', 5, 987.767),
	84:		('C6', 'C', 6, 1046.502),
	85:		('C#6', 'C#', 6, 1108.731),
	86:		('D6', 'D', 6, 1174.659),
	87:		('D#6', 'D#', 6, 1244.508),
	88:		('E6', 'E', 6, 1318.510),
	89:		('F6', 'F', 6, 1396.913),
	90:		('F#6', 'F#', 6, 1479.978),
	91:		('G6', 'G', 6, 1567.982),
	92:		('G#6', 'G#', 6, 1661.219),
	93:		('A6', 'A', 6, 1760.000),
	94:		('A#6', 'A#', 6, 1864.655),
	95:		('B6', 'B', 6, 1975.533),
	96:		('C7', 'C', 7, 2093.005),
	97:		('C#7', 'C#', 7, 2217.461),
	98:		('D7', 'D', 7, 2349.318),
	99:		('D#7', 'D#', 7, 2489.016),
	100:		('E7', 'E', 7, 2637.020),
	101:		('F7', 'F', 7, 2793.826),
	102:		('F#7', 'F#', 7, 2959.955),
	103:		('G7', 'G', 7, 3135.963),
	104:		('G#7', 'G#', 7, 3322.438),
	105:		('A7', 'A', 7, 3520.000),
	106:		('A#7', 'A#', 7, 3729.310),
	107:		('B7', 'B', 7, 3951.066),
	108:		('C8', 'C', 8, 4186.009),
	109:		('C#8', 'C#', 8, 4434.922),
	110:		('D8', 'D', 8, 4698.636),
	111:		('D#8', 'D#', 8, 4978.032),
	112:		('E8', 'E', 8, 5274.041),
	113:		('F8', 'F', 8, 5587.652),
	114:		('F#8', 'F#', 8, 5919.911),
	115:		('G8', 'G', 8, 6271.927),
	116:		('G#8', 'G#', 8, 6644.875),
	117:		('A8', 'A', 8, 7040.000),
	118:		('A#8', 'A#', 8, 7458.620),
	119:		('B8', 'B', 8, 7902.133),
	120:		('C9', 'C', 9, 8372.018),
	121:		('C#9', 'C#', 9, 8869.844),
	122:		('D9', 'D', 9, 9397.273),
	123:		('D#9', 'D#', 9, 9956.063),
	124:		('E9', 'E', 9, 10548.080),
	125:		('F9', 'F', 9, 11175.300),
	126:		('F#9', 'F#', 9, 11839.820),
	127:		('G9', 'G', 9, 12543.850)
}

NOTE_NAMES = [
	'C-1',
	'C#-1',
	'D-1',
	'D#-1',
	'E-1',
	'F-1',
	'F#-1',
	'G-1',
	'G#-1',
	'A-1',
	'A#-1',
	'B-1',
	'C0',
	'C#0',
	'D0',
	'D#0',
	'E0',
	'F0',
	'F#0',
	'G0',
	'G#0',
	'A0',
	'A#0',
	'B0',
	'C1',
	'C#1',
	'D1',
	'D#1',
	'E1',
	'F1',
	'F#1',
	'G1',
	'G#1',
	'A1',
	'A#1',
	'B1',
	'C2',
	'C#2',
	'D2',
	'D#2',
	'E2',
	'F2',
	'F#2',
	'G2',
	'G#2',
	'A2',
	'A#2',
	'B2',
	'C3',
	'C#3',
	'D3',
	'D#3',
	'E3',
	'F3',
	'F#3',
	'G3',
	'G#3',
	'A3',
	'A#3',
	'B3',
	'C4',
	'C#4',
	'D4',
	'D#4',
	'E4',
	'F4',
	'F#4',
	'G4',
	'G#4',
	'A4',
	'A#4',
	'B4',
	'C5',
	'C#5',
	'D5',
	'D#5',
	'E5',
	'F5',
	'F#5',
	'G5',
	'G#5',
	'A5',
	'A#5',
	'B5',
	'C6',
	'C#6',
	'D6',
	'D#6',
	'E6',
	'F6',
	'F#6',
	'G6',
	'G#6',
	'A6',
	'A#6',
	'B6',
	'C7',
	'C#7',
	'D7',
	'D#7',
	'E7',
	'F7',
	'F#7',
	'G7',
	'G#7',
	'A7',
	'A#7',
	'B7',
	'C8',
	'C#8',
	'D8',
	'D#8',
	'E8',
	'F8',
	'F#8',
	'G8',
	'G#8',
	'A8',
	'A#8',
	'B8',
	'C9',
	'C#9',
	'D9',
	'D#9',
	'E9',
	'F9',
	'F#9',
	'G9'
]

NOTE_PITCHES = {
	'C-1':		0,
	'C#-1':		1,
	'D-1':		2,
	'D#-1':		3,
	'E-1':		4,
	'F-1':		5,
	'F#-1':		6,
	'G-1':		7,
	'G#-1':		8,
	'A-1':		9,
	'A#-1':		10,
	'B-1':		11,
	'C0':		12,
	'C#0':		13,
	'D0':		14,
	'D#0':		15,
	'E0':		16,
	'F0':		17,
	'F#0':		18,
	'G0':		19,
	'G#0':		20,
	'A0':		21,
	'A#0':		22,
	'B0':		23,
	'C1':		24,
	'C#1':		25,
	'D1':		26,
	'D#1':		27,
	'E1':		28,
	'F1':		29,
	'F#1':		30,
	'G1':		31,
	'G#1':		32,
	'A1':		33,
	'A#1':		34,
	'B1':		35,
	'C2':		36,
	'C#2':		37,
	'D2':		38,
	'D#2':		39,
	'E2':		40,
	'F2':		41,
	'F#2':		42,
	'G2':		43,
	'G#2':		44,
	'A2':		45,
	'A#2':		46,
	'B2':		47,
	'C3':		48,
	'C#3':		49,
	'D3':		50,
	'D#3':		51,
	'E3':		52,
	'F3':		53,
	'F#3':		54,
	'G3':		55,
	'G#3':		56,
	'A3':		57,
	'A#3':		58,
	'B3':		59,
	'C4':		60,
	'C#4':		61,
	'D4':		62,
	'D#4':		63,
	'E4':		64,
	'F4':		65,
	'F#4':		66,
	'G4':		67,
	'G#4':		68,
	'A4':		69,
	'A#4':		70,
	'B4':		71,
	'C5':		72,
	'C#5':		73,
	'D5':		74,
	'D#5':		75,
	'E5':		76,
	'F5':		77,
	'F#5':		78,
	'G5':		79,
	'G#5':		80,
	'A5':		81,
	'A#5':		82,
	'B5':		83,
	'C6':		84,
	'C#6':		85,
	'D6':		86,
	'D#6':		87,
	'E6':		88,
	'F6':		89,
	'F#6':		90,
	'G6':		91,
	'G#6':		92,
	'A6':		93,
	'A#6':		94,
	'B6':		95,
	'C7':		96,
	'C#7':		97,
	'D7':		98,
	'D#7':		99,
	'E7':		100,
	'F7':		101,
	'F#7':		102,
	'G7':		103,
	'G#7':		104,
	'A7':		105,
	'A#7':		106,
	'B7':		107,
	'C8':		108,
	'C#8':		109,
	'D8':		110,
	'D#8':		111,
	'E8':		112,
	'F8':		113,
	'F#8':		114,
	'G8':		115,
	'G#8':		116,
	'A8':		117,
	'A#8':		118,
	'B8':		119,
	'C9':		120,
	'C#9':		121,
	'D9':		122,
	'D#9':		123,
	'E9':		124,
	'F9':		125,
	'F#9':		126,
	'G9':		127
}

NOTE_FREQUENCIES = [
	8.176,
	8.662,
	9.177,
	9.723,
	10.301,
	10.913,
	11.562,
	12.250,
	12.978,
	13.750,
	14.568,
	15.434,
	16.352,
	17.324,
	18.354,
	19.445,
	20.602,
	21.827,
	23.125,
	24.500,
	25.957,
	27.500,
	29.135,
	30.868,
	32.703,
	34.648,
	36.708,
	38.891,
	41.203,
	43.654,
	46.249,
	48.999,
	51.913,
	55.000,
	58.270,
	61.735,
	65.406,
	69.296,
	73.416,
	77.782,
	82.407,
	87.307,
	92.499,
	97.999,
	103.826,
	110.000,
	116.541,
	123.471,
	130.813,
	138.591,
	146.832,
	155.563,
	164.814,
	174.614,
	184.997,
	195.998,
	207.652,
	220.000,
	233.082,
	246.942,
	261.626,
	277.183,
	293.665,
	311.127,
	329.628,
	349.228,
	369.994,
	391.995,
	415.305,
	440.000,
	466.164,
	493.883,
	523.251,
	554.365,
	587.330,
	622.254,
	659.255,
	698.456,
	739.989,
	783.991,
	830.609,
	880.000,
	932.328,
	987.767,
	1046.502,
	1108.731,
	1174.659,
	1244.508,
	1318.510,
	1396.913,
	1479.978,
	1567.982,
	1661.219,
	1760.000,
	1864.655,
	1975.533,
	2093.005,
	2217.461,
	2349.318,
	2489.016,
	2637.020,
	2793.826,
	2959.955,
	3135.963,
	3322.438,
	3520.000,
	3729.310,
	3951.066,
	4186.009,
	4434.922,
	4698.636,
	4978.032,
	5274.041,
	5587.652,
	5919.911,
	6271.927,
	6644.875,
	7040.000,
	7458.620,
	7902.133,
	8372.018,
	8869.844,
	9397.273,
	9956.063,
	10548.080,
	11175.300,
	11839.820,
	12543.850
]

NOTE_OFFSETS = {
	'Cb':		-1,
	'C':		0,
	'C#':		1,
	'Db':		1,
	'D':		2,
	'D#':		3,
	'Eb':		3,
	'E':		4,
	'E#':		5,
	'Fb':		4,
	'F':		5,
	'F#':		6,
	'Gb':		6,
	'G':		7,
	'G#':		8,
	'Ab':		8,
	'A':		9,
	'A#':		10,
	'Bb':		10,
	'B':		11,
	'B#':		12
}

NOTE_NAME_SHARPS = {
	0:	'C',
	1:	'C#',
	2:	'D',
	3:	'D#',
	4:	'E',
	5:	'F',
	6:	'F#',
	7:	'G',
	8:	'G#',
	9:	'A',
	10:	'A#',
	11:	'B'
}

NOTE_NAME_FLATS = {
	0:	'C',
	1:	'Db',
	2:	'D',
	3:	'Eb',
	4:	'E',
	5:	'F',
	6:	'Gb',
	7:	'G',
	8:	'Ab',
	9:	'A',
	10:	'Bb',
	11:	'B'
}

MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]

MINOR_SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]

MAJOR_SCALES = {
	'Db':	 [1, 3, 5, 6, 8, 10, 0],
	'Ab':	 [8, 10, 0, 1, 3, 5, 7],
	'Eb':	 [3, 5, 7, 8, 10, 0, 2],
	'Bb':	 [10, 0, 2, 3, 5, 7, 9],
	'F':	 [5, 7, 9, 10, 0, 2, 4],
	'C':	 [0, 2, 4, 5, 7, 9, 11],
	'G':	 [7, 9, 11, 0, 2, 4, 6],
	'D':	 [2, 4, 6, 7, 9, 11, 1],
	'A':	 [9, 11, 1, 2, 4, 6, 8],
	'E':	 [4, 6, 8, 9, 11, 1, 3],
	'B':	 [11, 1, 3, 4, 6, 8, 10],
	'F#':	 [6, 8, 10, 11, 1, 3, 5]
}

MINOR_SCALES = {
	'Bb':	 [10, 0, 1, 3, 5, 6, 8],
	'F':	 [5, 7, 8, 10, 0, 1, 3],
	'C':	 [0, 2, 3, 5, 7, 8, 10],
	'G':	 [7, 9, 10, 0, 2, 3, 5],
	'D':	 [2, 4, 5, 7, 9, 10, 0],
	'A':	 [9, 11, 0, 2, 4, 5, 7],
	'E':	 [4, 6, 7, 9, 11, 0, 2],
	'B':	 [11, 1, 2, 4, 6, 7, 9],
	'F#':	 [6, 8, 9, 11, 1, 2, 4],
	'C#':	 [1, 3, 4, 6, 8, 9, 11],
	'G#':	 [8, 10, 11, 1, 3, 4, 6],
	'D#':	 [3, 5, 6, 8, 10, 11, 1]
}

COMMON_MAJOR_KEYS = [
	'Db', 'Ab', 'Eb', 'Bb', 'F',
	'C', 'G', 'D', 'A', 'E', 'B', 'F#',
]

COMMON_MINOR_KEYS = [
	'Bb', 'F', 'C', 'G', 'D',
	'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#'
]

DURATION_NAMES = {
	0.015625:	'64th',
	0.03125:	'32nd',
	0.0625:		'16th',
	0.125:		'eighth',
	0.25:		'quarter',
	0.5:		'half',
	1.0:		'whole'
}

DURATION_SYMBOLS = {
	0.015625:	'',
	0.03125:	'',
	0.0625:		'',
	0.125:		'',
	0.25:		'',
	0.5:		'',
	1.0:		''
}

DURATION_FRACTIONS = {
	0.015625:	'1/64',
	0.03125:	'1/32',
	0.0625:		'1/16',
	0.125:		'1/8',
	0.25:		'1/4',
	0.5:		'1/2',
	1.0:		'1'
}

# MIDI event status bytes
# <status_byte> & 0xF0 will equal one of the following values:
MIDI_NOTE_OFF		= 0x80	# 0x8n,x1,x2 - Note Off (x1 = note number, x2 = velocity).
MIDI_NOTE_ON		= 0x90	# 0x9n,x1,x2 - Note On  (x1 = note number, x2 = velocity [x2=0 -> note off]).
MIDI_POLY_PRESSURE	= 0xA0	# 0xBn,x1,x2 - Poly Pressure (x1 = note number, x2 = pressure value).
MIDI_CONTROL_CHANGE	= 0xB0	# 0xCn,x1,x2 - Control Change (x1 = controller number, x2 = value).
MIDI_PROGRAM_SELECT	= 0xC0	# 0xCn,x1    - Program Change (x1 = program number).
MIDI_PRESSURE		= 0xD0	# 0xDn,x1    - Channel (Mono) Pressure (x1 = value).
MIDI_PITCH_BEND		= 0xE0	# 0xEn,x1,x2 - Pitch Bend (x1 = LSB, x2 = MSB).


MIDI_PROGRAM_NAMES = {
	1:		'Acoustic Grand Piano',
	2:		'Bright Acoustic Piano',
	3:		'Electric Grand Piano',
	4:		'Honky-tonk Piano',
	5:		'Electric Piano 1',
	6:		'Electric Piano 2',
	7:		'Harpsichord',
	8:		'Clavi',
	9:		'Celesta',
	10:		'Glockenspiel',
	11:		'Music Box',
	12:		'Vibraphone',
	13:		'Marimba',
	14:		'Xylophone',
	15:		'Tubular Bells',
	16:		'Dulcimer',
	17:		'Drawbar Organ',
	18:		'Percussive Organ',
	19:		'Rock Organ',
	20:		'Church Organ',
	21:		'Reed Organ',
	22:		'Accordion',
	23:		'Harmonica',
	24:		'Tango Accordion',
	25:		'Acoustic Guitar (nylon)',
	26:		'Acoustic Guitar (steel)',
	27:		'Electric Guitar (jazz)',
	28:		'Electric Guitar (clean)',
	29:		'Electric Guitar (muted)',
	30:		'Overdriven Guitar',
	31:		'Distortion Guitar',
	32:		'Guitar harmonics',
	33:		'Acoustic Bass',
	34:		'Electric Bass (finger)',
	35:		'Electric Bass (pick)',
	36:		'Fretless Bass',
	37:		'Slap Bass 1',
	38:		'Slap Bass 2',
	39:		'Synth Bass 1',
	40:		'Synth Bass 2',
	41:		'Violin',
	42:		'Viola',
	43:		'Cello',
	44:		'Contrabass',
	45:		'Tremolo Strings',
	46:		'Pizzicato Strings',
	47:		'Orchestral Harp',
	48:		'Timpani',
	49:		'String Ensemble 1',
	50:		'String Ensemble 2',
	51:		'SynthStrings 1',
	52:		'SynthStrings 2',
	53:		'Choir Aahs',
	54:		'Voice Oohs',
	55:		'Synth Voice',
	56:		'Orchestra Hit',
	57:		'Trumpet',
	58:		'Trombone',
	59:		'Tuba',
	60:		'Muted Trumpet',
	61:		'French Horn',
	62:		'Brass Section',
	63:		'SynthBrass 1',
	64:		'SynthBrass 2',
	65:		'Soprano Sax',
	66:		'Alto Sax',
	67:		'Tenor Sax',
	68:		'Baritone Sax',
	69:		'Oboe',
	70:		'English Horn',
	71:		'Bassoon',
	72:		'Clarinet',
	73:		'Piccolo',
	74:		'Flute',
	75:		'Recorder',
	76:		'Pan Flute',
	77:		'Blown Bottle',
	78:		'Shakuhachi',
	79:		'Whistle',
	80:		'Ocarina',
	81:		'Lead 1 (square)',
	82:		'Lead 2 (sawtooth)',
	83:		'Lead 3 (calliope)',
	84:		'Lead 4 (chiff)',
	85:		'Lead 5 (charang)',
	86:		'Lead 6 (voice)',
	87:		'Lead 7 (fifths)',
	88:		'Lead 8 (bass + lead)',
	89:		'Pad 1 (new age)',
	90:		'Pad 2 (warm)',
	91:		'Pad 3 (polysynth)',
	92:		'Pad 4 (choir)',
	93:		'Pad 5 (bowed)',
	94:		'Pad 6 (metallic)',
	95:		'Pad 7 (halo)',
	96:		'Pad 8 (sweep)',
	97:		'FX 1 (rain)',
	98:		'FX 2 (soundtrack)',
	99:		'FX 3 (crystal)',
	100:	'FX 4 (atmosphere)',
	101:	'FX 5 (brightness)',
	102:	'FX 6 (goblins)',
	103:	'FX 7 (echoes)',
	104:	'FX 8 (sci-fi)',
	105:	'Sitar',
	106:	'Banjo',
	107:	'Shamisen',
	108:	'Koto',
	109:	'Kalimba',
	110:	'Bag pipe',
	111:	'Fiddle',
	112:	'Shanai',
	113:	'Tinkle Bell',
	114:	'Agogo',
	115:	'Steel Drums',
	116:	'Woodblock',
	117:	'Taiko Drum',
	118:	'Melodic Tom',
	119:	'Synth Drum',
	120:	'Reverse Cymbal',
	121:	'Guitar Fret Noise',
	122:	'Breath Noise',
	123:	'Seashore',
	124:	'Bird Tweet',
	125:	'Telephone Ring',
	126:	'Helicopter',
	127:	'Applause',
	128:	'Gunshot'
}

MIDI_DRUM_IDS = {
	35	: 'acoustic_base_drum',
	36	: 'bass_drum_1',
	37	: 'side_stick',
	38	: 'acoustic_snare',
	39	: 'hand_clap',
	40	: 'electric_snare',
	41	: 'low_floor_tom',
	42	: 'closed_hi_hat',
	43	: 'high_floor_tom',
	44	: 'pedal_hi_hat',
	45	: 'low_tom',
	46	: 'open_hi_hat',
	47	: 'low_mid_tom',
	48	: 'hi_mid_tom',
	49	: 'crash_cymbal_1',
	50	: 'high_tom',
	51	: 'ride_cymbal_1',
	52	: 'chinese_cymbal',
	53	: 'ride_bell',
	54	: 'tambourine',
	55	: 'splash_cymbal',
	56	: 'cowbell',
	57	: 'crash_cymbal_2',
	58	: 'vibraslap',
	59	: 'ride_cymbal_2',
	60	: 'hi_bongo',
	61	: 'low_bongo',
	62	: 'mute_hi_conga',
	63	: 'open_hi_conga',
	64	: 'low_conga',
	65	: 'high_timbale',
	66	: 'low_timbale',
	67	: 'high_agogo',
	68	: 'low_agogo',
	69	: 'cabasa',
	70	: 'maracas',
	71	: 'short_whistle',
	72	: 'long_whistle',
	73	: 'short_guiro',
	74	: 'long_guiro',
	75	: 'claves',
	76	: 'hi_wood_block',
	77	: 'low_wood_block',
	78	: 'mute_cuica',
	79	: 'open_cuica',
	80	: 'mute_triangle',
	81	: 'open_triangle'
}

MIDI_DRUM_PITCHES = {
	'acoustic_base_drum': 35,
	'bass_drum_1'		: 36,
	'side_stick'		: 37,
	'acoustic_snare'	: 38,
	'hand_clap'			: 39,
	'electric_snare'	: 40,
	'low_floor_tom'		: 41,
	'closed_hi_hat'		: 42,
	'high_floor_tom'	: 43,
	'pedal_hi_hat'		: 44,
	'low_tom'			: 45,
	'open_hi_hat'		: 46,
	'low_mid_tom'		: 47,
	'hi_mid_tom'		: 48,
	'crash_cymbal_1'	: 49,
	'high_tom'			: 50,
	'ride_cymbal_1'		: 51,
	'chinese_cymbal'	: 52,
	'ride_bell'			: 53,
	'tambourine'		: 54,
	'splash_cymbal'		: 55,
	'cowbell'			: 56,
	'crash_cymbal_2'	: 57,
	'vibraslap'			: 58,
	'ride_cymbal_2'		: 59,
	'hi_bongo'			: 60,
	'low_bongo'			: 61,
	'mute_hi_conga'		: 62,
	'open_hi_conga'		: 63,
	'low_conga'			: 64,
	'high_timbale'		: 65,
	'low_timbale'		: 66,
	'high_agogo'		: 67,
	'low_agogo'			: 68,
	'cabasa'			: 69,
	'maracas'			: 70,
	'short_whistle'		: 71,
	'long_whistle'		: 72,
	'short_guiro'		: 73,
	'long_guiro'		: 74,
	'claves'			: 75,
	'hi_wood_block'		: 76,
	'low_wood_block'	: 77,
	'mute_cuica'		: 78,
	'open_cuica'		: 79,
	'mute_triangle'		: 80,
	'open_triangle'		: 81
}

MIDI_DRUM_NAMES = {
	35	: 'Acoustic Bass Drum',
	36	: 'Bass Drum',
	37	: 'Side Stick',
	38	: 'Acoustic Snare',
	39	: 'Hand Clap',
	40	: 'Electric Snare',
	41	: 'Low Floor Tom',
	42	: 'Closed Hi Hat',
	43	: 'High Floor Tom',
	44	: 'Pedal Hi Hat',
	45	: 'Low Tom',
	46	: 'Open Hi Hat',
	47	: 'Low Mid Tom',
	48	: 'Hi Mid Tom',
	49	: 'Crash Cymbal 1',
	50	: 'High Tom',
	51	: 'Ride Cymbal 1',
	52	: 'Chinese Cymbal',
	53	: 'Ride Bell',
	54	: 'Tambourine',
	55	: 'Splash Cymbal',
	56	: 'Cowbell',
	57	: 'Crash Cymbal 2',
	58	: 'Vibraslap',
	59	: 'Ride Cymbal 2',
	60	: 'Hi Bongo',
	61	: 'Low Bongo',
	62	: 'Mute Hi Conga',
	63	: 'Open Hi Conga',
	64	: 'Low Conga',
	65	: 'High Timbale',
	66	: 'Low Timbale',
	67	: 'High Agogo',
	68	: 'Low Agogo',
	69	: 'Cabasa',
	70	: 'Maracas',
	71	: 'Short Whistle',
	72	: 'Long Whistle',
	73	: 'Short Guiro',
	74	: 'Long Guiro',
	75	: 'Claves',
	76	: 'Hi Wood Block',
	77	: 'Low Wood Block',
	78	: 'Mute Cuica',
	79	: 'Open Cuica',
	80	: 'Mute Triangle',
	81	: 'Open Triangle'
}


class Note:

	_name_values = {
		'A': {' ': 9, '#': 10, 'b': 8},
		'B': {' ': 11, '#': 12, 'b': 10},
		'C': {' ': 0, '#': 1, 'b': -1},
		'D': {' ': 2, '#': 3, 'b': 1},
		'E': {' ': 4, '#': 5, 'b': 3},
		'F': {' ': 5, '#': 6, 'b': 4},
		'G': {' ': 7, '#': 8, 'b': 6}
	}

	_pitch_values = {
		0:	{' ': 'C'},
		1:	{'#': 'C', 'b': 'D'},
		2:	{' ': 'D'},
		3:	{'#': 'D', 'b': 'E'},
		4:	{' ': 'E', 'b': 'F'},
		5:	{' ': 'F', '#': 'E'},
		6:	{'#': 'F', 'b': 'G'},
		7:	{' ': 'G'},
		8:	{'#': 'G', 'b': 'A'},
		9:	{' ': 'A'},
		10:	{'#': 'A', 'b': 'B'},
		11:	{' ': 'B'}
	}

	_incidental_strings = {
		' ' : ['', '', ''],
		'b' : [CHAR_FLAT_ASCII, CHAR_FLAT_UNICODE, ' flat '],
		'#' : [CHAR_SHARP_ASCII, CHAR_SHARP_UNICODE, ' sharp ']
	}

	_incidental_equiv = {
		' '					: ' ',
		'b'					: 'b',
		CHAR_FLAT_UNICODE	: 'b',
		'flat'				: 'b',
		'#'					: '#',
		CHAR_SHARP_UNICODE	: '#',
		'sharp'				: '#'
	}

	_name_reg = re.compile(
		'([ABCDEFG])' + \
		'[\s\-\.]*' + \
		'([\u266D|\u266F|#|b|sharp|flat])*' + \
		'[\s\.]*' + \
		'(\-)?(\d)?',
		re.IGNORECASE
	)
	_float_reg = re.compile('^(\d)*\.(\d)*$')
	_int_reg = re.compile('^(\d)+$')

	INCIDENTAL_ASCII = 0
	INCIDENTAL_UNICODE = 1
	INCIDENTAL_NAMES = 2

	# Set these using Note.<prop> to override for all new Note instances:
	lcase_name = False
	incidentals_style = INCIDENTAL_ASCII
	prefer_flats = False

	def __init__(self, val):
		if isinstance(val, int):
			self.pitch = val
		elif isinstance(val, float):
			self.pitch = Note.nearest_pitch(val)
		else:
			if self._float_reg.match(val):
				self.pitch = Note.nearest_pitch(float(val))
			elif self._int_reg.match(val):
				self.pitch = int(val)
			else:
				m = self._name_reg.match(val)
				if m is None:
					raise ValueError()
				letter, incid, neg, octave = m.groups()
				if octave is None:
					self.__octave = 3
				elif neg == '1':
					if octave == '1':
						self.__octave = -1
					else:
						raise ValueError('Octave cannot be less than -1')
				else:
					self.__octave = int(octave)
					if self.__octave > 9:
						raise ValueError('Octave cannot be greater than 9')
				if incid is None:
					incid = ' '
				else:
					incid = self._incidental_equiv[incid] \
						if incid in self._incidental_equiv \
						else self._incidental_equiv[incid.lower()]
				self.__note_value = self._name_values[letter.upper()][incid]
				self.__pitch = self.__note_value + (self.__octave + 1) * 12

	def __str__(self):
		pl = self._pitch_values[self.__note_value]
		if ' ' in pl:
			name = pl[' ']
			incid = ' '
		elif self.prefer_flats:
			name = pl['b']
			incid = 'b'
		else:
			name = pl['#']
			incid = '#'
		if self.lcase_name:
			name = name.lower()
		incid = self._incidental_strings[incid][self.incidentals_style]
		return f"{name}{incid}{self.octave}"

	def __int__(self):
		return self.__pitch

	@property
	def name(self):
		return self.__str__()

	@property
	def pitch(self):
		return self.__pitch

	@pitch.setter
	def pitch(self, val):
		self.__pitch = int(val)
		self.__octave = floor(self.__pitch / 12) - 1
		self.__note_value = self.__pitch % 12

	@property
	def interval_above_c(self):
		"""
		Returns the number of half-steps above note "C" in this Note's octave.
		"""
		return self.__note_value

	@property
	def octave(self):
		"""
		Returns this Note's octave.
		"""
		return self.__octave

	@property
	def frequency(self):
		return NOTE_FREQUENCIES[self.__pitch]

	@classmethod
	def nearest_pitch(cls, frequency):
		pos = bisect_left(NOTE_FREQUENCIES, frequency)
		if pos == len(NOTE_FREQUENCIES):
			return len(NOTE_FREQUENCIES)
		elif pos == 0:
			return 0
		diff_a = abs(frequency - NOTE_FREQUENCIES[pos - 1])
		diff_b = abs(frequency - NOTE_FREQUENCIES[pos])
		return pos if diff_b < diff_a else pos - 1

	@classmethod
	def nearest_to(cls, frequency):
		return Note(cls.nearest_pitch(frequency))


#  end midi_notes/__init__.py
