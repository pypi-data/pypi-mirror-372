'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
import functools
import importlib
import importlib.metadata
import inspect
import io
import multiprocessing
import os
import random
import re
import struct
import sys
import tempfile
import time
import unittest
import urllib.parse
from contextlib import contextmanager
from io import BytesIO, StringIO
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union
import numpy as np
import PIL.Image
import PIL.ImageOps
import requests
from numpy.linalg import norm
from packaging import version
from .import_utils import (BACKENDS_MAPPING, is_sapiens_accelerator_available, is_sapiens_machine_available, is_compel_available, is_flax_available, is_gguf_available, is_note_seq_available, is_onnx_available,
is_opencv_available, is_peft_available, is_timm_available, is_torch_available, is_torch_version, is_torchao_available, is_torchsde_available, is_transformers_available)
global_rng = random.Random()
_required_peft_version = is_peft_available() and version.parse(version.parse(importlib.metadata.version('peft')).base_version) > version.parse('0.5')
_required_sapiens_transformers_version = is_transformers_available() and version.parse(version.parse(importlib.metadata.version('sapiens_transformers')).base_version) > version.parse('4.33')
USE_PEFT_BACKEND = _required_peft_version and _required_sapiens_transformers_version
BIG_GPU_MEMORY = int(os.getenv('BIG_GPU_MEMORY', 40))
if is_torch_available():
    import torch
    if 'DIFFUSERS_TEST_BACKEND' in os.environ:
        backend = os.environ['DIFFUSERS_TEST_BACKEND']
        try: _ = importlib.import_module(backend)
        except ModuleNotFoundError as e: raise ModuleNotFoundError(f"Failed to import `DIFFUSERS_TEST_BACKEND` '{backend}'! This should be the name of an installed module to enable a specified backend.):\n{e}") from e
    if 'DIFFUSERS_TEST_DEVICE' in os.environ:
        torch_device = os.environ['DIFFUSERS_TEST_DEVICE']
        try: _ = torch.device(torch_device)
        except RuntimeError as e: raise RuntimeError(f'Unknown testing device specified by environment variable `DIFFUSERS_TEST_DEVICE`: {torch_device}') from e
    else:
        torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
        is_torch_higher_equal_than_1_12 = version.parse(version.parse(torch.__version__).base_version) >= version.parse('1.12')
        if is_torch_higher_equal_than_1_12:
            mps_backend_registered = hasattr(torch.backends, 'mps')
            torch_device = 'mps' if mps_backend_registered and torch.backends.mps.is_available() else torch_device
def torch_all_close(a, b, *args, **kwargs):
    if not is_torch_available(): raise ValueError('PyTorch needs to be installed to use this function.')
    if not torch.allclose(a, b, *args, **kwargs): assert False, f'Max diff is absolute {(a - b).abs().max()}. Diff tensor is {(a - b).abs()}.'
    return True
def numpy_cosine_similarity_distance(a, b):
    similarity = np.dot(a, b) / (norm(a) * norm(b))
    distance = 1.0 - similarity.mean()
    return distance
def print_tensor_test(tensor, limit_to_slices=None, max_torch_print=None, filename='test_corrections.txt', expected_tensor_name='expected_slice'):
    if max_torch_print: torch.set_printoptions(threshold=10000)
    test_name = os.environ.get('PYTEST_CURRENT_TEST')
    if not torch.is_tensor(tensor): tensor = torch.from_numpy(tensor)
    if limit_to_slices: tensor = tensor[0, -3:, -3:, -1]
    tensor_str = str(tensor.detach().cpu().flatten().to(torch.float32)).replace('\n', '')
    output_str = tensor_str.replace('tensor', f'{expected_tensor_name} = np.array')
    test_file, test_class, test_fn = test_name.split('::')
    test_fn = test_fn.split()[0]
    with open(filename, 'a') as f: print('::'.join([test_file, test_class, test_fn, output_str]), file=f)
