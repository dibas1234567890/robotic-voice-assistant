import time
from gtts import gTTS
import numpy as np
import pyttsx3 
import speech_recognition as sr
from playsound import playsound

language = "en"
r = sr.Recognizer() 
engine = pyttsx3.init()
name = "Dibas"
# greetings = [f"whats up master {name}", "yeah?", "Well, hello there! How's it going today?",
#              f"Ahoy there, Captain {name}! How's the ship sailing?", "How can I help?", "How's it going my man!"]
greetings =[f"Hello {name}, how may I help you?"]
tts_engine = 'gtts'
messages = [{"role": "system", "content": "You are a helpful assistant. Keep answers under 100 words."}]


def listen_for_wake_word(source, messages):
    print("DEBUG: === Starting wake word detection ===")
    print("DEBUG: Listening for 'Hello'...")
    print("DEBUG: Wake word detection is case-insensitive")

    listen_attempts = 0
    max_attempts = 50

    while listen_attempts < max_attempts:
        listen_attempts += 1
        print(f"DEBUG: Wake word attempt {listen_attempts}")
        try:
            print("DEBUG: Waiting for audio input...")
            audio = r.listen(source, timeout=10, phrase_time_limit=5)
            print("DEBUG: Audio captured, attempting recognition...")
            text = r.recognize_google(audio)
            print(f"DEBUG: Recognition successful: '{text}'")
            if "hello" in text.lower():
                print("DEBUG: *** WAKE WORD DETECTED! ***")
                greet_text = np.random.choice(greetings)
                try:
                    if tts_engine == 'pyttsx3':
                        engine.say(greet_text)
                        engine.runAndWait()
                    elif tts_engine == 'gtts':
                        tts = gTTS(text=greet_text, lang=language)
                        tts.save('response.mp3')
                        playsound('response.mp3')
                    print("DEBUG: Greeting complete, switching to conversation mode")
                    # listen_and_respond(source, messages)
                    break
                except Exception as e:
                    
                    print(f"DEBUG: Error during greeting: {e}")
            else:
                print(f"DEBUG: Wake word not found in '{text}'. Continuing to listen...")
        except sr.WaitTimeoutError:
            print("DEBUG: Listen timeout - no speech detected")
            continue
        except sr.UnknownValueError:
            print("DEBUG: Audio captured but not understood")
            continue
        except sr.RequestError as e:
            print(f"DEBUG: Recognition error: {e}")
            time.sleep(1)
            continue
        except Exception as e:
            print(f"DEBUG: Unexpected error: {e}")
            continue
    print(f"DEBUG: Wake word detection stopped after {listen_attempts} attempts")

with sr.Microphone(device_index=4) as source: 
    r.adjust_for_ambient_noise(source=source)
    listen_for_wake_word(source=source, messages=messages)