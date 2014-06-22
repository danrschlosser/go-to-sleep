
import subprocess

PLAY = 'afplay'
SOUND_FILE = 'go_to_sleep/go_to_sleep.m4a'

def go_to_sleep():
    subprocess.call([PLAY, SOUND_FILE])