def get_tests_dir(append_path=None):
    """Args:"""
    caller__file__ = inspect.stack()[1][1]
    tests_dir = os.path.abspath(os.path.dirname(caller__file__))
    while not tests_dir.endswith('tests'): tests_dir = os.path.dirname(tests_dir)
    if append_path: return Path(tests_dir, append_path).as_posix()
    else: return tests_dir
def str_to_bool(value) -> int:
    value = value.lower()
    if value in ('y', 'yes', 't', 'true', 'on', '1'): return 1
    elif value in ('n', 'no', 'f', 'false', 'off', '0'): return 0
    else: raise ValueError(f'invalid truth value {value}')
def parse_flag_from_env(key, default=False):
    try: value = os.environ[key]
    except KeyError: _value = default
    else:
        try: _value = str_to_bool(value)
        except ValueError: raise ValueError(f'If set, {key} must be yes or no.')
    return _value
_run_slow_tests = parse_flag_from_env('RUN_SLOW', default=False)
_run_nightly_tests = parse_flag_from_env('RUN_NIGHTLY', default=False)
_run_compile_tests = parse_flag_from_env('RUN_COMPILE', default=False)
def floats_tensor(shape, scale=1.0, rng=None, name=None):
    if rng is None: rng = global_rng
    total_dims = 1
    for dim in shape: total_dims *= dim
    values = []
    for _ in range(total_dims): values.append(rng.random() * scale)
    return torch.tensor(data=values, dtype=torch.float).view(shape).contiguous()
def slow(test_case): return unittest.skipUnless(_run_slow_tests, 'test is slow')(test_case)
def nightly(test_case): return unittest.skipUnless(_run_nightly_tests, 'test is nightly')(test_case)
def is_torch_compile(test_case): return unittest.skipUnless(_run_compile_tests, 'test is torch compile')(test_case)
def require_torch(test_case): return unittest.skipUnless(is_torch_available(), 'test requires PyTorch')(test_case)
def require_torch_2(test_case): return unittest.skipUnless(is_torch_available() and is_torch_version('>=', '2.0.0'), 'test requires PyTorch 2')(test_case)
def require_torch_version_greater_equal(torch_version):
    def decorator(test_case):
        correct_torch_version = is_torch_available() and is_torch_version('>=', torch_version)
        return unittest.skipUnless(correct_torch_version, f'test requires torch with the version greater than or equal to {torch_version}')(test_case)
    return decorator
def require_torch_gpu(test_case): return unittest.skipUnless(is_torch_available() and torch_device == 'cuda', 'test requires PyTorch+CUDA')(test_case)
def require_torch_accelerator(test_case): return unittest.skipUnless(is_torch_available() and torch_device != 'cpu', 'test requires accelerator+PyTorch')(test_case)
def require_torch_multi_gpu(test_case):
    if not is_torch_available(): return unittest.skip('test requires PyTorch')(test_case)
    import torch
    return unittest.skipUnless(torch.cuda.device_count() > 1, 'test requires multiple GPUs')(test_case)
def require_torch_accelerator_with_fp16(test_case): return unittest.skipUnless(_is_torch_fp16_available(torch_device), 'test requires accelerator with fp16 support')(test_case)
def require_torch_accelerator_with_fp64(test_case): return unittest.skipUnless(_is_torch_fp64_available(torch_device), 'test requires accelerator with fp64 support')(test_case)
def require_big_gpu_with_torch_cuda(test_case):
    if not is_torch_available(): return unittest.skip('test requires PyTorch')(test_case)
    import torch
    if not torch.cuda.is_available(): return unittest.skip('test requires PyTorch CUDA')(test_case)
    device_properties = torch.cuda.get_device_properties(0)
    total_memory = device_properties.total_memory / 1024 ** 3
    return unittest.skipUnless(total_memory >= BIG_GPU_MEMORY, f'test requires a GPU with at least {BIG_GPU_MEMORY} GB memory')(test_case)
