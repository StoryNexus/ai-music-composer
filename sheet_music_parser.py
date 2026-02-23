"""
Sheet Music Parser - Converts sheet music to MIDI using Audiveris
"""
import os, subprocess
from pathlib import Path
from typing import Optional, List, Tuple


class SheetMusicParser:
    def __init__(self, audiveris_path: Optional[str] = None):
        self.audiveris_path = audiveris_path
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.pdf', '.tiff', '.tif']

    def check_dependencies(self) -> Tuple[bool, List[str]]:
        missing = []
        try:
            result = subprocess.run(['audiveris', '-help'], capture_output=True, timeout=5)
            if result.returncode != 0: missing.append('audiveris')
        except (FileNotFoundError, subprocess.TimeoutExpired):
            missing.append('audiveris')
        return len(missing) == 0, missing

    def parse_sheet_music(self, input_file: str, output_midi: Optional[str] = None) -> Optional[str]:
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"Error: File not found: {input_file}"); return None
        installed, missing = self.check_dependencies()
        if not installed:
            print("Error: Audiveris not installed"); return None
        if output_midi is None:
            output_midi = input_path.stem + '.mid'
        try:
            cmd = ['audiveris', '-batch', '-export', '-output',
                   str(Path(output_midi).parent or '.'), str(input_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0 and Path(output_midi).exists():
                return output_midi
            return None
        except Exception as e:
            print(f"Error: {e}"); return None

    def batch_parse(self, input_dir: str, output_dir: str = None) -> List[str]:
        input_path = Path(input_dir)
        output_path = Path(output_dir) if output_dir else input_path
        if not input_path.exists(): return []
        output_path.mkdir(parents=True, exist_ok=True)
        files = []
        for ext in self.supported_formats:
            files.extend(input_path.glob(f"*{ext}"))
        results = []
        for i, file in enumerate(files, 1):
            output_midi = output_path / f"{file.stem}.mid"
            result = self.parse_sheet_music(str(file), str(output_midi))
            if result: results.append(result)
        return results


class SimpleMusicXMLParser:
    def __init__(self):
        try:
            from music21 import converter
            self.converter = converter
            self.available = True
        except ImportError:
            self.available = False

    def musicxml_to_midi(self, musicxml_file: str, output_midi: Optional[str] = None) -> Optional[str]:
        if not self.available: return None
        try:
            score = self.converter.parse(musicxml_file)
            if output_midi is None:
                output_midi = Path(musicxml_file).stem + '.mid'
            score.write('midi', fp=output_midi)
            return output_midi
        except Exception as e:
            print(f"Error: {e}"); return None
