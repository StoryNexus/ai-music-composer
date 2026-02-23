#!/usr/bin/env python3
"""Example: Advanced JSON composition for LLM integration"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from midi_composer import create_from_json

def main():
    print("Advanced JSON examples...\n")

    lofi_spec = {
        "tempo": 85, "time_signature": [4, 4],
        "key": "A", "scale": "MINOR", "octave": 3,
        "tracks": [
            {"type": "chord_progression", "progression": [1, 6, 4, 5],
             "duration_per_chord": 4.0, "instrument": "rhodes"},
            {"type": "bass", "pattern": [[1,2],[1,2],[6,2],[6,2],[4,2],[4,2],[5,2],[5,2]],
             "octave": 2, "instrument": "electric_bass_finger"},
            {"type": "drums", "pattern": {"kick": [0, 2.5], "snare": [1, 3],
             "closed_hihat": [0,.5,1,1.5,2,2.5,3,3.5]}, "measures": 4}
        ]
    }
    composer = create_from_json(json.dumps(lofi_spec))
    composer.export_to_midi("advanced_lofi.mid")

    jazz_spec = {
        "tempo": 140, "time_signature": [4, 4],
        "key": "C", "scale": "MAJOR", "octave": 3,
        "tracks": [
            {"type": "chord_progression", "progression": [2, 5, 1],
             "duration_per_chord": 4.0, "instrument": "acoustic_grand_piano"},
            {"type": "bass", "pattern": [[2,1],[4,1],[6,1],[7,1],[5,1],[7,1],[2,1],[4,1],[1,1],[3,1],[5,1],[7,1]],
             "octave": 2, "instrument": "acoustic_bass"},
        ]
    }
    composer = create_from_json(json.dumps(jazz_spec))
    composer.export_to_midi("advanced_jazz.mid")
    print("Done! Modify these JSON specs to experiment.")

if __name__ == "__main__": main()