def require_torch_accelerator_with_training(test_case): return unittest.skipUnless(is_torch_available() and backend_supports_training(torch_device), 'test requires accelerator with training support')(test_case)
def skip_mps(test_case): return unittest.skipUnless(torch_device != 'mps', "test requires non 'mps' device")(test_case)
def require_flax(test_case): return unittest.skipUnless(is_flax_available(), 'test requires JAX & Flax')(test_case)
def require_compel(test_case): return unittest.skipUnless(is_compel_available(), 'test requires compel')(test_case)
def require_onnxruntime(test_case): return unittest.skipUnless(is_onnx_available(), 'test requires onnxruntime')(test_case)
def require_note_seq(test_case): return unittest.skipUnless(is_note_seq_available(), 'test requires note_seq')(test_case)
def require_accelerator(test_case): return unittest.skipUnless(torch_device != 'cpu', 'test requires a hardware accelerator')(test_case)
def require_torchsde(test_case): return unittest.skipUnless(is_torchsde_available(), 'test requires torchsde')(test_case)
def require_peft_backend(test_case): return unittest.skipUnless(USE_PEFT_BACKEND, 'test requires PEFT backend')(test_case)
def require_timm(test_case): return unittest.skipUnless(is_timm_available(), 'test requires timm')(test_case)
def require_sapiens_machine(test_case): return unittest.skipUnless(is_sapiens_machine_available(), 'test requires sapiens_machine')(test_case)
def require_sapiens_accelerator(test_case): return unittest.skipUnless(is_sapiens_accelerator_available(), 'test requires sapiens_accelerator')(test_case)
def require_peft_version_greater(peft_version):
    def decorator(test_case):
        correct_peft_version = is_peft_available() and version.parse(version.parse(importlib.metadata.version('peft')).base_version) > version.parse(peft_version)
        return unittest.skipUnless(correct_peft_version, f'test requires PEFT backend with the version greater than {peft_version}')(test_case)
    return decorator
def require_sapiens_transformers_version_greater(sapiens_transformers_version):
    def decorator(test_case):
        correct_sapiens_transformers_version = is_transformers_available() and version.parse(version.parse(importlib.metadata.version('sapiens_transformers')).base_version) > version.parse(sapiens_transformers_version)
        return unittest.skipUnless(correct_sapiens_transformers_version, f'test requires transformers with the version greater than {sapiens_transformers_version}')(test_case)
    return decorator
def require_sapiens_accelerator_version_greater(sapiens_accelerator_version):
    def decorator(test_case):
        correct_sapiens_accelerator_version = is_sapiens_accelerator_available() and version.parse(version.parse(importlib.metadata.version('sapiens_accelerator')).base_version) > version.parse(sapiens_accelerator_version)
        return unittest.skipUnless(correct_sapiens_accelerator_version, f'Test requires sapiens_accelerator with the version greater than {sapiens_accelerator_version}.')(test_case)
    return decorator
def require_sapiens_machine_version_greater(sapiens_version):
    def decorator(test_case):
        correct_sapiens_version = is_sapiens_machine_available() and version.parse(version.parse(importlib.metadata.version('sapiens_machine')).base_version) > version.parse(sapiens_version)
        return unittest.skipUnless(correct_sapiens_version, f'Test requires sapiens_machine with the version greater than {sapiens_version}.')(test_case)
    return decorator
def require_gguf_version_greater_or_equal(gguf_version):
    def decorator(test_case):
        correct_gguf_version = is_gguf_available() and version.parse(version.parse(importlib.metadata.version('gguf')).base_version) >= version.parse(gguf_version)
        return unittest.skipUnless(correct_gguf_version, f'Test requires gguf with the version greater than {gguf_version}.')(test_case)
    return decorator
def require_torchao_version_greater_or_equal(torchao_version):
    def decorator(test_case):
        correct_torchao_version = is_torchao_available() and version.parse(version.parse(importlib.metadata.version('torchao')).base_version) >= version.parse(torchao_version)
        return unittest.skipUnless(correct_torchao_version, f'Test requires torchao with version greater than {torchao_version}.')(test_case)
    return decorator
