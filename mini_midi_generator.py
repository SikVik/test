import argparse
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List

PPQ = 480


@dataclass
class MidiEvent:
    tick: int
    on: bool
    note: int
    velocity: int
    channel: int


def var_len(value: int) -> bytes:
    """Encode an integer as a MIDI variable-length quantity."""
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.insert(0, (value & 0x7F) | 0x80)
        value >>= 7
    return bytes(out)


def note_name_to_midi(name: str) -> int:
    names = {
        "C": 0,
        "C#": 1,
        "Db": 1,
        "D": 2,
        "D#": 3,
        "Eb": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "Gb": 6,
        "G": 7,
        "G#": 8,
        "Ab": 8,
        "A": 9,
        "A#": 10,
        "Bb": 10,
        "B": 11,
    }
    name = name.strip()
    if len(name) < 2:
        raise ValueError(f"Invalid note name: {name}")

    pitch = name[:-1]
    octave = int(name[-1])
    if pitch not in names:
        raise ValueError(f"Invalid pitch: {pitch}")
    return 12 * (octave + 1) + names[pitch]


def build_scale(root: str, scale_type: str) -> List[int]:
    major_intervals = [0, 2, 4, 5, 7, 9, 11]
    minor_intervals = [0, 2, 3, 5, 7, 8, 10]
    intervals = major_intervals if scale_type == "major" else minor_intervals

    root_midi = note_name_to_midi(root)
    return [root_midi + i for i in intervals]


def triad(scale: List[int], degree: int) -> List[int]:
    i = (degree - 1) % 7
    return [scale[i], scale[(i + 2) % 7], scale[(i + 4) % 7]]


def choose_progression(scale_type: str) -> List[int]:
    options = {
        "major": [[1, 5, 6, 4], [1, 4, 5, 1], [6, 4, 1, 5]],
        "minor": [[1, 6, 3, 7], [1, 7, 6, 7], [1, 4, 5, 1]],
    }
    return random.choice(options[scale_type])


def generate_events(
    key: str,
    scale_type: str,
    bars: int,
    tempo_bpm: int,
    seed: int | None,
) -> List[MidiEvent]:
    if seed is not None:
        random.seed(seed)

    scale = build_scale(key, scale_type)
    progression = choose_progression(scale_type)
    bar_ticks = PPQ * 4
    events: List[MidiEvent] = []

    for bar in range(bars):
        chord_degree = progression[bar % len(progression)]
        chord = [n + 48 - scale[0] for n in triad(scale, chord_degree)]
        chord_start = bar * bar_ticks
        chord_end = chord_start + bar_ticks

        for n in chord:
            events.append(MidiEvent(chord_start, True, n, 68, 0))
            events.append(MidiEvent(chord_end, False, n, 0, 0))

        step_ticks = PPQ // 2
        for step in range(8):
            tick = chord_start + step * step_ticks
            duration = random.choice([PPQ // 2, PPQ, PPQ // 4])
            end_tick = min(chord_end, tick + duration)

            if random.random() < 0.25:
                continue

            note_source = random.choice(chord + [n + 60 - scale[0] for n in scale])
            note = max(48, min(84, note_source + random.choice([-12, 0, 0, 12])))
            velocity = random.randint(72, 108)
            events.append(MidiEvent(tick, True, note, velocity, 1))
            events.append(MidiEvent(end_tick, False, note, 0, 1))

    return sorted(events, key=lambda e: (e.tick, 0 if not e.on else 1, e.note))


def write_midi(path: Path, tempo_bpm: int, events: List[MidiEvent]) -> None:
    tempo = int(60_000_000 / tempo_bpm)
    track = bytearray()

    track += var_len(0) + bytes([0xFF, 0x51, 0x03]) + tempo.to_bytes(3, "big")
    track += var_len(0) + bytes([0xC0, 0x00])  # piano program
    track += var_len(0) + bytes([0xC1, 0x40])  # synth lead for melody

    last_tick = 0
    for e in events:
        delta = e.tick - last_tick
        status = 0x90 if e.on else 0x80
        track += var_len(delta) + bytes([status | (e.channel & 0x0F), e.note & 0x7F, e.velocity & 0x7F])
        last_tick = e.tick

    track += var_len(PPQ) + bytes([0xFF, 0x2F, 0x00])

    data = bytearray()
    data += b"MThd"
    data += (6).to_bytes(4, "big")
    data += (0).to_bytes(2, "big")  # format 0
    data += (1).to_bytes(2, "big")  # one track
    data += PPQ.to_bytes(2, "big")

    data += b"MTrk"
    data += len(track).to_bytes(4, "big")
    data += track

    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a mini MIDI chord/melody idea.")
    parser.add_argument("--key", default="C4", help="Root note, e.g. C4, D#3, Bb3")
    parser.add_argument("--scale", choices=["major", "minor"], default="major")
    parser.add_argument("--bars", type=int, default=8, help="Number of bars to generate")
    parser.add_argument("--tempo", type=int, default=110, help="Tempo in BPM")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for repeatable output")
    parser.add_argument("--out", default="mini_generator.mid", help="Output MIDI file path")
    args = parser.parse_args()

    events = generate_events(args.key, args.scale, args.bars, args.tempo, args.seed)
    out_path = Path(args.out)
    write_midi(out_path, args.tempo, events)

    print(f"Generated {out_path} ({args.bars} bars, {args.scale} in {args.key}, {args.tempo} BPM)")


if __name__ == "__main__":
    main()
