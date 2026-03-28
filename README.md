# Music Player App

This repository contains:

- A simple Python script to play an audio file using `pygame`.
- A mini MIDI chord/melody generator that creates a `.mid` file with basic harmony + lead notes.

## Requirements

- Python 3
- `pygame` library for the player. Install with:

```bash
pip install pygame
```

## Play Audio File

Run the script with the path to an audio file (MP3 or WAV):

```bash
python play_music.py path/to/your/song.mp3
```

Press `Ctrl+C` to stop playback.

## Generate a Mini MIDI Idea

Create a short random MIDI progression + melody:

```bash
python mini_midi_generator.py --key C4 --scale major --bars 8 --tempo 110 --out idea.mid
```

Useful options:

- `--key`: root note, e.g. `C4`, `D#3`, `Bb3`
- `--scale`: `major` or `minor`
- `--bars`: number of bars to create
- `--tempo`: BPM
- `--seed`: fixed random seed for reproducible output
- `--out`: output MIDI file path
