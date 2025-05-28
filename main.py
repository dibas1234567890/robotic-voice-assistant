from colorama import Fore
from voice_utils.wake_word import listen_for_wake_word
from voice_utils.realtime_connection import realtime_main_
import speech_recognition as sr

messages = [{"role": "system", "content": "You are a helpful assistant. Keep answers under 100 words."}]
r = sr.Recognizer() 
name = "Dibas"


def main():
    """Calls the wakeword and realtime connection functions to first activate the listener and then pass queries to 
    the API"""

    with sr.Microphone(device_index=4) as source: 
        r.adjust_for_ambient_noise(source=source)
        check_var = listen_for_wake_word(source=source, messages=messages, r=r, name=name)
        if check_var: 
            print(Fore.GREEN + "Inside checkvar condition")
            realtime_main_()



if __name__ == "__main__":
    main()