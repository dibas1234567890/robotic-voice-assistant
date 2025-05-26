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
from helper_functions import get_weather
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

def send_mic_audio_to_websocket(ws): 
    try: 
        while not stop_event.is_set():
            if not mic_queue.empty():
                mic_chunk = mic_queue.get()
                print(Fore.GREEN + "sending audio to mic")
                encoded_chunk = base64.b64encode(mic_chunk).decode("utf-8") 
                message = json.dumps({"type":"input_audio_buffer.append", "audio":encoded_chunk})
                try: 
                    ws.send(message)
                except Exception as e: 
                    print(f"Couldn't send mic audio {e}")
    except Exception as e: 
        print(f"Exception in send_mic_audio_thread {e}")
    finally: 
        print("Mic thread audio is being exited")

def speaker_callback(in_data, frame_count, time_info, status):
    global audio_buffer, mic_on_at

    bytes_needed =frame_count *2 
    current_buffer_size = len(audio_buffer)

    if current_buffer_size >= bytes_needed: 
        audio_chunk = bytes(audio_buffer[:bytes_needed])
        audio_buffer = audio_buffer[bytes_needed:]
        mic_on_at = time.time()
    else: 
        audio_chunk = bytes(audio_buffer)
        audio_buffer.clear()

def recieve_audio_from_websocket(ws):
    global audio_buffer

    try: 
        while not stop_event.is_set(): 
            try: 
                message = ws.recv()
                if not message: 
                    print(Fore.RED + "Empty message recieved")
                    print(Fore.BLACK )
                    break
                message = json.loads(message)
                event_type = message['type']
                print(Fore.GREEN + f"recieved websocket response {event_type}")
                if event_type == "session.created": 
                    send_fc_session_update(ws)
                elif event_type == "response.audio.delta": 
                    audio_content = base64.b64decode(message['delta'])
                    audio_buffer.extend(audio_content)
                    print(Fore.GREEN + f"Received {len(audio_content)} bytes, totall_buffer_size = {len(audio_buffer)}")
                    print(Fore.BLACK)
                elif event_type == "input_audio.speech_started":
                    print(Fore.GREEN + "Speech started, clearing buffer and stopping playback")
                    print(Fore.BLACK)
                    clear_audio_buffer()
                    stop_audio_playback()
                elif event_type == "response.audio.done":
                    print(Fore.GREEN + "AI is done speaking")
                    print(Fore.BLACK)
                elif event_type == "response.function_call_arguments.done":
                    handle_function_call(message, ws)

            except Exception as e: 
                print(Fore.RED + "Error while receiving audio") 
                print(Fore.BLACK)

    except Exception as e: 
        print(Fore.RED + f"Exception received in receive audio thread: {e}")
        print(Fore.BLACK)

def handle_function_call(event_json:dict, ws): 
    try: 
        name = event_json.get("name", "")
        call_id = event_json.get("call_id", "")
        arguments = event_json.get("arguments", "")
        function_call_args = json.loads(arguments)

        if name == "get_weather": 
            city = function_call_args.get("city", "")
            if city: 
                weather_result = get_weather(city)
                send_function_call_result(weather_result, call_id, ws)
            else: 
                print(Fore.RED +"City name not provided")
                print(Fore.BLACK)

    except Exception as e: 
        print()
        print(Fore.RED +f"Exception in {__name__}")
        print(Fore.BLACK)


def send_function_call_result(result, call_id, ws): 
    result_json = {
        "type":"conversation.item.create", 
        "item":{
            "type":"funciton_call_output", 
            "output" :  result,
            "call_id" : call_id
        }
    }

    try: 
        ws.send(json.dumps(result_json))
        print(Fore.GREEN + f"Sent funciton call result {result_json}")
        print(Fore.BLACK)
        rp_json = {
            "type": "response.create"
        }
        ws.send(json.dumps(rp_json))
        print(Fore.GREEN + f"json = {rp_json}")
        print(Fore.BLACK)
    except Exception as e: 
        print(Fore.RED + f"An exception occurred in {__name__}")
        print(Fore.BLACK)


def send_fc_session_update(ws): 
    """
    Sends a session update message over a WebSocket connection.

    Parameters:
    ws (WebSocket): The WebSocket connection through which the message is sent.

    The message updates the session with new instructions tailored for a voice agent
    that can retrieve weather information using a tool.

    Instructions:
    - Greet the user in a friendly way.
    - If the user asks about the weather, use the weather tool to fetch the current
      weather based on their location or the city they mention.
    - Respond clearly and concisely with the relevant weather information.
    """
    session_config = {
        "type": "session.update", 
        "session": {
            "instructions": (
                "You are a helpful voice assistant. Greet the user cheerfully. "
                "If they ask about the weather, use the weather tool to look up the "
                "current conditions based on their location or the city they mention. "
                "Respond in a natural, conversational tone with the weather information."
            ), 
            "turn_detection": {
                "type" : "server_vad", 
                "threshold" : 0.5, 
                "prefix_padding_ms" : 300, 
                "silence_duration_ms" : 500
            }, 
            "voice": "alloy",
            "temperature": 1,
            "max_response_output_tokens": 4096,
            "modalities": ["text", "audio"],
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "tool_choice" : "auto", 
        }
    }
    ws.send(json.dumps(session_config))
