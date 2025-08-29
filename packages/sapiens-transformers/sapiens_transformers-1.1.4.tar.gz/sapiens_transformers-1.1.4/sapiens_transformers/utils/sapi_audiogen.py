"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
class SAPIAudioGen():
	def __init__(self, model_path='', local_device='', progress_bar=False):
		model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
		local_device = local_device.lower().strip() if type(local_device) == str else str(local_device).lower().strip()
		progress_bar, gpt_max_text_tokens = bool(progress_bar) if type(progress_bar) in (bool, int, float) else False, 400
		from os import path, environ
		if path.isdir(model_path):
			from contextlib import contextmanager, redirect_stdout
			import sys
			from os import devnull
			from warnings import catch_warnings, simplefilter, filterwarnings
			from torch import set_default_device
			from json import load, dump, JSONDecodeError
			from TTS.api import TTS as sapi_audiogen
			@contextmanager
			def suppress_output():
			    original_stdout, original_stderr = sys.stdout, sys.stderr
			    null_output = open(devnull, 'w')
			    try:
			        sys.stdout = sys.stderr = null_output
			        with catch_warnings():
			            simplefilter("ignore")
			            yield
			    finally:
			        sys.stdout, sys.stderr = original_stdout, original_stderr
			        null_output.close()
			def __filterwarnings():
				filterwarnings('ignore', category=FutureWarning)
				filterwarnings('ignore', message='GPT2InferenceModel has generative capabilities')
				filterwarnings('ignore', message='The attention mask is not set')
			__filterwarnings()
			environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'
			if len(local_device) < 1:
				from torch import cuda, device, backends
				if cuda.is_available(): local_device = device('cuda')
				elif backends.mps.is_available(): local_device = device('mps')
				else: local_device = device('cpu')
			def __set_default_device(): set_default_device(local_device)
			__set_default_device()
			def __get_attribute_values(json_path=''):
				try:
					with open(json_path, 'r', encoding='utf-8') as file: data = load(file)
					model, model_args = data.get('model', ''), data.get('model_args', {})
					gpt_max_text_tokens = model_args.get('gpt_max_text_tokens', 400)
					return (model, gpt_max_text_tokens)
				except (JSONDecodeError, FileNotFoundError, IOError): return ''
			def __update_model_in_configuration(file_path='', old_model='', new_model=''):
				try:
					with open(file_path, 'r', encoding='utf-8') as file: configuration = load(file)
					if configuration.get('model') == old_model:
						configuration['model'] = new_model
						with open(file_path, 'w', encoding='utf-8') as file: dump(configuration, file, indent=4, ensure_ascii=False)
						return True
					return False
				except (JSONDecodeError, FileNotFoundError, IOError): return False
			def __set_model_to_xtts(file_path=''): return __update_model_in_configuration(file_path=file_path, old_model='sapi_audiogen', new_model='xtts')
			def __set_model_to_sapi_audiogen(file_path=''): return __update_model_in_configuration(file_path=file_path, old_model='xtts', new_model='sapi_audiogen')
			configuration_path = path.join(model_path, 'config.json')
			model_type, gpt_max_text_tokens = __get_attribute_values(json_path=configuration_path)
			if model_type == 'sapi_audiogen': __set_model_to_xtts(file_path=configuration_path)
			with suppress_output():
				with open(devnull, 'w') as _devnull:
					with redirect_stdout(_devnull):
						with catch_warnings():
							simplefilter('ignore')
							__sapi_audiogen = sapi_audiogen(model_path=model_path, config_path=configuration_path, gpu=local_device=='cuda', progress_bar=progress_bar)
							if local_device == 'mps': __sapi_audiogen.synthesizer = __sapi_audiogen.synthesizer.to('mps')
			if model_type == 'sapi_audiogen': __set_model_to_sapi_audiogen(file_path=configuration_path)
			self.__filterwarnings, self.__set_default_device, self.__suppress_output, self.__devnull, self.__redirect_stdout, self.__catch_warnings, self.__simplefilter, self.__sapi_audiogen = __filterwarnings, __set_default_device, suppress_output, devnull, redirect_stdout, catch_warnings, simplefilter, __sapi_audiogen
		else: self.__filterwarnings, self.__set_default_device, self.__suppress_output, self.__devnull, self.__redirect_stdout, self.__catch_warnings, self.__simplefilter, self.__sapi_audiogen = None, None, None, None, None, None, None, None
		self.__path, self.__model_path, self.__gpt_max_text_tokens = path, model_path, gpt_max_text_tokens
	def text_to_speech(self, text='', voice_file_path='', output_path='', language='en'):
		text = text.strip() if type(text) == str else str(text).strip()
		voice_file_path = voice_file_path.strip() if type(voice_file_path) == str else str(voice_file_path).strip()
		output_path = output_path.strip() if type(output_path) == str else str(output_path).strip()
		language = language.lower().strip() if type(language) == str else str(language).lower().strip()
		self.__filterwarnings()
		self.__set_default_device()
		if len(output_path) < 1: output_path = './VOICE.wav'
		extension = str(self.__path.splitext(output_path)[1]).strip()
		if len(extension) < 1: output_path += '.wav'
		def __find_wav_file(model_path='', language='en'):
			from os import walk
			first_wav, prioritized_wav = '', ''
			for root, _, files in walk(model_path):
				for file in files:
					if file.lower().endswith('.wav'):
						file_path = self.__path.join(root, file)
						if file.startswith(language): return file_path
						if file.endswith(language + '.wav') and not prioritized_wav: prioritized_wav = file_path
						if not first_wav: first_wav = file_path
			return prioritized_wav if prioritized_wav else first_wav
		if len(voice_file_path) < 1: voice_file_path = __find_wav_file(model_path=self.__model_path, language=language)
		def __split_text(text='', max_tokens=100, encoding_name='cl100k_base'):
			from tiktoken import get_encoding
			from re import split
			encoding = get_encoding(encoding_name)
			tokens = encoding.encode(text)
			if len(tokens) <= max_tokens: return [text]
			sentences = split(r'(\.|\!|\?|\;|\n)', text)
			parts, current_part = [], ''
			for index in range(0, len(sentences) - 1, 2):
				sentence = sentences[index] + (sentences[index + 1] if index + 1 < len(sentences) else '')
				sentence_tokens = encoding.encode(sentence)
				if len(encoding.encode(current_part)) + len(sentence_tokens) <= max_tokens: current_part += sentence
				else:
					parts.append(current_part.strip())
					current_part = sentence
			if current_part: parts.append(current_part.strip())
			return parts
		tokens_list, voice_path, voices_base64 = __split_text(text=text, max_tokens=self.__gpt_max_text_tokens, encoding_name='cl100k_base'), output_path, []
		from tempfile import NamedTemporaryFile
		def __file_to_base64(state=True, path=''):
			if state and len(path) > 0:
				from base64 import b64encode
				with open(path, 'rb') as file: result = b64encode(file.read()).decode('utf-8')
				from os import unlink
				unlink(path)
			return result
		def __merge_base64_wav(voices_base64=[], output_path=''):
			from base64 import b64decode
			from io import BytesIO
			from wave import open as open_wav
			from numpy import frombuffer, int16, concatenate
			sample_width, frame_rate, channels, audio_data = None, None, None, []
			for b64_audio in voices_base64:
				decoded_audio = b64decode(b64_audio)
				with open_wav(BytesIO(decoded_audio), 'rb') as wav_file:
					if sample_width is None: sample_width, frame_rate, channels = wav_file.getsampwidth(), wav_file.getframerate(), wav_file.getnchannels()
					if (wav_file.getsampwidth() != sample_width or wav_file.getframerate() != frame_rate or wav_file.getnchannels() != channels): return False
					frames = frombuffer(wav_file.readframes(wav_file.getnframes()), dtype=int16)
					audio_data.append(frames)
			merged_audio = concatenate(audio_data)
			with open_wav(output_path, 'wb') as output_wav:
				output_wav.setnchannels(channels)
				output_wav.setsampwidth(sample_width)
				output_wav.setframerate(frame_rate)
				output_wav.writeframes(merged_audio.tobytes())
			return True
		for tokens in tokens_list:
			with NamedTemporaryFile(suffix='.wav', delete=False) as temporary_file: voice_path = temporary_file.name
			with self.__suppress_output():
				with open(self.__devnull, 'w') as _devnull:
					with self.__redirect_stdout(_devnull):
						with self.__catch_warnings():
							self.__simplefilter('ignore')
							self.__sapi_audiogen.tts_to_file(text=tokens, file_path=voice_path, speaker_wav=voice_file_path, language=language)
							state = self.__path.isfile(voice_path)
							voice_base64 = __file_to_base64(state=state, path=voice_path)
							voices_base64.append(voice_base64)
		if len(voices_base64) > 0: __merge_base64_wav(voices_base64=voices_base64, output_path=output_path)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
