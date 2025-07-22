import argparse
import pygame
import time
import os


def main(audio_file):
    if not os.path.isfile(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    try:
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple music player using pygame")
    parser.add_argument("audio_file", help="Path to audio file (mp3 or wav)")
    args = parser.parse_args()
    main(args.audio_file)
