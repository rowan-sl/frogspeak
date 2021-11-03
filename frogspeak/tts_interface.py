import functools
from TTS.utils.synthesizer import Synthesizer
from TTS.utils.manage import ModelManager
import numpy as np
import time
import wave
import yaml
import pathlib
import torch
import logging

import asyncio as aio
from functools import partial

from utils.filepath import conf_path

class AIOTTSConverter:
    """asyncio Text-to-speech converter"""
    def __init__(self, main_logger: logging.Logger):
        self.ml = main_logger
        # read from config part 1 (this parts config)
        with open(conf_path, "r") as f:
            self.conf = yaml.safe_load(f)
        # speeeeeed
        cuda_availablity = torch.cuda.is_available()
        if cuda_availablity == True:
            if self.conf["use_cuda"]:
                self.conf["use_cuda"] = True
            else:
                self.conf["use_cuda"] = False
        else:
            self.conf["use_cuda"] = False
            self.ml.warn("!! Cuda is not available!!!")
        # create instance of the coqui tts model manager
        self.manager = ModelManager()
        # download the model
        (
            self.model_path,
            self.config_path,
            self.model_item,
        ) = self.manager.download_model(self.conf["model"])
        # download the vocoder
        self.vocoder_path, self.vocoder_config_path, _ = self.manager.download_model(
            self.model_item["default_vocoder"]
        )
        # create the coqui tts instance
        self.coqui_tts = Synthesizer(
            self.model_path,
            self.config_path,
            None,
            self.vocoder_path,
            self.vocoder_config_path,
            None,
            None,
            self.conf["use_cuda"],
        )

    async def tts(self, text):
        loop = aio.get_running_loop()
        return await loop.run_in_executor(
            None,
            functools.partial(
                self._tts,
                text
            )
        )

    def _tts(self, text):
        """blocking version of tts, actualy does the tts while the tts() function handles the asyncio part"""
        voice = self.coqui_tts.tts(text)
        return voice
