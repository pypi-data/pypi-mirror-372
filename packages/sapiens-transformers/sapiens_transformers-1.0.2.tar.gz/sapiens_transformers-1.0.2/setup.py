"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from setuptools import setup, find_packages
package_name = 'sapiens_transformers'
version = '1.0.2'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    install_requires=[
        'transformers',
        'requests',
        'certifi',
        'tqdm',
        'numpy',
        'torch',
        'torchvision',
        'torchaudio',
        'accelerate',
        'sapiens-machine',
        'sapiens-accelerator',
        'tokenizers',
        'regex',
        'huggingface-hub',
        'datasets',
        'sentencepiece',
        'protobuf',
        'optimum',
        'einops',
        'hydra-core',
        'lightning',
        'braceexpand',
        'webdataset',
        'h5py',
        'ijson',
        'matplotlib',
        'diffusers',
        'moviepy',
        'llama-cpp-python',
        'llamacpp',
        'beautifulsoup4',
        'ftfy',
        'av',
        'tiktoken',
        'opencv-python',
        'scipy',
        'TTS',
        'pydub',
        'nemo-toolkit[all]',
        'megatron-core'
    ],
    url='https://github.com/sapiens-technology/sapiens_transformers',
    license='Proprietary Software'
)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
