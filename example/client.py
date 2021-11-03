import asyncio as aio
import msgpack
import pyaudio
import gzip
import dill

audio = pyaudio.PyAudio()

speakers = audio.open(
    format=pyaudio.paFloat32,
    channels=1,
    rate=22050,
    output=True,
    frames_per_buffer=1024,
)

def play(audio):
    speakers.start_stream()
    for chunk in audio:
        speakers.write(chunk)
    speakers.stop_stream()

async def example_client():
    reader, writer = await aio.open_connection(
        'localhost', 15555
    )
    writer.write(msgpack.dumps({})); await writer.drain()
    print("enter what to say. make shure to finish with a .")
    msg = {"type": "do_tts", "text": input("what to say: ")}
    bmsg = msgpack.dumps(msg)
    writer.write(bmsg)
    await writer.drain()
    print("sent request")
    unpacker: msgpack.fallback.Unpacker = msgpack.Unpacker()
    audio_in = []
    status = 0 #0 for normal, 1 for saving audio
    done = False
    while not done:
        buf = await reader.read(1024**2)
        unpacker.feed(buf)
        for obj in unpacker:
            if status == 0:
                if obj["type"] == "tts_status":
                    if obj["status"] == "converting":
                        print("audio being converted")
                    elif obj["status"] == "sending_audio":
                        print("audio is being sent")
                        status=1
            elif status == 1:
                if obj["type"] == "audio_chunk":
                    print("recieved chunk")
                    audio_in.append(obj["audio"])
                if obj["type"] == "tts_status":
                    if obj["status"] == "done_sending_audio":
                        print("audio done being sent")
                        status = 0
                        play(audio_in)
                        audio_in = []
                        done = True
    writer.close()
    await writer.wait_closed()

aio.run(example_client())