import os
from openai import OpenAI
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import numpy as np
from gtts import gTTS
from playsound import playsound
import time

# Load environment variables
load_dotenv()

# Configuration
language = 'en'
tts_engine = 'gtts'  # 'gtts', 'pyttsx3', 'openai'
name = "Dibas"
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
model = 'gpt-3.5-turbo'
greetings = [f"whats up master {name}", "yeah?", "Well, hello there! How's it going today?",
             f"Ahoy there, Captain {name}! How's the ship sailing?", "How can I help?", "How's it going my man!"]

# Initialize recognizer
r = sr.Recognizer()

# DEBUG: Print recognizer settings
print(f"DEBUG: Recognizer energy threshold: {r.energy_threshold}")
print(f"DEBUG: Recognizer dynamic energy threshold: {r.dynamic_energy_threshold}")
print(f"DEBUG: Recognizer pause threshold: {r.pause_threshold}")
print(f"DEBUG: Recognizer phrase threshold: {r.phrase_threshold}")
print(f"DEBUG: Recognizer non speaking duration: {r.non_speaking_duration}")

# Set up pyttsx3 engine (if used)
engine = pyttsx3.init()
voices = engine.getProperty('voices')
print(f"DEBUG: Available voices: {len(voices)}")
for i, voice in enumerate(voices):
    print(f"DEBUG: Voice {i}: {voice.id}")

# Safely set voice
if len(voices) > 2:
    voice = voices[2]
    engine.setProperty('voice', voice.id)
    print(f"DEBUG: Using voice: {voice.id}")
else:
    print(f"DEBUG: Using default voice (only {len(voices)} voices available)")


def get_completion(messages, model="gpt-3.5-turbo-0125"):
    print("DEBUG: Getting completion from OpenAI...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=1
        )
        print("DEBUG: Successfully got completion from OpenAI")
        return response.choices[0].message.content
    except Exception as e:
        print(f"DEBUG: Error getting completion: {e}")
        return "Sorry, I couldn't process that request."


def get_bluetooth_microphone_index():
    print("DEBUG: Searching for microphones...")
    microphones = sr.Microphone.list_microphone_names()
    print(f"DEBUG: Found {len(microphones)} microphones:")
    
    for index, name in enumerate(microphones):
        print(f"DEBUG: {index}: {name}")
        if "bluetooth" in name.lower() or "headset" in name.lower():
            print(f"DEBUG: Found Bluetooth microphone at index {index}")
            return index
    
    print("DEBUG: No Bluetooth microphone found")
    return None


def test_microphone(source):
    """Test if microphone is working"""
    print("DEBUG: Testing microphone - say something...")
    try:
        # Short test listen
        audio = r.listen(source, timeout=3, phrase_time_limit=2)
        test_text = r.recognize_google(audio)
        print(f"DEBUG: Microphone test successful. Heard: '{test_text}'")
        return True
    except sr.WaitTimeoutError:
        print("DEBUG: Microphone test timeout - no speech detected")
        return False
    except sr.UnknownValueError:
        print("DEBUG: Microphone test - speech detected but not understood")
        return True  # At least we're getting audio
    except Exception as e:
        print(f"DEBUG: Microphone test error: {e}")
        return False


def listen_for_wake_word(source, messages):
    print("DEBUG: === Starting wake word detection ===")
    print("DEBUG: Listening for 'Hello'...")
    print("DEBUG: Wake word detection is case-insensitive")
    
    listen_attempts = 0
    max_attempts = 50  # Prevent infinite loop during debugging
    
    while listen_attempts < max_attempts:
        listen_attempts += 1
        print(f"DEBUG: Wake word attempt {listen_attempts}")
        
        try:
            print("DEBUG: Waiting for audio input...")
            # Increase timeout and add phrase_time_limit
            audio = r.listen(source, timeout=10, phrase_time_limit=5)
            print("DEBUG: Audio captured, attempting recognition...")
            
            # Try recognition
            text = r.recognize_google(audio)
            print(f"DEBUG: Recognition successful: '{text}'")
            print(f"DEBUG: Checking if '{text.lower()}' contains 'hello'")
            
            if "hello" in text.lower():
                print("DEBUG: *** WAKE WORD DETECTED! ***")
                greet_text = np.random.choice(greetings)
                print(f"DEBUG: Selected greeting: '{greet_text}'")

                try:
                    if tts_engine == 'pyttsx3':
                        print("DEBUG: Using pyttsx3 for greeting...")
                        engine.say(greet_text)
                        engine.runAndWait()
                    elif tts_engine == 'gtts':
                        print("DEBUG: Using gTTS for greeting...")
                        tts = gTTS(text=greet_text, lang=language)
                        tts.save('response.mp3')
                        print("DEBUG: Playing greeting...")
                        playsound('response.mp3')
                    
                    print("DEBUG: Greeting complete, switching to conversation mode")
                    listen_and_respond(source, messages)
                    break
                except Exception as e:
                    print(f"DEBUG: Error during greeting: {e}")
            else:
                print(f"DEBUG: Wake word not found in '{text}'. Continuing to listen...")
                
        except sr.WaitTimeoutError:
            print("DEBUG: Listen timeout - no speech detected within timeout period")
            continue
        except sr.UnknownValueError:
            print("DEBUG: Audio captured but speech not recognized")
            continue
        except sr.RequestError as e:
            print(f"DEBUG: Recognition service error: {e}")
            time.sleep(1)  # Wait before retrying
            continue
        except Exception as e:
            print(f"DEBUG: Unexpected error in wake word detection: {e}")
            continue
    
    print(f"DEBUG: Wake word detection stopped after {listen_attempts} attempts")