def deprecate_after_peft_backend(test_case): return unittest.skipUnless(not USE_PEFT_BACKEND, 'test skipped in favor of PEFT backend')(test_case)
def get_python_version():
    sys_info = sys.version_info
    major, minor = (sys_info.major, sys_info.minor)
    return (major, minor)
def load_numpy(arry: Union[str, np.ndarray], local_path: Optional[str]=None) -> np.ndarray:
    if isinstance(arry, str):
        if local_path is not None: return Path(local_path, arry.split('/')[-5], arry.split('/')[-2], arry.split('/')[-1]).as_posix()
        elif arry.startswith('http://') or arry.startswith('https://'):
            response = requests.get(arry)
            response.raise_for_status()
            arry = np.load(BytesIO(response.content))
        elif os.path.isfile(arry): arry = np.load(arry)
        else: raise ValueError(f'Incorrect path or url, URLs must start with `http://` or `https://`, and {arry} is not a valid path')
    elif isinstance(arry, np.ndarray): pass
    else: raise ValueError('Incorrect format used for numpy ndarray. Should be an url linking to an image, a local path, or a ndarray.')
    return arry
def load_pt(url: str):
    response = requests.get(url)
    response.raise_for_status()
    arry = torch.load(BytesIO(response.content))
    return arry
def load_image(image: Union[str, PIL.Image.Image]) -> PIL.Image.Image:
    """Returns:"""
    if isinstance(image, str):
        if image.startswith('http://') or image.startswith('https://'): image = PIL.Image.open(requests.get(image, stream=True).raw)
        elif os.path.isfile(image): image = PIL.Image.open(image)
        else: raise ValueError(f'Incorrect path or url, URLs must start with `http://` or `https://`, and {image} is not a valid path')
    elif isinstance(image, PIL.Image.Image): image = image
    else: raise ValueError('Incorrect format used for image. Should be an url linking to an image, a local path, or a PIL image.')
    image = PIL.ImageOps.exif_transpose(image)
    image = image.convert('RGB')
    return image
def preprocess_image(image: PIL.Image, batch_size: int):
    w, h = image.size
    w, h = (x - x % 8 for x in (w, h))
    image = image.resize((w, h), resample=PIL.Image.LANCZOS)
    image = np.array(image).astype(np.float32) / 255.0
    image = np.vstack([image[None].transpose(0, 3, 1, 2)] * batch_size)
    image = torch.from_numpy(image)
    return 2.0 * image - 1.0
def export_to_gif(image: List[PIL.Image.Image], output_gif_path: str=None) -> str:
    if output_gif_path is None: output_gif_path = tempfile.NamedTemporaryFile(suffix='.gif').name
    image[0].save(output_gif_path, save_all=True, append_images=image[1:], optimize=False, duration=100, loop=0)
    return output_gif_path
@contextmanager
def buffered_writer(raw_f):
    f = io.BufferedWriter(raw_f)
    yield f
    f.flush()
def export_to_ply(mesh, output_ply_path: str=None):
    if output_ply_path is None: output_ply_path = tempfile.NamedTemporaryFile(suffix='.ply').name
    coords = mesh.verts.detach().cpu().numpy()
    faces = mesh.faces.cpu().numpy()
    rgb = np.stack([mesh.vertex_channels[x].detach().cpu().numpy() for x in 'RGB'], axis=1)
    with buffered_writer(open(output_ply_path, 'wb')) as f:
        f.write(b'ply\n')
        f.write(b'format binary_little_endian 1.0\n')
        f.write(bytes(f'element vertex {len(coords)}\n', 'ascii'))
        f.write(b'property float x\n')
        f.write(b'property float y\n')
        f.write(b'property float z\n')
        if rgb is not None:
            f.write(b'property uchar red\n')
            f.write(b'property uchar green\n')
            f.write(b'property uchar blue\n')
        if faces is not None:
            f.write(bytes(f'element face {len(faces)}\n', 'ascii'))
            f.write(b'property list uchar int vertex_index\n')
        f.write(b'end_header\n')
        if rgb is not None:
            rgb = (rgb * 255.499).round().astype(int)
            vertices = [(*coord, *rgb) for coord, rgb in zip(coords.tolist(), rgb.tolist())]
            format = struct.Struct('<3f3B')
            for item in vertices: f.write(format.pack(*item))
        else:
            format = struct.Struct('<3f')
            for vertex in coords.tolist(): f.write(format.pack(*vertex))
        if faces is not None:
            format = struct.Struct('<B3I')
            for tri in faces.tolist(): f.write(format.pack(len(tri), *tri))
    return output_ply_path
