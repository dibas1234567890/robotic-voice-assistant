import asyncio
from colorama import Fore
from voice_utils.wake_word import listen_for_wake_word
from voice_utils.realtime_connection import realtime_main_
import speech_recognition as sr

messages = [{"role": "system", "content": "You are a helpful assistant. Keep answers under 100 words."}]
r = sr.Recognizer()
name = "Dibas"

async def main():
    loop = asyncio.get_running_loop()
    #TODO: change device index later
    with sr.Microphone(device_index=4) as source:
        r.adjust_for_ambient_noise(source=source)
        
        # Run blocking wake word detection in a thread
        check_var = await loop.run_in_executor(
            None,  # use default thread pool
            listen_for_wake_word,
            source, messages, name, r  # pass args to your function
        )

        if check_var:
            print(Fore.GREEN + "Inside checkvar condition")
            await realtime_main_()

if __name__ == "__main__":
    asyncio.run(main())
