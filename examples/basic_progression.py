#!/usr/bin/env python3
"""Example: Basic I-IV-V-I chord progression in C major"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from midi_composer import MIDIComposer, ScaleType

def main():
    print("Creating I-IV-V-I in C major...")
    composer = MIDIComposer(tempo=120)
    root = composer.note_name_to_midi('C', 4)
    track = composer.create_chord_progression(
        root=root, scale_type=ScaleType.MAJOR,
        progression=[1, 4, 5, 1], duration_per_chord=4.0)
    track.program = composer.INSTRUMENTS['rhodes']
    track.name = "Chords"
    composer.add_track(track)
    composer.export_to_midi("basic_progression.mid")
    print("Done!")

if __name__ == "__main__": main()
