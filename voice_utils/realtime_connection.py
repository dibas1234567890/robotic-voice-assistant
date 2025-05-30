#built-in imports
import base64 
import json
import os 
import queue
import socket
import threading
import time 
import pyaudio
import socks
import websocket
from colorama import Fore
import asyncio

#custom importss
from tools.hotel_information_tools import general_hotel_information_tool
from tools.hotel_service_tools import hotel_service_tool
from tools.weather_tool import get_weather
from voice_utils.realime_config import CustomRealtimeConfig


config = CustomRealtimeConfig()

#TODO: make dynamic serviuces
listed_services = ["front_desk", "room_service", "housekeeping", "maintenance", "admin", "help"]
socket.socket = socks.socksocket

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

languages = "Arabic, English, French, Mexican, Hindi"

if not OPENAI_API_KEY: 
    raise ValueError("API KEY MISSING")

WS_URL = os.getenv("REALTIME_WS_URL")
if not WS_URL: 
    raise ValueError("WS_URL not initialized properly")

chunk_size = config.CHUNK_SIZE
rate = config.RATE
format_ = config.FORMAT

audio_buffer = bytearray()

mic_queue = queue.Queue()

stop_event = threading.Event()

mic_on_at = 0 
mic_active = None
REENGAGE_DELAY_MS = config.REENGAGE_DELAY_MS




def run_async_function_in_thread(async_func, *args):
    
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_func(*args))


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
        print('🎙️🟢 Mic active')
        mic_active = True
    mic_queue.put(in_data)

    # if time.time() > mic_on_at:
    #     if mic_active != True:
    #         print('🎙️🟢 Mic active')
    #         mic_active = True
    #     mic_queue.put(in_data)
    # else:
    #     if mic_active != False:
    #         print('🎙️🔴 Mic suppressed')
    #         mic_active = False

    return (None, pyaudio.paContinue)


# Function to send microphone audio data to the WebSocket
def send_mic_audio_to_websocket(ws):
    try:
        while not stop_event.is_set():
            if not mic_queue.empty():
                mic_chunk = mic_queue.get()
                # print(f'🎤 Sending {len(mic_chunk)} bytes of audio data.')
                encoded_chunk = base64.b64encode(mic_chunk).decode('utf-8')
                message = json.dumps({'type': 'input_audio_buffer.append', 'audio': encoded_chunk})
                try:
                    ws.send(message)
                except Exception as e:
                    print(Fore.RED + f'Error sending mic audio: {e}')
    except Exception as e:
        print(f'Exception in send_mic_audio_to_websocket thread: {e}')
    finally:
        print('Exiting send_mic_audio_to_websocket thread.')

def speaker_callback(in_data, frame_count, time_info, status):
    global audio_buffer, mic_on_at

    bytes_needed =frame_count *2 
    current_buffer_size = len(audio_buffer)

    if current_buffer_size >= bytes_needed: 
        audio_chunk = bytes(audio_buffer[:bytes_needed])
        audio_buffer = audio_buffer[bytes_needed:]
        mic_on_at = time.time() +REENGAGE_DELAY_MS/1000
    else: 
        audio_chunk = bytes(audio_buffer) + b'\x00' * (bytes_needed-current_buffer_size)
        audio_buffer.clear()
    return (audio_chunk, pyaudio.paContinue)


async def recieve_audio_from_websocket(ws, pinecone_client = None):
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
                    await handle_function_call(message, ws, pinecone_client)
                elif event_type == "error":
                    error_detail = message.get("message", "No message")
                    print(Fore.RED + f"WebSocket Error: {error_detail}")
                    print(Fore.RED + f"Full Error Event: {json.dumps(message, indent=2)}")
                    print(Fore.BLACK)
                    stop_event.set()  # Optionally shut down everything

            except Exception as e: 
                print(Fore.RED + "Error while receiving audio") 
                print(Fore.BLACK)

    except Exception as e: 
        print(Fore.RED + f"Exception received in receive audio thread: {e}")
        print(Fore.BLACK)

async def handle_function_call(event_json:dict, ws, pinecone_client): 
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
        if name == "general_hotel_information_tool": 
            query = function_call_args.get("query","")

            if query: 
                hotel_information_results = await general_hotel_information_tool(query=query, pinecone_client=pinecone_client)
                send_function_call_result(str(hotel_information_results), call_id, ws)
        if name == "hotel_service_tool":
            query = function_call_args.get("query","")
            service_request = function_call_args.get("service_request", "")
            quantity = function_call_args.get("quantity", '')

            if query and service_request:
                # You need to wrap the service_request, quantity, and query into a list of dicts
                service_requests = [{
                    "service_request": service_request,
                    "quantity": quantity,
                    "query": query
                }]
                
                hotel_service_request_result = await hotel_service_tool(requests=service_requests)

                send_function_call_result(str(hotel_service_request_result), call_id, ws)


    except Exception as e: 
        print()
        print(Fore.RED +f"Exception in {__name__}")
        print(Fore.BLACK)