def export_to_obj(mesh, output_obj_path: str=None):
    if output_obj_path is None: output_obj_path = tempfile.NamedTemporaryFile(suffix='.obj').name
    verts = mesh.verts.detach().cpu().numpy()
    faces = mesh.faces.cpu().numpy()
    vertex_colors = np.stack([mesh.vertex_channels[x].detach().cpu().numpy() for x in 'RGB'], axis=1)
    vertices = ['{} {} {} {} {} {}'.format(*coord, *color) for coord, color in zip(verts.tolist(), vertex_colors.tolist())]
    faces = ['f {} {} {}'.format(str(tri[0] + 1), str(tri[1] + 1), str(tri[2] + 1)) for tri in faces.tolist()]
    combined_data = ['v ' + vertex for vertex in vertices] + faces
    with open(output_obj_path, 'w') as f: f.writelines('\n'.join(combined_data))
def export_to_video(video_frames: List[np.ndarray], output_video_path: str=None) -> str:
    if is_opencv_available(): import cv2
    else: raise ImportError(BACKENDS_MAPPING['opencv'][1].format('export_to_video'))
    if output_video_path is None: output_video_path = tempfile.NamedTemporaryFile(suffix='.mp4').name
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    h, w, c = video_frames[0].shape
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps=8, frameSize=(w, h))
    for i in range(len(video_frames)):
        img = cv2.cvtColor(video_frames[i], cv2.COLOR_RGB2BGR)
        video_writer.write(img)
    return output_video_path
def load_hf_numpy(path) -> np.ndarray:
    base_url = 'https://huggingface.co/datasets/fusing/diffusers-testing/resolve/main'
    if not path.startswith('http://') and (not path.startswith('https://')): path = os.path.join(base_url, urllib.parse.quote(path))
    return load_numpy(path)
pytest_opt_registered = {}
def pytest_addoption_shared(parser):
    option = '--make-reports'
    if option not in pytest_opt_registered:
        parser.addoption(option, action='store', default=False, help='generate report files. The value of this option is used as a prefix to report names')
        pytest_opt_registered[option] = 1
