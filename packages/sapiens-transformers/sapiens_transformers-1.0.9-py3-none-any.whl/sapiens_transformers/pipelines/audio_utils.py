"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import datetime
import platform
import subprocess
from typing import Optional, Tuple, Union
import numpy as np
def ffmpeg_read(bpayload: bytes, sampling_rate: int) -> np.array:
    ar = f"{sampling_rate}"
    ac = "1"
    format_for_conversion = "f32le"
    ffmpeg_command = ["ffmpeg", "-i", "pipe:0", "-ac", ac, "-ar", ar, "-f", format_for_conversion, "-hide_banner", "-loglevel", "quiet", "pipe:1"]
    try:
        with subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as ffmpeg_process: output_stream = ffmpeg_process.communicate(bpayload)
    except FileNotFoundError as error: raise ValueError("ffmpeg was not found but is required to load audio files from filename") from error
    out_bytes = output_stream[0]
    audio = np.frombuffer(out_bytes, np.float32)
    if audio.shape[0] == 0: raise ValueError("Soundfile is either not in the correct format or is malformed. Ensure that the soundfile has a valid audio file extension (e.g. wav, flac or mp3) and is not corrupted. If reading from a remote URL, ensure that the URL is the full address to **download** the audio file.")
    return audio
def ffmpeg_microphone(sampling_rate: int, chunk_length_s: float, format_for_conversion: str = "f32le", ffmpeg_input_device: Optional[str] = None):
    ar = f"{sampling_rate}"
    ac = "1"
    if format_for_conversion == "s16le": size_of_sample = 2
    elif format_for_conversion == "f32le": size_of_sample = 4
    else: raise ValueError(f"Unhandled format `{format_for_conversion}`. Please use `s16le` or `f32le`")
    system = platform.system()
    if system == "Linux":
        format_ = "alsa"
        input_ = ffmpeg_input_device or "default"
    elif system == "Darwin":
        format_ = "avfoundation"
        input_ = ffmpeg_input_device or ":default"
    elif system == "Windows":
        format_ = "dshow"
        input_ = ffmpeg_input_device or _get_microphone_name()
    ffmpeg_command = ["ffmpeg", "-f", format_, "-i", input_, "-ac", ac, "-ar", ar, "-f", format_for_conversion, "-fflags", "nobuffer", "-hide_banner", "-loglevel", "quiet", "pipe:1"]
    chunk_len = int(round(sampling_rate * chunk_length_s)) * size_of_sample
    iterator = _ffmpeg_stream(ffmpeg_command, chunk_len)
    for item in iterator: yield item
def ffmpeg_microphone_live(sampling_rate: int, chunk_length_s: float, stream_chunk_s: Optional[int] = None, stride_length_s: Optional[Union[Tuple[float, float], float]] = None, format_for_conversion: str = "f32le", ffmpeg_input_device: Optional[str] = None):
    if stream_chunk_s is not None: chunk_s = stream_chunk_s
    else: chunk_s = chunk_length_s
    microphone = ffmpeg_microphone(sampling_rate, chunk_s, format_for_conversion=format_for_conversion, ffmpeg_input_device=ffmpeg_input_device)
    if format_for_conversion == "s16le":
        dtype = np.int16
        size_of_sample = 2
    elif format_for_conversion == "f32le":
        dtype = np.float32
        size_of_sample = 4
    else: raise ValueError(f"Unhandled format `{format_for_conversion}`. Please use `s16le` or `f32le`")
    if stride_length_s is None: stride_length_s = chunk_length_s / 6
    chunk_len = int(round(sampling_rate * chunk_length_s)) * size_of_sample
    if isinstance(stride_length_s, (int, float)): stride_length_s = [stride_length_s, stride_length_s]
    stride_left = int(round(sampling_rate * stride_length_s[0])) * size_of_sample
    stride_right = int(round(sampling_rate * stride_length_s[1])) * size_of_sample
    audio_time = datetime.datetime.now()
    delta = datetime.timedelta(seconds=chunk_s)
    for item in chunk_bytes_iter(microphone, chunk_len, stride=(stride_left, stride_right), stream=True):
        item["raw"] = np.frombuffer(item["raw"], dtype=dtype)
        item["stride"] = (item["stride"][0] // size_of_sample, item["stride"][1] // size_of_sample)
        item["sampling_rate"] = sampling_rate
        audio_time += delta
        if datetime.datetime.now() > audio_time + 10 * delta: continue
        yield item
def chunk_bytes_iter(iterator, chunk_len: int, stride: Tuple[int, int], stream: bool = False):
    acc = b""
    stride_left, stride_right = stride
    if stride_left + stride_right >= chunk_len: raise ValueError(f"Stride needs to be strictly smaller than chunk_len: ({stride_left}, {stride_right}) vs {chunk_len}")
    _stride_left = 0
    for raw in iterator:
        acc += raw
        if stream and len(acc) < chunk_len:
            stride = (_stride_left, 0)
            yield {"raw": acc[:chunk_len], "stride": stride, "partial": True}
        else:
            while len(acc) >= chunk_len:
                stride = (_stride_left, stride_right)
                item = {"raw": acc[:chunk_len], "stride": stride}
                if stream: item["partial"] = False
                yield item
                _stride_left = stride_left
                acc = acc[chunk_len - stride_left - stride_right :]
    if len(acc) > stride_left:
        item = {"raw": acc, "stride": (_stride_left, 0)}
        if stream: item["partial"] = False
        yield item
def _ffmpeg_stream(ffmpeg_command, buflen: int):
    bufsize = 2**24
    try:
        with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, bufsize=bufsize) as ffmpeg_process:
            while True:
                raw = ffmpeg_process.stdout.read(buflen)
                if raw == b"": break
                yield raw
    except FileNotFoundError as error: raise ValueError("ffmpeg was not found but is required to stream audio files from filename") from error
def _get_microphone_name():
    command = ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", ""]
    try:
        ffmpeg_devices = subprocess.run(command, text=True, stderr=subprocess.PIPE, encoding="utf-8")
        microphone_lines = [line for line in ffmpeg_devices.stderr.splitlines() if "(audio)" in line]
        if microphone_lines:
            microphone_name = microphone_lines[0].split('"')[1]
            print(f"Using microphone: {microphone_name}")
            return f"audio={microphone_name}"
    except FileNotFoundError: print("ffmpeg was not found. Please install it or make sure it is in your system PATH.")
    return "default"
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
