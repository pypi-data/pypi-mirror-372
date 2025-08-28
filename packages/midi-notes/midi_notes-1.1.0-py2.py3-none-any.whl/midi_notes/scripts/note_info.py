#  midi_notes/scripts/note_info.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Show information / convert format for the given note.
"""
import logging, sys, argparse, re
from midi_notes import Note

def main():
	p = argparse.ArgumentParser()
	p.add_argument('Note', type = str, nargs = 1,
		help = "Numeric midi value, frequency, or note name")
	group = p.add_mutually_exclusive_group()
	group.add_argument('-n', '--name', action="store_true", default = True)
	group.add_argument('-m', '--midi-value', action="store_true")
	group.add_argument('-p', '--pitch', action="store_true", help = 'Same as "--midi-value"')
	group.add_argument('-f', '--frequency', action="store_true")
	p.add_argument('--flats', action="store_true",
		help = 'If note is incidental, print the flat variation')
	p.add_argument("--verbose", "-v", action="store_true",
		help="Show more detailed debug information")
	p.epilog = __doc__
	options = p.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)3d] %(message)s"
	)

	note = options.Note[0]
	if re.match(r'^[0-9]*\.[0-9]*$', note):
		note = Note(float(note))
	elif note.isnumeric():
		note = Note(int(note))
	else:
		note = Note(note)

	note.prefer_flats = options.flats
	if options.midi_value or options.pitch:
		print(note.pitch)
	elif options.frequency:
		print(note.frequency)
	elif options.name:
		print(note.name)


if __name__ == "__main__":
	main()


#  end midi_notes/scripts/note_info.py
