#!/usr/bin/env python3
"""Example: Batch generation for Suno workflow"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_interface import create_quick_composition

def main():
    print("Generating batch variations...\n")
    configs = [
        ('lofi', 'Am', 80), ('lofi', 'A', 85), ('lofi', 'Am', 90),
        ('funk', 'E', 100), ('funk', 'Em', 110), ('funk', 'E', 105),
    ]
    for genre, key, tempo in configs:
        key_safe = key.replace('#', 'sharp').replace('m', 'min')
        filename = f"{genre}_{key_safe}_{tempo}bpm.mid"
        composer = create_quick_composition(genre, key, tempo)
        composer.export_to_midi(filename)
    print("\nDone! Import all into your DAW and find the best ideas.")

if __name__ == "__main__": main()
