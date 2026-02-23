"""
LilyPond Generator - Converts musical structures to LilyPond notation
"""
from typing import List, Dict, Optional
from midi_composer import Note, Track
import re


class LilyPondGenerator:
    NOTE_NAMES = ['c', 'cis', 'd', 'dis', 'e', 'f', 'fis', 'g', 'gis', 'a', 'ais', 'b']
    DURATION_MAP = {4.0: '1', 3.0: '2.', 2.0: '2', 1.5: '4.', 1.0: '4',
                    0.75: '8.', 0.5: '8', 0.25: '16', 0.125: '32'}
    INSTRUMENT_NAMES = {
        0: 'acoustic grand', 4: 'electric piano', 32: 'acoustic bass',
        33: 'electric bass (finger)', 36: 'slap bass', 40: 'violin',
        48: 'string ensemble', 56: 'trumpet', 66: 'tenor sax',
        80: 'lead 1 (square)', 81: 'lead 2 (sawtooth)', 89: 'pad 2 (warm)',
    }

    def __init__(self, title="Composition", composer="AI Music Composer"):
        self.title = title
        self.composer = composer
        self.tempo = 120
        self.time_signature = (4, 4)
        self.tracks: List[Dict] = []

    def midi_to_lilypond_note(self, midi_number, duration=1.0, is_rest=False):
        if is_rest:
            return f"r{self.DURATION_MAP.get(duration, '4')}"
        note_class = midi_number % 12
        octave = (midi_number // 12) - 4
        note_name = self.NOTE_NAMES[note_class]
        if octave > 0: note_name += "\'" * octave
        elif octave < 0: note_name += "," * abs(octave)
        return f"{note_name}{self.DURATION_MAP.get(duration, '4')}"

    def notes_to_lilypond(self, notes, voice_name="melody"):
        if not notes: return ""
        sorted_notes = sorted(notes, key=lambda n: n.start_time)
        lilypond_notes = []
        current_time = 0.0
        for note in sorted_notes:
            if note.start_time > current_time:
                lilypond_notes.append(self.midi_to_lilypond_note(0, note.start_time - current_time, True))
            lilypond_notes.append(self.midi_to_lilypond_note(note.pitch, note.duration))
            current_time = note.start_time + note.duration
        result = []
        for i in range(0, len(lilypond_notes), 8):
            result.append("  " + " ".join(lilypond_notes[i:i+8]))
        return "\n".join(result)

    def chord_notes_to_lilypond(self, notes):
        if not notes: return ""
        time_groups = {}
        for note in notes:
            time_groups.setdefault(note.start_time, []).append(note)
        lilypond_output = []
        current_time = 0.0
        for time in sorted(time_groups.keys()):
            if time > current_time:
                lilypond_output.append(self.midi_to_lilypond_note(0, time - current_time, True))
            chord_notes = time_groups[time]
            if len(chord_notes) == 1:
                note = chord_notes[0]
                lilypond_output.append(self.midi_to_lilypond_note(note.pitch, note.duration))
                current_time = time + note.duration
            else:
                chord_notes.sort(key=lambda n: n.pitch)
                duration = chord_notes[0].duration
                parts = []
                for n in chord_notes:
                    parts.append(self.midi_to_lilypond_note(n.pitch, 0)[:-1])
                chord_str = "<" + " ".join(parts) + ">" + self.DURATION_MAP.get(duration, '4')
                lilypond_output.append(chord_str)
                current_time = time + duration
        result = []
        for i in range(0, len(lilypond_output), 4):
            result.append("  " + " ".join(lilypond_output[i:i+4]))
        return "\n".join(result)

    def add_track_from_track_object(self, track: Track):
        self.tracks.append({
            'name': track.name, 'notes': track.notes,
            'instrument': track.program, 'is_drum': (track.channel == 9)
        })

    def set_tempo(self, tempo): self.tempo = tempo
    def set_time_signature(self, num, den): self.time_signature = (num, den)

    def generate_lilypond_file(self, filename="output.ly"):
        output = ['\\version "2.24.0"', '', '\\header {',
                  f'  title = "{self.title}"', f'  composer = "{self.composer}"', '}', '']
        for track in self.tracks:
            track_var = re.sub(r'[^a-z0-9_]', '', track['name'].lower().replace(' ', '_').replace('-', '_'))
            output.append(f"{track_var} = {{")
            output.append("  \\clef treble")
            if track['is_drum']:
                output.append("  % Drum track")
            else:
                time_groups = {}
                for note in track['notes']:
                    time_groups.setdefault(note.start_time, []).append(note)
                has_chords = any(len(v) > 1 for v in time_groups.values())
                output.append(self.chord_notes_to_lilypond(track['notes']) if has_chords
                              else self.notes_to_lilypond(track['notes']))
            output.extend(["}", ""])
        output.append("\\score {")
        output.append("  <<")
        for track in self.tracks:
            track_var = re.sub(r'[^a-z0-9_]', '', track['name'].lower().replace(' ', '_').replace('-', '_'))
            inst = self.INSTRUMENT_NAMES.get(track['instrument'], 'piano')
            output.extend(["    \\new Staff {",
                           f'      \\set Staff.instrumentName = "{track["name"]}"',
                           f'      \\set Staff.midiInstrument = "{inst}"',
                           f"      \\{track_var}", "    }"])
        output.extend(["  >>", "  \\layout { }",
                       "  \\midi {", f"    \\tempo 4 = {self.tempo}", "  }", "}"])
        with open(filename, 'w') as f:
            f.write('\n'.join(output))
        print(f"LilyPond file saved: {filename}")
        return filename

    @staticmethod
    def compile_to_pdf(ly_file):
        import subprocess
        from pathlib import Path
        try:
            result = subprocess.run(['lilypond', ly_file], capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return str(Path(ly_file).with_suffix('.pdf'))
        except FileNotFoundError:
            print("LilyPond not found. Install from http://lilypond.org/")
        return None

    @staticmethod
    def compile_to_midi(ly_file):
        import subprocess
        from pathlib import Path
        try:
            result = subprocess.run(['lilypond', '--output=midi', ly_file],
                                    capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return str(Path(ly_file).with_suffix('.midi'))
        except FileNotFoundError:
            print("LilyPond not found. Install from http://lilypond.org/")
        return None


def create_lilypond_from_composer(composer, title="Composition", composer_name="AI Music Composer"):
    lily = LilyPondGenerator(title=title, composer=composer_name)
    lily.set_tempo(composer.tempo)
    lily.set_time_signature(*composer.time_signature)
    for track in composer.tracks:
        lily.add_track_from_track_object(track)
    return lily


def create_installation_guide():
    print("Install LilyPond from: http://lilypond.org/download.html")
    print("Verify: lilypond --version")