def send_function_call_result(result, call_id, ws): 
    result_json = {
        "type":"conversation.item.create", 
        "item":{
            "type":"function_call_output", 
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
    Also, nthere are multiple tools like generalhotel information tool, entertainment tools, proceed accordingly

    Instructions:
    - Greet the user in a friendly way.
    - If the user asks about the weather, use the weather tool to fetch the current
      weather based on their location or the city they mention.
    - Respond clearly and concisely with the relevant weather information.
   
    """
    hotels = "Accord Hotels"
    session_config = {
        "type": "session.update", 
        "session": {
            "instructions": (
                f"You are a helpful voice assistant for {hotels}. Greet the user cheerfully. "
                "If they ask about the weather, use the weather tool to look up the "
                "current conditions based on their location or the city they mention. "
                "Respond in a natural, conversational tone with the weather information."
                f""" - You will be provided multiple tools like general_hotel_information_tool, weather tool, etc make the tool selection dynamic as per the session configuration. 
              Always respond with the language the user has replied to you in the latest message from these languages, 
              only these languages {languages}, when the user asks general hotelinformation questions autmaitcally assume that it is for {hotels}"""
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
            "tools" : [
                {
                    "type":"function", 
                    "name" : "get_weather", 
                    "description":"Get current weather for a specified city", 
                    "parameters" : {
                        "type":"object",
                        "properties" : {
                            "city" :{
                                "type" :"string", 
                                "description" : "The name of the city for which the weather is to be fetched"
                            }, 
                           

                        },
                         "required" : ["city"]
                    }
                }, {
                    "type" : "function", 
                    "name" : "general_hotel_information_tool", 
                    "description" : "Use the piencone index for parsing through any queries related to hotel information like wifi password", 
                    "parameters" : {
                        "type" : "object", 
                        "properties" : {
                            "query" : {
                                "type": "string", 
                                "description" : "The query the user has asked for"
                            }, 
                         
                        }, 
                        "required" : ["query"]
                    }
                }, 
               {
                "type": "function",
                "name": "hotel_service_tool",
                "description": f"This tool takes any of the service listed here: {listed_services}",
                "parameters": {
                    "type": "object",
                    "properties": {
                    "service_request": {
                        "type": "string",
                        "enum": listed_services,
                        "description": "The type of request by the guest, from the list provided to you"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "The amount of the requested item or service for how many guests"
                    },
                    "query": {
                        "type": "string",
                        "description": "The user's query regarding the service request"
                    }
                    },
                    "required": ["service_request", "query"]
                }
                }

            ]
        }
    }
    session_config_json = json.dumps(session_config)
    print(f"Send FC session update: {session_config_json}")

    try: 
        ws.send(session_config_json)
    except: 
        print("Failed to send session update")


def create_connection_with_ipv4(*args, **kwargs): 
    original_getaddrinfo = socket.getaddrinfo
    def getaddrinfo_ipv4(host, port, family=socket.AF_INET, *args): 
        return original_getaddrinfo(host, port, socket.AF_INET, *args)
    socket.getaddrinfo = getaddrinfo_ipv4

    try: 
        return websocket.create_connection(*args, **kwargs) 
    finally: 
        socket.getaddrinfo = original_getaddrinfo

async def connect_to_openai(pinecone_client):
    ws = None 
    try:
        ws = create_connection_with_ipv4(
            WS_URL,
            header=[f"Authorization: Bearer {OPENAI_API_KEY}", 'OpenAI-Beta: realtime=v1']
        )
        print(Fore.GREEN + "Connected to OpenAI socket")

        # Create async task for receiving audio (non-blocking)
        receive_task = asyncio.create_task(recieve_audio_from_websocket(ws, pinecone_client))

        # Start blocking mic thread (ok to use thread for this)
        mic_thread = threading.Thread(target=send_mic_audio_to_websocket, args=(ws,))
        mic_thread.start()

        while not stop_event.is_set():
            await asyncio.sleep(0.1)

        print(Fore.GREEN + "Sending websocket close frame")
        ws.send_close()

        await receive_task
        mic_thread.join()

        print(Fore.GREEN + "Websocket closed and threads terminated")
    except Exception as e:
        print(Fore.RED + f"Failed to connect to OpenAI: {e}")
    finally:
        if ws is not None:
            try:
                ws.close()
                print(Fore.GREEN + "Websocket connection closed")
            except Exception:
                print(Fore.RED + "Error closing connection")

async def realtime_main_(pinecone_client): 
    p = pyaudio.PyAudio()
    mic_stream = p.open(format=config.FORMAT,
                        channels=1, 
                        rate=rate, 
                        input=True, 
                        stream_callback=mic_callback,
                        frames_per_buffer=chunk_size)
    speaker_stream = p.open(format=config.FORMAT,
                        channels=1, 
                        rate=rate, 
                        output=True, 
                        stream_callback=speaker_callback,
                        frames_per_buffer=chunk_size)
    try: 
        mic_stream.start_stream()
        speaker_stream.start_stream()
        await connect_to_openai(pinecone_client)
        while mic_stream.is_active() and speaker_stream.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt: 
        print(Fore.GREEN + "Gracefully shutting down")
        print(Fore.BLACK)
        stop_event.set()

    finally: 
        mic_stream.stop_stream()
        mic_stream.close()
        speaker_stream.stop_stream()
        speaker_stream.close()
        p.terminate()
        print(Fore.GREEN, "Audio streams stopped and resources released. Exiting")
        print(Fore.BLACK, "")

# if __name__ == "__main__": 
#     realtime_main_()