def pytest_terminal_summary_main(tr, id):
    """Args:"""
    from _pytest.config import create_terminal_writer
    if not len(id): id = 'tests'
    config = tr.config
    orig_writer = config.get_terminal_writer()
    orig_tbstyle = config.option.tbstyle
    orig_reportchars = tr.reportchars
    dir = 'reports'
    Path(dir).mkdir(parents=True, exist_ok=True)
    report_files = {k: f'{dir}/{id}_{k}.txt' for k in ['durations', 'errors', 'failures_long', 'failures_short', 'failures_line', 'passes', 'stats', 'summary_short', 'warnings']}
    dlist = []
    for replist in tr.stats.values():
        for rep in replist:
            if hasattr(rep, 'duration'): dlist.append(rep)
    if dlist:
        dlist.sort(key=lambda x: x.duration, reverse=True)
        with open(report_files['durations'], 'w') as f:
            durations_min = 0.05
            f.write('slowest durations\n')
            for i, rep in enumerate(dlist):
                if rep.duration < durations_min:
                    f.write(f'{len(dlist) - i} durations < {durations_min} secs were omitted')
                    break
                f.write(f'{rep.duration:02.2f}s {rep.when:<8} {rep.nodeid}\n')
    def summary_failures_short(tr):
        reports = tr.getreports('failed')
        if not reports: return
        tr.write_sep('=', 'FAILURES SHORT STACK')
        for rep in reports:
            msg = tr._getfailureheadline(rep)
            tr.write_sep('_', msg, red=True, bold=True)
            longrepr = re.sub('.*_ _ _ (_ ){10,}_ _ ', '', rep.longreprtext, 0, re.M | re.S)
            tr._tw.line(longrepr)
    config.option.tbstyle = 'auto'
    with open(report_files['failures_long'], 'w') as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_failures()
    with open(report_files['failures_short'], 'w') as f:
        tr._tw = create_terminal_writer(config, f)
        summary_failures_short(tr)
    config.option.tbstyle = 'line'
    with open(report_files['failures_line'], 'w') as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_failures()
    with open(report_files['errors'], 'w') as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_errors()
    with open(report_files['warnings'], 'w') as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_warnings()
        tr.summary_warnings()
    tr.reportchars = 'wPpsxXEf'
    with open(report_files['passes'], 'w') as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_passes()
    with open(report_files['summary_short'], 'w') as f:
        tr._tw = create_terminal_writer(config, f)
        tr.short_test_summary()
    with open(report_files['stats'], 'w') as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_stats()
    tr._tw = orig_writer
    tr.reportchars = orig_reportchars
    config.option.tbstyle = orig_tbstyle
def is_flaky(max_attempts: int=5, wait_before_retry: Optional[float]=None, description: Optional[str]=None):
    """Args:"""
    def decorator(test_func_ref):
        @functools.wraps(test_func_ref)
        def wrapper(*args, **kwargs):
            retry_count = 1
            while retry_count < max_attempts:
                try: return test_func_ref(*args, **kwargs)
                except Exception as err:
                    if wait_before_retry is not None: time.sleep(wait_before_retry)
                    retry_count += 1
            return test_func_ref(*args, **kwargs)
        return wrapper
    return decorator
def run_test_in_subprocess(test_case, target_func, inputs=None, timeout=None):
    """Args:"""
    if timeout is None: timeout = int(os.environ.get('PYTEST_TIMEOUT', 600))
    start_methohd = 'spawn'
    ctx = multiprocessing.get_context(start_methohd)
    input_queue = ctx.Queue(1)
    output_queue = ctx.JoinableQueue(1)
    input_queue.put(inputs, timeout=timeout)
    process = ctx.Process(target=target_func, args=(input_queue, output_queue, timeout))
    process.start()
    try:
        results = output_queue.get(timeout=timeout)
        output_queue.task_done()
    except Exception as e:
        process.terminate()
        test_case.fail(e)
    process.join(timeout=timeout)
    if results['error'] is not None: test_case.fail(f"{results['error']}")
class CaptureLogger:
    """Returns:"""
    def __init__(self, logger):
        self.logger = logger
        self.io = StringIO()
        self.sh = logging.StreamHandler(self.io)
        self.out = ''
    def __enter__(self):
        self.logger.addHandler(self.sh)
        return self
    def __exit__(self, *exc):
        self.logger.removeHandler(self.sh)
        self.out = self.io.getvalue()
    def __repr__(self): return f'captured: {self.out}\n'
def enable_full_determinism():
    os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':16:8'
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
def disable_full_determinism():
    os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ''
    torch.use_deterministic_algorithms(False)
def _is_torch_fp16_available(device):
    if not is_torch_available(): return False
    import torch
    device = torch.device(device)
    try:
        x = torch.zeros((2, 2), dtype=torch.float16).to(device)
        _ = torch.mul(x, x)
        return True
    except Exception as e:
        if device.type == 'cuda': raise ValueError(f"You have passed a device of type 'cuda' which should work with 'fp16', but 'cuda' does not seem to be correctly installed on your machine: {e}")
        return False
