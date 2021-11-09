import asyncio as aio
import logging
import msgpack
import gzip
from error import BadUsageException
from tts_interface import AIOTTSConverter
import dill

CHUNKS_PER_MSG = 100000

class ClientInterface:
    rdr: aio.StreamReader
    wrtr: aio.StreamWriter
    tts_cvtr: AIOTTSConverter

    def __init__(self, rdr: aio.StreamReader, wrtr: aio.StreamWriter, READ_SIZE: int, logger: logging.Logger):
        self.logger = logger
        self.READ_SIZE = READ_SIZE
        self.rdr = rdr
        self.wrtr = wrtr
        self.unpacker: msgpack.fallback.Unpacker = msgpack.Unpacker()
        self.tts_cvtr = AIOTTSConverter(logger)
        self.closed = False

    async def cli_main(self):
        "do all the things to deal with the client"
        while True:
            #checks if conn closed, and also reads more data from the socket
            if not await self._recieve_data():
                #the connection closed
                break
            for msg in self.unpacker:
                self.logger.debug(f"recieved {msg}")
                if type(msg) != dict:
                    continue
                if "type" in msg.keys():
                    if (msg["type"] == "do_tts") and ("text" in msg.keys()):
                        text = msg["text"]
                        if type(text) != str:
                            continue
                        await self._send_message(
                            {
                                "type": "tts_status",
                                "status": "converting"
                            }
                        )
                        audio = await self.tts_cvtr.tts(text)
                        fmtd_audio = []
                        for chunk in audio:
                            if not type(chunk) == int:
                                fmtd_audio.append(chunk.tobytes())
                        await self._send_message(
                            {
                                "type": "tts_status",
                                "status": "sending_audio",
                                "metadata": {
                                    "total_chunks": len(fmtd_audio),
                                }
                            }
                        )
                        for i in range(0, len(fmtd_audio), CHUNKS_PER_MSG):
                            chunk_set = fmtd_audio[i:i + CHUNKS_PER_MSG]
                            await self._send_message(
                                {
                                    "type": "audio_chunks",
                                    "chunks": chunk_set,
                                },
                                False
                            )
                        await self._send_message(
                            {
                                "type": "tts_status",
                                "status": "done_sending_audio"
                            }
                        )

    async def _recieve_data(self):
        buf = await self.rdr.read(self.READ_SIZE)
        if not buf:
            await self._close_conn()
            return False
        self.unpacker.feed(buf)
        return True

    async def _send_message(self, msg, log=True):
        if self.closed:
            raise BadUsageException("Connection is closed!")
        if log:self.logger.debug(f"Sending {msg}")
        bmsg = msgpack.dumps(msg)
        self.wrtr.write(bmsg)
        await self.wrtr.drain()

    async def _close_conn(self):
        if self.closed:
            raise BadUsageException("Connection is already closed!")
        self.logger.debug(f"Closing connection")
        await self.wrtr.drain()
        self.wrtr.close()
        await self.wrtr.wait_closed()
        self.closed = True