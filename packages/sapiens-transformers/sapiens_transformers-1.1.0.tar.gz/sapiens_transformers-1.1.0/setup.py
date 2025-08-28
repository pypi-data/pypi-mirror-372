"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from setuptools import setup, find_packages
package_name = 'sapiens_transformers'
version = '1.1.0'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    install_requires=[
        'transformers==4.45.2',
        'huggingface-hub==0.28.1',
        'requests',
        'certifi==2024.2.2',
        'tqdm',
        'numpy==1.25.2',
        'torch==2.4.1',
        'torchvision==0.19.1',
        'torchaudio==2.4.1',
        'accelerate==1.3.0',
        'sapiens-machine==1.0.9',
        'sapiens-accelerator==1.0.5',
        'tokenizers==0.20.1',
        'regex==2024.9.11',
        'datasets',
        'sentencepiece==0.2.0',
        'protobuf',
        'optimum==1.23.3',
        'einops==0.8.0',
        'nemo-toolkit==2.1.0',
        'hydra-core==1.3.2',
        'lightning==2.5.0',
        'braceexpand==0.1.7',
        'webdataset==0.2.100',
        'h5py==3.12.1',
        'ijson==3.3.0',
        'matplotlib==3.10.0',
        'diffusers==0.32.2',
        'moviepy==1.0.3',
        'llama-cpp-python==0.3.6',
        'llamacpp==0.1.14',
        'beautifulsoup4==4.12.3',
        'ftfy==6.3.1',
        'tiktoken==0.4.0',
        'opencv-python',
        'scipy==1.15.1',
        'pydub==0.25.1',
        'megatron-core==0.10.0'
    ],
    extras_require={
        'multimedia': [
            'pyav==14.1.0; python_version<"3.12"',
            'TTS==0.22.0; python_version<"3.12"',
            'av; python_version>="3.12"'
        ],
        'toolkit': ['nemo-toolkit[all]==2.1.0']
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