def _is_torch_fp64_available(device):
    if not is_torch_available(): return False
    import torch
    device = torch.device(device)
    try:
        x = torch.zeros((2, 2), dtype=torch.float64).to(device)
        _ = torch.mul(x, x)
        return True
    except Exception as e:
        if device.type == 'cuda': raise ValueError(f"You have passed a device of type 'cuda' which should work with 'fp64', but 'cuda' does not seem to be correctly installed on your machine: {e}")
        return False
if is_torch_available():
    BACKEND_SUPPORTS_TRAINING = {'cuda': True, 'cpu': True, 'mps': False, 'default': True}
    BACKEND_EMPTY_CACHE = {'cuda': torch.cuda.empty_cache, 'cpu': None, 'mps': None, 'default': None}
    BACKEND_DEVICE_COUNT = {'cuda': torch.cuda.device_count, 'cpu': lambda: 0, 'mps': lambda: 0, 'default': 0}
    BACKEND_MANUAL_SEED = {'cuda': torch.cuda.manual_seed, 'cpu': torch.manual_seed, 'default': torch.manual_seed}
def _device_agnostic_dispatch(device: str, dispatch_table: Dict[str, Callable], *args, **kwargs):
    if device not in dispatch_table: return dispatch_table['default'](*args, **kwargs)
    fn = dispatch_table[device]
    if fn is None: return None
    return fn(*args, **kwargs)
def backend_manual_seed(device: str, seed: int): return _device_agnostic_dispatch(device, BACKEND_MANUAL_SEED, seed)
def backend_empty_cache(device: str): return _device_agnostic_dispatch(device, BACKEND_EMPTY_CACHE)
def backend_device_count(device: str): return _device_agnostic_dispatch(device, BACKEND_DEVICE_COUNT)
def backend_supports_training(device: str):
    if not is_torch_available(): return False
    if device not in BACKEND_SUPPORTS_TRAINING: device = 'default'
    return BACKEND_SUPPORTS_TRAINING[device]
if is_torch_available():
    def update_mapping_from_spec(device_fn_dict: Dict[str, Callable], attribute_name: str):
        try:
            spec_fn = getattr(device_spec_module, attribute_name)
            device_fn_dict[torch_device] = spec_fn
        except AttributeError as e:
            if 'default' not in device_fn_dict: raise AttributeError(f"`{attribute_name}` not found in '{device_spec_path}' and no default fallback function found.") from e
    if 'DIFFUSERS_TEST_DEVICE_SPEC' in os.environ:
        device_spec_path = os.environ['DIFFUSERS_TEST_DEVICE_SPEC']
        if not Path(device_spec_path).is_file(): raise ValueError(f'Specified path to device specification file is not found. Received {device_spec_path}')
        try: import_name = device_spec_path[:device_spec_path.index('.py')]
        except ValueError as e: raise ValueError(f'Provided device spec file is not a Python file! Received {device_spec_path}') from e
        device_spec_module = importlib.import_module(import_name)
        try: device_name = device_spec_module.DEVICE_NAME
        except AttributeError: raise AttributeError('Device spec file did not contain `DEVICE_NAME`')
        if 'DIFFUSERS_TEST_DEVICE' in os.environ and torch_device != device_name:
            msg = f"Mismatch between environment variable `DIFFUSERS_TEST_DEVICE` '{torch_device}' and device found in spec '{device_name}'\n"
            msg += 'Either unset `DIFFUSERS_TEST_DEVICE` or ensure it matches device spec name.'
            raise ValueError(msg)
        torch_device = device_name
        update_mapping_from_spec(BACKEND_MANUAL_SEED, 'MANUAL_SEED_FN')
        update_mapping_from_spec(BACKEND_EMPTY_CACHE, 'EMPTY_CACHE_FN')
        update_mapping_from_spec(BACKEND_DEVICE_COUNT, 'DEVICE_COUNT_FN')
        update_mapping_from_spec(BACKEND_SUPPORTS_TRAINING, 'SUPPORTS_TRAINING')
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
