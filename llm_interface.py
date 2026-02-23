"""
LLM Music Composer Interface
Provides a natural language interface for AI assistants to compose music
"""

import json
from typing import Dict, List, Any, Optional
from midi_composer import MIDIComposer, ScaleType, ChordQuality, create_from_json


class LLMComposerInterface:
    """Interface for LLMs to compose music through structured commands"""

    SYSTEM_PROMPT = """
You are a music composition assistant with access to a MIDI generation system.
When a user describes music, generate a JSON specification wrapped in <midi_spec> tags.

AVAILABLE SCALES: MAJOR, MINOR, HARMONIC_MINOR, MELODIC_MINOR,
PENTATONIC_MAJOR, PENTATONIC_MINOR, BLUES, DORIAN, PHRYGIAN, LYDIAN,
MIXOLYDIAN, LOCRIAN, WHOLE_TONE, CHROMATIC

TRACK TYPES:
1. chord_progression: progression (scale degrees), duration_per_chord, instrument
2. melody: pattern ([scale_degree, duration, rest]), octave, instrument
3. bass: pattern ([scale_degree, duration]), octave, instrument
4. drums: pattern ({drum: [hit_times]}), measures

INSTRUMENTS: acoustic_grand_piano, electric_piano, rhodes, wurlitzer,
acoustic_guitar_steel, electric_guitar_clean, acoustic_bass,
electric_bass_finger, slap_bass, synth_bass_1, violin, cello,
string_ensemble, trumpet, trombone, brass_section, alto_sax, tenor_sax,
synth_lead_square, synth_lead_sawtooth, synth_pad_warm, hammond

DRUMS: kick, snare, closed_hihat, open_hihat, crash, ride

Return JSON in <midi_spec>...</midi_spec> tags.
"""

    @staticmethod
    def get_system_prompt() -> str:
        return LLMComposerInterface.SYSTEM_PROMPT

    @staticmethod
    def parse_llm_response(response: str) -> Optional[str]:
        try:
            start = response.find('<midi_spec>')
            end = response.find('</midi_spec>')
            if start != -1 and end != -1:
                json_str = response[start + 11:end].strip()
                json.loads(json_str)
                return json_str
            return None
        except json.JSONDecodeError:
            return None

    @staticmethod
    def generate_from_description(description: str, llm_response: str) -> Optional[str]:
        json_spec = LLMComposerInterface.parse_llm_response(llm_response)
        if not json_spec:
            print("Error: Could not find valid <midi_spec> in LLM response")
            return None
        try:
            composer = create_from_json(json_spec)
            safe_name = "".join(c for c in description[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"{safe_name}.mid"
            composer.export_to_midi(filename)
            return filename
        except Exception as e:
            print(f"Error generating MIDI: {e}")
            return None


class MusicTheoryHelper:
    """Helper functions for music theory concepts"""

    GENRE_TEMPLATES = {
        'lofi': {
            'tempo': (70, 90), 'scale': 'MINOR', 'time_signature': [4, 4],
            'instruments': {'chords': 'rhodes', 'melody': 'electric_piano', 'bass': 'electric_bass_finger'},
            'progression': [1, 6, 4, 5],
        },
        'jazz': {
            'tempo': (120, 180), 'scale': 'DORIAN', 'time_signature': [4, 4],
            'instruments': {'chords': 'acoustic_grand_piano', 'melody': 'tenor_sax', 'bass': 'acoustic_bass'},
            'progression': [2, 5, 1],
        },
        'funk': {
            'tempo': (95, 115), 'scale': 'MINOR', 'time_signature': [4, 4],
            'instruments': {'chords': 'electric_guitar_clean', 'melody': 'trumpet', 'bass': 'slap_bass'},
            'progression': [1, 1, 1, 1],
        },
        'ambient': {
            'tempo': (60, 80), 'scale': 'MAJOR', 'time_signature': [4, 4],
            'instruments': {'chords': 'synth_pad_warm', 'melody': 'synth_pad_choir', 'bass': 'synth_bass_1'},
            'progression': [1, 5, 6, 4],
        },
        'pop': {
            'tempo': (100, 130), 'scale': 'MAJOR', 'time_signature': [4, 4],
            'instruments': {'chords': 'electric_piano', 'melody': 'synth_lead_sawtooth', 'bass': 'electric_bass_finger'},
            'progression': [1, 5, 6, 4],
        },
        'rock': {
            'tempo': (120, 140), 'scale': 'MINOR', 'time_signature': [4, 4],
            'instruments': {'chords': 'electric_guitar_clean', 'melody': 'synth_lead_square', 'bass': 'electric_bass_pick'},
            'progression': [1, 4, 5, 1],
        },
    }

    @staticmethod
    def get_genre_template(genre: str) -> Dict[str, Any]:
        genre = genre.lower()
        if genre in MusicTheoryHelper.GENRE_TEMPLATES:
            return MusicTheoryHelper.GENRE_TEMPLATES[genre].copy()
        return {
            'tempo': (120, 140), 'scale': 'MAJOR', 'time_signature': [4, 4],
            'instruments': {'chords': 'electric_piano', 'melody': 'synth_lead_sawtooth', 'bass': 'electric_bass_finger'},
            'progression': [1, 4, 5, 1],
        }

    @staticmethod
    def create_syncopated_rhythm(measures: int = 4) -> Dict[str, List[float]]:
        pattern = {'kick': [], 'snare': [], 'closed_hihat': []}
        for measure in range(measures):
            offset = measure * 4
            pattern['kick'].extend([offset, offset + 1.5, offset + 2.5])
            pattern['snare'].extend([offset + 1, offset + 3])
            for i in range(16):
                pattern['closed_hihat'].append(offset + i * 0.25)
        return pattern


def create_quick_composition(genre: str, key: str = 'C',
                            tempo: Optional[int] = None) -> MIDIComposer:
    """Quick composition helper using genre templates"""
    template = MusicTheoryHelper.get_genre_template(genre)
    if tempo is None:
        tempo_range = template['tempo']
        tempo = (tempo_range[0] + tempo_range[1]) // 2
    composer = MIDIComposer(tempo=tempo, time_signature=template['time_signature'])
    root = composer.note_name_to_midi(key, 3)
    scale_type = ScaleType[template['scale']]

    chord_track = composer.create_chord_progression(
        root=root, scale_type=scale_type,
        progression=template['progression'], duration_per_chord=4.0)
    chord_track.program = composer.INSTRUMENTS[template['instruments']['chords']]
    composer.add_track(chord_track)

    bass_pattern = [[degree, 4.0] for degree in template['progression']]
    bass_track = composer.create_bass_line(
        root=root, scale_type=scale_type, pattern=bass_pattern, octave=2)
    bass_track.program = composer.INSTRUMENTS[template['instruments']['bass']]
    composer.add_track(bass_track)

    if genre in ['funk', 'lofi', 'pop', 'rock']:
        if genre == 'funk':
            drum_pattern = MusicTheoryHelper.create_syncopated_rhythm(4)
        else:
            drum_pattern = {
                'kick': [0, 2], 'snare': [1, 3],
                'closed_hihat': [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5],
            }
        drum_track = composer.create_drum_pattern(drum_pattern, measures=4)
        composer.add_track(drum_track)
    return composer


if __name__ == "__main__":
    print("Creating quick lo-fi composition...")
    composer = create_quick_composition('lofi', key='Am', tempo=85)
    composer.export_to_midi('lofi_example.mid')
    print("Done!")