def listen_and_respond(source, messages):
    print("DEBUG: === Entering conversation mode ===")
    
    try:
        playsound("listen_chime.mp3")
        print("DEBUG: Played listen chime")
    except Exception as e:
        print(f"DEBUG: Could not play listen chime: {e}")
    
    conversation_attempts = 0
    max_conversation_attempts = 10
    
    while conversation_attempts < max_conversation_attempts:
        conversation_attempts += 1
        print(f"DEBUG: Conversation attempt {conversation_attempts}")
        print("DEBUG: Listening for conversation...")
        
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            text = r.recognize_google(audio)
            print(f"DEBUG: You said: '{text}'")

            messages.append({'role': 'user', 'content': text})
            print(f"DEBUG: Added user message to conversation. Total messages: {len(messages)}")
            
            response_text = get_completion(messages)
            print(f"DEBUG: AI Response: '{response_text}'")

            # Text-to-speech response
            try:
                if tts_engine == 'pyttsx3':
                    print("DEBUG: Using pyttsx3 for response...")
                    engine.say(response_text)
                    engine.runAndWait()
                elif tts_engine == 'gtts':
                    print("DEBUG: Using gTTS for response...")
                    tts = gTTS(text=response_text, lang=language)
                    tts.save('response.mp3')
                    playsound('response.mp3')
                elif tts_engine == 'openai':
                    print("DEBUG: Using OpenAI TTS for response...")
                    response = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=response_text
                    )
                    response.stream_to_file('response.mp3')
                    playsound('response.mp3')
                
                print("DEBUG: Response played successfully")
            except Exception as e:
                print(f"DEBUG: Error playing response: {e}")

            messages.append({'role': 'assistant', 'content': response_text})
            print(f"DEBUG: Added assistant message. Total messages: {len(messages)}")
            
            try:
                playsound("listen_chime.mp3")
                print("DEBUG: Played listen chime after response")
            except Exception as e:
                print(f"DEBUG: Could not play listen chime after response: {e}")

        except sr.WaitTimeoutError:
            print("DEBUG: Conversation timeout - returning to wake word detection")
            listen_for_wake_word(source, messages)
            break
        except sr.UnknownValueError:
            print("DEBUG: Speech not recognized in conversation mode")
            try:
                playsound("error.mp3")
            except:
                print("DEBUG: Could not play error sound")
            print("DEBUG: Returning to wake word detection...")
            listen_for_wake_word(source, messages)
            break
        except sr.RequestError as e:
            print(f"DEBUG: Recognition service error in conversation: {e}")
            try:
                engine.say(f"Error: {e}")
                engine.runAndWait()
            except:
                print("DEBUG: Could not announce error")
            listen_for_wake_word(source, messages)
            break
        except Exception as e:
            print(f"DEBUG: Unexpected error in conversation: {e}")
            break


if __name__ == "__main__":
    print("DEBUG: === Starting Voice Assistant ===")
    
    # Test API key
    if not api_key:
        print("DEBUG: WARNING - No OpenAI API key found!")
    else:
        print("DEBUG: OpenAI API key loaded successfully")
    
    # Find microphone
    mic_index = get_bluetooth_microphone_index()
    if mic_index is None:
        print("DEBUG: Using default system microphone")
        mic_index = None
    else:
        print(f"DEBUG: Using Bluetooth microphone at index {mic_index}")

    # Initialize conversation
    messages = [{"role": "system", "content": "You are a helpful assistant. Keep answers under 100 words."}]
    print(f"DEBUG: Initialized conversation with {len(messages)} system message(s)")
    
    # Set up microphone
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print("DEBUG: Microphone initialized successfully")
            print("DEBUG: Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=2)
            print(f"DEBUG: Ambient noise adjustment complete. Energy threshold: {r.energy_threshold}")
            
            # Test microphone
            print("DEBUG: Testing microphone functionality...")
            if test_microphone(source):
                print("DEBUG: Microphone test passed")
            else:
                print("DEBUG: WARNING - Microphone test failed, but continuing anyway")
            
            # Start wake word detection
            print("DEBUG: Starting main loop...")
            listen_for_wake_word(source, messages)
            
    except Exception as e:
        print(f"DEBUG: Critical error with microphone setup: {e}")
        print("DEBUG: Available microphones:")
        for i, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"DEBUG: {i}: {name}")