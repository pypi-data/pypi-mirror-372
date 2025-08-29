"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from setuptools import setup, find_packages
package_name = 'sapiens_transformers'
version = '1.1.1'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    install_requires=[
        'transformers',
        'huggingface-hub',
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
        'datasets',
        'sentencepiece',
        'protobuf',
        'optimum',
        'einops',
        'nemo-toolkit',
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
        'tiktoken',
        'opencv-python',
        'scipy',
        'pydub',
        'megatron-core'
    ],
    extras_require={
        'multimedia': [
            'pyav; python_version<"3.12"',
            'TTS; python_version<"3.12"',
            'av; python_version>="3.12"'
        ],
        'toolkit': ['nemo-toolkit[all]']
    },
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
