
import pyaudio


class CustomRealtimeConfig(): 
    def __init__(self, CHUNK_SIZE = 1024, FORMAT = pyaudio.paInt16, RATE = 24000, REENGAGE_DELAY_MS = 1000
):
        self.CHUNK_SIZE = CHUNK_SIZE
        self.RATE = RATE
        self.FORMAT = FORMAT
        self.REENGAGE_DELAY_MS = REENGAGE_DELAY_MS