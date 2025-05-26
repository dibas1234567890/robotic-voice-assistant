#built-in imports
import base64 
import json
import os 
import queue
import socket
import subprocess
import threading
import time 
import pyaudio
import socks
import websocket
from colorama import Fore

#custom importss
from realime_config import CustomRealtimeConfig

config = CustomRealtimeConfig()

socket.socket = socks.socksocket

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY: 
    raise ValueError("API KEY MISSING")

WS_URL = os.getenv("REALTIME_WS_URL")
if not WS_URL: 
    raise ValueError("WS_URL not initialized properly")

chunk_size = config.CHUNK_SIZE
rate = config.RATE
format = config.FORMAT

audio_buffer = bytearray()

mic_queue = queue.Queue()

stop_event = threading.Event()

mic_on_at = 0 
mic_active = None
REENGAGE_DELAY_MS = config.REENGAGE_DELAY_MS


def clear_audio_buffer():
    global audio_buffer 
    audio_buffer = bytearray()
    print(Fore.GREEN + "Audio Buffer cleaned")
    print(Fore.BLACK)


def stop_audio_playback(): 
    global is_playing
    is_playing = False
    print(Fore.GREEN + "Stopped Audio Feedback")
    print(Fore.BLACK)


def mic_callback(in_data, frame_count, time_info, status): 
    global mic_on_at, mic_active

    if mic_active != True: 
       print(Fore.GREEN + "Mic Active")
       pass

    mic_queue.put(in_data)

    return (None, pyaudio.paContinue)


