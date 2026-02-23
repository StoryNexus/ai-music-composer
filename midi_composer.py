"""
MIDI Composer - AI-Powered Music Generation
Converts natural language musical descriptions into MIDI files
"""

from midiutil import MIDIFile
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import random


class ScaleType(Enum):
    """Musical scale types"""
    MAJOR = [0, 2, 4, 5, 7, 9, 11]
    MINOR = [0, 2, 3, 5, 7, 8, 10]
    HARMONIC_MINOR = [0, 2, 3, 5, 7, 8, 11]
    MELODIC_MINOR = [0, 2, 3, 5, 7, 9, 11]
    PENTATONIC_MAJOR = [0, 2, 4, 7, 9]
    PENTATONIC_MINOR = [0, 3, 5, 7, 10]
    BLUES = [0, 3, 5, 6, 7, 10]
    DORIAN = [0, 2, 3, 5, 7, 9, 10]
    PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]
    LYDIAN = [0, 2, 4, 6, 7, 9, 11]
    MIXOLYDIAN = [0, 2, 4, 5, 7, 9, 10]
    LOCRIAN = [0, 1, 3, 5, 6, 8, 10]
    WHOLE_TONE = [0, 2, 4, 6, 8, 10]
    CHROMATIC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class ChordQuality(Enum):
    """Chord qualities and their intervals"""
    MAJOR = [0, 4, 7]
    MINOR = [0, 3, 7]
    DIMINISHED = [0, 3, 6]
    AUGMENTED = [0, 4, 8]
    MAJOR7 = [0, 4, 7, 11]
    MINOR7 = [0, 3, 7, 10]
    DOMINANT7 = [0, 4, 7, 10]
    DIMINISHED7 = [0, 3, 6, 9]
    HALF_DIMINISHED7 = [0, 3, 6, 10]
    MINOR_MAJOR7 = [0, 3, 7, 11]
    AUGMENTED7 = [0, 4, 8, 10]
    SUS2 = [0, 2, 7]
    SUS4 = [0, 5, 7]
    ADD9 = [0, 4, 7, 14]
    MAJOR6 = [0, 4, 7, 9]
    MINOR6 = [0, 3, 7, 9]


@dataclass
class Note:
    """Represents a single note"""
    pitch: int
    start_time: float
    duration: float
    velocity: int = 80

    def __post_init__(self):
        self.pitch = max(0, min(127, self.pitch))
        self.velocity = max(0, min(127, self.velocity))


@dataclass
class Track:
    """Represents a MIDI track"""
    name: str
    channel: int
    notes: List[Note]
    program: int = 0

    def __post_init__(self):
        if self.notes is None:
            self.notes = []


