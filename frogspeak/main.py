import asyncio as aio
# import socket
# import numpy as np
# import time
# import wave
# import yaml
# import pathlib
# import torch
import msgpack
import logging

from args import args
from logging_config import setup_logging
logger = setup_logging(args, logging.DEBUG)

from client_interface import ClientInterface

READ_SIZE = 1024 ** 2

async def handle_client(rdr: aio.StreamReader, wrtr: aio.StreamWriter):
    logger.info("new client connected")
    client = ClientInterface(rdr, wrtr, READ_SIZE, logger)
    await client.cli_main()

async def run_server():
    server = await aio.start_server(handle_client, 'localhost', 15555)
    logger.info("ready to serve")
    async with server:
        await server.serve_forever()

aio.run(run_server())