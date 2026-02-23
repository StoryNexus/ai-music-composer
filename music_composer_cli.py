#!/usr/bin/env python3
"""AI Music Composer - Command Line Interface"""

import sys, os, json, re
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from midi_composer import MIDIComposer, ScaleType
from llm_interface import LLMComposerInterface, create_quick_composition, MusicTheoryHelper

try:
    from sheet_music_parser import SheetMusicParser, SimpleMusicXMLParser
    SHEET_MUSIC_AVAILABLE = True
except ImportError:
    SHEET_MUSIC_AVAILABLE = False

try:
    from lilypond_generator import create_lilypond_from_composer, LilyPondGenerator
    LILYPOND_AVAILABLE = True
except ImportError:
    LILYPOND_AVAILABLE = False


class Colors:
    HEADER = '\033[95m'; BLUE = '\033[94m'; CYAN = '\033[96m'
    GREEN = '\033[92m'; YELLOW = '\033[93m'; RED = '\033[91m'
    ENDC = '\033[0m'; BOLD = '\033[1m'


def print_banner():
    print(f"""
{Colors.CYAN}======================================================
         AI MUSIC COMPOSER - CLI v1.0
     Turn Your Musical Ideas Into MIDI Files
======================================================{Colors.ENDC}
""")


def print_menu():
    return input(f"""
{Colors.BOLD}MAIN MENU:{Colors.ENDC}

{Colors.GREEN}1.{Colors.ENDC} Quick Composition (Genre Templates)
{Colors.GREEN}2.{Colors.ENDC} Natural Language Composition
{Colors.GREEN}3.{Colors.ENDC} Advanced Composition (Custom JSON)
{Colors.GREEN}4.{Colors.ENDC} Convert Sheet Music to MIDI
{Colors.GREEN}5.{Colors.ENDC} Generate LilyPond Notation
{Colors.GREEN}6.{Colors.ENDC} View LLM System Prompt
{Colors.GREEN}7.{Colors.ENDC} Help & Examples
{Colors.GREEN}8.{Colors.ENDC} Exit

{Colors.YELLOW}Your choice:{Colors.ENDC} """)


def quick_composition():
    print(f"\n{Colors.CYAN}QUICK COMPOSITION{Colors.ENDC}\n")
    genres = ['lofi', 'jazz', 'funk', 'ambient', 'pop', 'rock']
    for i, g in enumerate(genres, 1): print(f"  {i}. {g.capitalize()}")
    try:
        genre = genres[int(input(f"\n{Colors.YELLOW}Select genre:{Colors.ENDC} ").strip()) - 1]
    except (ValueError, IndexError):
        print(f"{Colors.RED}Invalid choice{Colors.ENDC}"); return
    key = input(f"{Colors.YELLOW}Key (e.g., C, Am, F#):{Colors.ENDC} ").strip() or 'C'
    tempo = input(f"{Colors.YELLOW}Tempo (BPM, Enter for default):{Colors.ENDC} ").strip()
    tempo = int(tempo) if tempo else None
    try:
        composer = create_quick_composition(genre, key, tempo)
        filename = f"{genre}_{key.replace('#', 'sharp')}_{composer.tempo}bpm.mid"
        composer.export_to_midi(filename)
        print(f"{Colors.GREEN}Success! Created: {filename}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.ENDC}")