class MIDIComposer:
    """Main MIDI composition engine"""

    INSTRUMENTS = {
        'acoustic_grand_piano': 0, 'bright_acoustic_piano': 1,
        'electric_grand_piano': 2, 'electric_piano': 4, 'rhodes': 4,
        'wurlitzer': 5, 'vibraphone': 11, 'marimba': 12, 'xylophone': 13,
        'drawbar_organ': 16, 'hammond': 16, 'rock_organ': 18,
        'acoustic_guitar_nylon': 24, 'acoustic_guitar_steel': 25,
        'electric_guitar_jazz': 26, 'electric_guitar_clean': 27,
        'electric_guitar_muted': 28, 'acoustic_bass': 32,
        'electric_bass_finger': 33, 'electric_bass_pick': 34,
        'fretless_bass': 35, 'slap_bass': 36, 'synth_bass_1': 38,
        'synth_bass_2': 39, 'violin': 40, 'viola': 41, 'cello': 42,
        'contrabass': 43, 'string_ensemble': 48, 'choir_aahs': 52,
        'voice_oohs': 53, 'trumpet': 56, 'trombone': 57, 'tuba': 58,
        'french_horn': 60, 'brass_section': 61, 'soprano_sax': 64,
        'alto_sax': 65, 'tenor_sax': 66, 'baritone_sax': 67,
        'clarinet': 71, 'synth_lead_square': 80, 'synth_lead_sawtooth': 81,
        'synth_lead_calliope': 82, 'synth_pad_new_age': 88,
        'synth_pad_warm': 89, 'synth_pad_polysynth': 90,
        'synth_pad_choir': 91, 'synth_pad_bowed': 92,
        'synth_pad_metallic': 93,
    }

    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def __init__(self, tempo: int = 120, time_signature: Tuple[int, int] = (4, 4)):
        self.tempo = tempo
        self.time_signature = time_signature
        self.tracks: List[Track] = []

    def note_name_to_midi(self, note_name: str, octave: int = 4) -> int:
        note_name = note_name.replace('m', '').strip().upper()
        flat_map = {'DB': 'C#', 'EB': 'D#', 'GB': 'F#', 'AB': 'G#', 'BB': 'A#'}
        if note_name in flat_map:
            note_name = flat_map[note_name]
        if note_name not in self.NOTE_NAMES:
            raise ValueError(f"Invalid note name: {note_name}")
        note_index = self.NOTE_NAMES.index(note_name)
        midi_number = (octave + 1) * 12 + note_index
        return max(0, min(127, midi_number))

    def get_scale_notes(self, root: int, scale_type: ScaleType, octaves: int = 2) -> List[int]:
        notes = []
        for octave in range(octaves):
            for interval in scale_type.value:
                note = root + (octave * 12) + interval
                if 0 <= note <= 127:
                    notes.append(note)
        return notes

    def create_chord(self, root: int, quality: ChordQuality,
                     inversion: int = 0, octave_doubling: bool = False) -> List[int]:
        intervals = quality.value.copy()
        if inversion > 0:
            for _ in range(inversion):
                intervals[0] += 12
                intervals.sort()
        chord = [root + interval for interval in intervals]
        if octave_doubling and len(chord) > 0:
            chord.append(chord[0] + 12)
        return [note for note in chord if 0 <= note <= 127]

    def create_chord_progression(self, root: int, scale_type: ScaleType,
                                progression: List[int], duration_per_chord: float = 4.0) -> Track:
        scale_notes = self.get_scale_notes(root, scale_type, octaves=3)
        notes = []
        current_time = 0.0
        for degree in progression:
            chord_root = scale_notes[degree - 1] if degree <= len(scale_notes) else root
            if scale_type == ScaleType.MAJOR:
                if degree in [1, 4, 5]: quality = ChordQuality.MAJOR
                elif degree in [2, 3, 6]: quality = ChordQuality.MINOR
                elif degree == 7: quality = ChordQuality.DIMINISHED
                else: quality = ChordQuality.MAJOR
            else:
                if degree in [3, 6, 7]: quality = ChordQuality.MAJOR
                elif degree in [1, 4, 5]: quality = ChordQuality.MINOR
                elif degree == 2: quality = ChordQuality.DIMINISHED
                else: quality = ChordQuality.MINOR
            chord = self.create_chord(chord_root, quality)
            for pitch in chord:
                notes.append(Note(pitch=pitch, start_time=current_time,
                                  duration=duration_per_chord, velocity=70))
            current_time += duration_per_chord
        return Track(name="Chord Progression", channel=0, notes=notes,
                     program=self.INSTRUMENTS['electric_piano'])

    def create_melody(self, root: int, scale_type: ScaleType,
                     pattern: List[Tuple[int, float, float]],
                     start_octave: int = 5) -> Track:
        scale_notes = self.get_scale_notes(root, scale_type, octaves=3)
        notes = []
        current_time = 0.0
        for degree, duration, rest in pattern:
            if degree > 0:
                note_index = (degree - 1) % len(scale_notes)
                octave_offset = ((degree - 1) // len(scale_notes)) * 12
                pitch = scale_notes[note_index] + octave_offset
                notes.append(Note(pitch=pitch, start_time=current_time,
                                  duration=duration, velocity=85))
            current_time += duration + rest
        return Track(name="Melody", channel=1, notes=notes,
                     program=self.INSTRUMENTS['synth_lead_sawtooth'])

    def create_bass_line(self, root: int, scale_type: ScaleType,
                        pattern: List[Tuple[int, float]], octave: int = 2) -> Track:
        scale_notes = self.get_scale_notes(root, scale_type, octaves=2)
        bass_notes = [note - 24 for note in scale_notes if note - 24 >= 0]
        notes = []
        current_time = 0.0
        for degree, duration in pattern:
            if degree > 0 and degree <= len(bass_notes):
                pitch = bass_notes[degree - 1]
                notes.append(Note(pitch=pitch, start_time=current_time,
                                  duration=duration, velocity=90))
            current_time += duration
        return Track(name="Bass", channel=2, notes=notes,
                     program=self.INSTRUMENTS['electric_bass_finger'])

    def create_drum_pattern(self, pattern: Dict[str, List[float]],
                           measures: int = 4) -> Track:
        DRUM_MAP = {
            'kick': 36, 'snare': 38, 'closed_hihat': 42, 'open_hihat': 46,
            'crash': 49, 'ride': 51, 'tom_high': 48, 'tom_mid': 47, 'tom_low': 45,
        }
        notes = []
        beats_per_measure = self.time_signature[0]
        for measure in range(measures):
            offset = measure * beats_per_measure
            for drum, hits in pattern.items():
                if drum in DRUM_MAP:
                    pitch = DRUM_MAP[drum]
                    for hit_time in hits:
                        notes.append(Note(pitch=pitch, start_time=offset + hit_time,
                                          duration=0.1, velocity=95))
        return Track(name="Drums", channel=9, notes=notes, program=0)

    def add_track(self, track: Track):
        self.tracks.append(track)

    def export_to_midi(self, filename: str = "output.mid"):
        num_tracks = len(self.tracks)
        midi_file = MIDIFile(num_tracks)
        for track_idx, track in enumerate(self.tracks):
            midi_file.addTrackName(track_idx, 0, track.name)
            midi_file.addTempo(track_idx, 0, self.tempo)
            if track.channel != 9:
                midi_file.addProgramChange(track_idx, track.channel, 0, track.program)
            for note in track.notes:
                midi_file.addNote(track=track_idx, channel=track.channel,
                                  pitch=note.pitch, time=note.start_time,
                                  duration=note.duration, volume=note.velocity)
        with open(filename, 'wb') as f:
            midi_file.writeFile(f)
        print(f"MIDI file saved: {filename}")
        return filename


def create_from_json(json_data: str) -> MIDIComposer:
    data = json.loads(json_data)
    composer = MIDIComposer(tempo=data.get('tempo', 120),
                            time_signature=tuple(data.get('time_signature', [4, 4])))
    key_name = data.get('key', 'C')
    octave = data.get('octave', 4)
    root = composer.note_name_to_midi(key_name, octave)
    scale_name = data.get('scale', 'MAJOR')
    scale_type = ScaleType[scale_name]
    for track_spec in data.get('tracks', []):
        track_type = track_spec.get('type')
        if track_type == 'chord_progression':
            track = composer.create_chord_progression(
                root=root, scale_type=scale_type,
                progression=track_spec['progression'],
                duration_per_chord=track_spec.get('duration_per_chord', 4.0))
            if 'instrument' in track_spec:
                track.program = composer.INSTRUMENTS.get(
                    track_spec['instrument'], composer.INSTRUMENTS['electric_piano'])
            composer.add_track(track)
        elif track_type == 'melody':
            track = composer.create_melody(
                root=root, scale_type=scale_type,
                pattern=track_spec['pattern'],
                start_octave=track_spec.get('octave', 5))
            if 'instrument' in track_spec:
                track.program = composer.INSTRUMENTS.get(
                    track_spec['instrument'], composer.INSTRUMENTS['synth_lead_sawtooth'])
            composer.add_track(track)
        elif track_type == 'bass':
            track = composer.create_bass_line(
                root=root, scale_type=scale_type,
                pattern=track_spec['pattern'],
                octave=track_spec.get('octave', 2))
            if 'instrument' in track_spec:
                track.program = composer.INSTRUMENTS.get(
                    track_spec['instrument'], composer.INSTRUMENTS['electric_bass_finger'])
            composer.add_track(track)
        elif track_type == 'drums':
            track = composer.create_drum_pattern(
                pattern=track_spec['pattern'],
                measures=track_spec.get('measures', 4))
            composer.add_track(track)
    return composer


if __name__ == "__main__":
    composer = MIDIComposer(tempo=120, time_signature=(4, 4))
    root = composer.note_name_to_midi('C', 4)
    chord_track = composer.create_chord_progression(
        root=root, scale_type=ScaleType.MAJOR,
        progression=[1, 4, 5, 1], duration_per_chord=4.0)
    composer.add_track(chord_track)
    composer.export_to_midi("example.mid")
