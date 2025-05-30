import asyncio
from colorama import Fore
import speech_recognition as sr

from custom_db.pinecone_client_ import PineconeCustom
from voice_utils.wake_word import listen_for_wake_word
from voice_utils.realtime_connection import realtime_main_

messages = [{"role": "system", "content": "You are a helpful assistant. Keep answers under 100 words."}]
r = sr.Recognizer()
name = "Dibas"

async def main():
    loop = asyncio.get_running_loop()

    # Avoid initializing async resources before this point
    with sr.Microphone(device_index=4) as source:
        r.adjust_for_ambient_noise(source=source)

        check_var = await loop.run_in_executor(
            None,
            listen_for_wake_word,
            source, messages, name, r
        )

        if check_var:
            print(Fore.GREEN + "Inside checkvar condition")

            async with PineconeCustom() as pinecone_client_async:
                await pinecone_client_async.connect_index()
                await realtime_main_(pinecone_client=pinecone_client_async)

if __name__ == "__main__":
    asyncio.run(main())