def natural_language_composition():
    print(f"\n{Colors.CYAN}NATURAL LANGUAGE COMPOSITION{Colors.ENDC}\n")
    print("Describe the music you want to create.")
    print('Example: "A melancholic lo-fi track at 85 BPM with Rhodes piano"\n')
    description = input(f"{Colors.YELLOW}Your description:{Colors.ENDC} ").strip()
    if not description: return
    choice = input(f"{Colors.YELLOW}Generate best-guess? (y/n):{Colors.ENDC} ").strip().lower()
    if choice == 'y':
        desc_lower = description.lower()
        genre = 'pop'
        for g in ['lofi', 'jazz', 'funk', 'ambient', 'rock']:
            if g in desc_lower: genre = g; break
        key = 'C'
        for note in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
            if f' {note} ' in f' {description} ' or f' {note}m' in desc_lower:
                key = note; break
        tempo = None
        m = re.search(r'(\d+)\s*bpm', desc_lower)
        if m: tempo = int(m.group(1))
        try:
            composer = create_quick_composition(genre, key, tempo)
            composer.export_to_midi(f"custom_{genre}.mid")
            print(f"{Colors.GREEN}Success!{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
    else:
        print("\nCopy the system prompt (Option 6) to ChatGPT/Claude,")
        print("describe your music, then use Option 3 with the JSON result.")


def advanced_composition():
    print(f"\n{Colors.CYAN}ADVANCED COMPOSITION (JSON){Colors.ENDC}\n")
    print("1. Paste JSON directly (end with END)")
    print("2. Provide a JSON file path\n")
    choice = input(f"{Colors.YELLOW}Choice:{Colors.ENDC} ").strip()
    json_str = None
    if choice == '1':
        print("Paste JSON (type END when done):")
        lines = []
        while True:
            line = input()
            if line.strip() == 'END': break
            lines.append(line)
        json_str = '\n'.join(lines)
    elif choice == '2':
        try:
            with open(input("File path: ").strip(), 'r') as f:
                json_str = f.read()
        except Exception as e:
            print(f"Error: {e}"); return
    if not json_str: return
    try:
        json.loads(json_str)
        from midi_composer import create_from_json
        composer = create_from_json(json_str)
        filename = input("Output filename (default: output.mid): ").strip() or "output.mid"
        composer.export_to_midi(filename)
        print(f"{Colors.GREEN}Created: {filename}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.ENDC}")


def sheet_music_conversion():
    if not SHEET_MUSIC_AVAILABLE:
        print("Sheet music conversion requires: pip install music21")
        print("Also requires Audiveris for image/PDF conversion.")
        return
    print("Sheet music conversion available. Use SheetMusicParser class.")


def lilypond_generation():
    if not LILYPOND_AVAILABLE:
        print("LilyPond generation requires lilypond_generator.py in same directory.")
        return
    print(f"\n{Colors.CYAN}LILYPOND NOTATION{Colors.ENDC}\n")
    genres = ['lofi', 'jazz', 'funk', 'ambient', 'pop', 'rock']
    for i, g in enumerate(genres, 1): print(f"  {i}. {g.capitalize()}")
    try:
        genre = genres[int(input("Select genre: ").strip()) - 1]
    except (ValueError, IndexError):
        print("Invalid choice"); return
    key = input("Key: ").strip() or 'C'
    tempo = input("Tempo (Enter for default): ").strip()
    tempo = int(tempo) if tempo else None
    title = input("Title: ").strip() or f"{genre.capitalize()} Composition"
    composer = create_quick_composition(genre, key, tempo)
    lily = create_lilypond_from_composer(composer, title=title)
    filename = f"{genre}_{key.replace('#', 'sharp')}.ly"
    lily.generate_lilypond_file(filename)
    print(f"To compile: lilypond {filename}")


def main():
    print_banner()
    while True:
        try:
            choice = print_menu()
            if choice == '1': quick_composition()
            elif choice == '2': natural_language_composition()
            elif choice == '3': advanced_composition()
            elif choice == '4': sheet_music_conversion()
            elif choice == '5': lilypond_generation()
            elif choice == '6': print(LLMComposerInterface.get_system_prompt())
            elif choice == '7':
                print("\nStart with Option 1 (Quick Composition).")
                print("Genres: lofi, jazz, funk, ambient, pop, rock")
                print("Generated MIDIs are starting points - import into DAW!")
            elif choice == '8':
                print("Goodbye!"); break
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
        except KeyboardInterrupt:
            print("\nGoodbye!"); break
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
