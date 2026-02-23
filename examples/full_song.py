#!/usr/bin/env python3
"""Example: Complete song with chords, melody, bass, drums"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from midi_composer import MIDIComposer, ScaleType

def main():
    print("Creating complete song...")
    composer = MIDIComposer(tempo=110)
    root = composer.note_name_to_midi('A', 3)

    chords = composer.create_chord_progression(
        root=root, scale_type=ScaleType.MINOR,
        progression=[1, 6, 3, 7], duration_per_chord=4.0)
    chords.program = composer.INSTRUMENTS['electric_piano']
    chords.name = "Chords"
    composer.add_track(chords)

    melody = composer.create_melody(root=root, scale_type=ScaleType.MINOR,
        pattern=[(1,1,0),(3,.5,0),(5,.5,0),(3,1,1),(6,1,0),(8,.5,0),(6,.5,0),(4,2,0),
                 (3,1.5,0),(5,.5,0),(3,1,0),(1,1,0),(7,2,0),(5,1,0),(3,1,0)])
    melody.program = composer.INSTRUMENTS['synth_lead_sawtooth']
    melody.name = "Melody"
    composer.add_track(melody)

    bass = composer.create_bass_line(root=root, scale_type=ScaleType.MINOR,
        pattern=[[1,2],[1,2],[6,2],[6,2],[3,2],[3,2],[7,2],[7,2]], octave=2)
    bass.program = composer.INSTRUMENTS['electric_bass_finger']
    bass.name = "Bass"
    composer.add_track(bass)

    drums = composer.create_drum_pattern(
        {'kick': [0,2], 'snare': [1,3],
         'closed_hihat': [0,.5,1,1.5,2,2.5,3,3.5]}, measures=4)
    drums.name = "Drums"
    composer.add_track(drums)

    composer.export_to_midi("complete_song.mid")
    print("Done! Tracks: Chords, Melody, Bass, Drums")

if __name__ == "__main__": main()
