"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
def set_tqdm(disable=True):
	try:
		disable = bool(disable) if type(disable) in (bool, int, float) else True
		from tqdm import tqdm
		from functools import partialmethod
		tqdm.__init__ = partialmethod(tqdm.__init__, disable=disable)
		return True
	except: return False
def update_tqdm(total=1, description=''):
	try:
		total = int(total) if type(total) in (int, float) else 1
		description = description.strip() if type(description) == str else str(description).strip()
		from tqdm import tqdm
		progress_bar = tqdm(total=total, desc=description, position=0, leave=True)
		return progress_bar
	except: return False
def model_conversion(sapiens_path='', to=''):
    try:
        sapiens_path = sapiens_path.strip() if type(sapiens_path) == str else str(sapiens_path).strip()
        to = to.lower().strip() if type(to) == str else str(to).lower().strip()
        from os import path
        if not path.isdir(sapiens_path): return False
        from sapiens_transformers.adaptations import STATE1X, STATE1Y, STATE2X, STATE2Y
        from glob import glob
        from os import rename
        if to == STATE1X: files, new_extension = glob(path.join(sapiens_path, '**', f'*.{STATE1Y}'), recursive=True), STATE1X
        elif to == STATE1Y: files, new_extension = glob(path.join(sapiens_path, '**', f'*.{STATE1X}'), recursive=True), STATE1Y
        elif to == STATE2X: files, new_extension = glob(path.join(sapiens_path, '**', f'*.{STATE2Y}'), recursive=True), STATE2X
        elif to == STATE2Y: files, new_extension = glob(path.join(sapiens_path, '**', f'*.{STATE2X}'), recursive=True), STATE2Y
        else: return False
        if not files: return False
        for old_path in files: rename(old_path, old_path.rsplit('.', 1)[0] + f'.{new_extension}')
        return True
    except: return False
def find_config_or_model_index(model_path=''):
	model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
	try:
		from os import walk
		for root, dirs, files in walk(model_path):
			if 'config.json' in files or 'model_index.json' in files: return root
	finally: return model_path
def get_configuration_path(model_path=''):
	model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
	try:
		from os import path
		if len(model_path) < 1 or not path.isdir(model_path): model_path = './'
		if not model_path.endswith('/'): model_path += '/'
		configuration_path = model_path+'config.json'
		if not path.isfile(configuration_path): configuration_path = model_path+'model_index.json'
		return configuration_path
	except: return './config.json'
def get_dictionary_from_json(configuration_path=''):
    configuration_json, content = {}, ''
    configuration_path = configuration_path.strip() if type(configuration_path) == str else str(configuration_path).strip()
    with open(configuration_path, 'r', encoding='utf-8') as file: content = str(file.read()).strip()
    try:
        from json import loads
        configuration_json = loads(content)
    except:
        from ast import literal_eval
        configuration_json = literal_eval(content)
    return configuration_json
def search_model_type(data={}, return_key=False):
	try:
		data = dict(data) if type(data) in (tuple, list, dict) else {}
		return_key = bool(return_key) if type(return_key) in (bool, int, float) else False
		if not isinstance(data, dict): return '-'
		if 'model_type' in data:
			key = 'model_type'
			return (data['model_type'], key) if return_key else data['model_type']
		if 'model' in data:
			model = str(data['model']).lower().strip()
			key = 'model'
			return (model, key) if return_key else model
		if 'architectures' in data:
			architectures = data['architectures']
			for architecture in architectures:
				architecture = str(architecture).lower().strip()
				if 'for' in architecture:
					key = 'architectures'
					return a(rchitecture.split('for')[0].strip(), key) if return_key else architecture.split('for')[0].strip()
		if '_class_name' in data:
			_class_name = str(data['_class_name']).lower().strip()
			key = '_class_name'
			return (_class_name.split('pipeline')[0].strip(), key) if return_key else _class_name.split('pipeline')[0].strip()
		for value in data.values():
			if isinstance(value, dict):
			    result = search_model_type(value)
			    if result: return result
		return ('-', '-') if return_key else '-'
	except: return ('-', '-') if return_key else '-'
def change_json_key_value(json_path='', key_name='', new_value=''):
	try:
		json_path = json_path.strip() if type(json_path) == str else str(json_path).strip()
		from os import path
		existing_file = len(json_path) > 0 and path.isfile(json_path)
		if existing_file:
			key_name = key_name.strip() if type(key_name) == str else str(key_name).strip()
			from json import load, dump
			def update_key(dictionary):
				if isinstance(dictionary, dict):
					for dictionary_key in dictionary:
						if dictionary_key == key_name: dictionary[dictionary_key] = new_value
						else: update_key(dictionary[dictionary_key])
				elif isinstance(dictionary, list):
					for list_item in dictionary: update_key(list_item)
			try:
				with open(json_path, 'r', encoding='utf-8') as file: data = load(file)
			except: data = get_dictionary_from_json(configuration_path=json_path)
			update_key(data)
			with open(json_path, 'w', encoding='utf-8') as file: dump(data, file, indent=4, ensure_ascii=False)
			return True
		else:
			print('Path: '+file_path)
			print('The given file json does not exist at the specified path.')
			return False
	except Exception as error:
		print('ERROR: '+str(error))
		return False
def get_dataset_from_file(file_path='', string_content=None):
	try:
		dataset = {}
		file_path, is_json_file = file_path.strip() if type(file_path) == str else str(file_path).strip(), False
		from os import path
		existing_file, existing_string = len(file_path) > 0 and path.isfile(file_path), string_content is not None
		if existing_file or existing_string:
			is_json_file = file_path.lower().endswith('.json')
			from datasets import load_dataset
			if is_json_file: dataset = load_dataset('json', data_files={'train': file_path}, field='data')
			else:
				file_data, temporary_file = {'data': []}, ''
				def remove_blank_lines(text=''):
					from re import sub
					return sub(r'\n\s*\n', '\n', str(text)).strip()
				content = original_content = ''
				if existing_string: string_content = string_content.strip() if type(string_content) == str else str(string_content).strip()
				if existing_file:
					with open(file_path, 'r', encoding='utf-8') as file: content = original_content = remove_blank_lines(file.read())
				if existing_string and len(string_content) > 0: content = original_content = '\n'.join((original_content, string_content)).strip()
				ponctuations = ('?', ':', '.', ';', '!')
				for ponctuation in ponctuations:
					lines_with_content, number_of_inputs = content.count('\n') + 1, content.count(ponctuation)
					if lines_with_content == number_of_inputs or lines_with_content == (number_of_inputs * 2):
						content, separator = content.replace(f'{ponctuation}\n', f'{ponctuation} '), '\n'
						inputs_outputs = content.split(separator)
						for input_output in inputs_outputs:
							data = input_output.split(ponctuation)
							first_data, last_data = data[0].strip(), data[-1].strip()
							file_data['data'].append({'input': first_data+ponctuation, 'output': last_data})
						break
				if len(file_data['data']) < 1:
					def process_content(content=''):
						current_segment, punctuation = content.strip(), {'?', '.', '!', ':', ';'}
						while current_segment:
							first_punctuation_position = -1
							for index, character in enumerate(current_segment):
								if character in punctuation:
									first_punctuation_position = index
									break
							if first_punctuation_position == -1: break
							remaining_text, input_text = current_segment[first_punctuation_position + 1:].lstrip(), current_segment[:first_punctuation_position + 1].strip()
							if remaining_text.startswith('```'):
								closing_position = remaining_text.find('```', 3)
								if closing_position == -1: code_content, new_remaining_text = remaining_text[3:].strip(), ''
								else: code_content, new_remaining_text = remaining_text[3:closing_position].strip(), remaining_text[closing_position + 3:].lstrip()
								output_text, current_segment = f'```{code_content}```', new_remaining_text
								file_data['data'].append({'input': input_text, 'output': output_text})
							else:
								next_punctuation_position = -1
								for index, character in enumerate(remaining_text):
									if character in punctuation:
										next_punctuation_position = index
										break
								if next_punctuation_position != -1: output_text, new_remaining_text = remaining_text[:next_punctuation_position + 1].strip(), remaining_text[next_punctuation_position + 1:].lstrip()
								else: output_text, new_remaining_text = remaining_text.strip(), ''
								file_data['data'].append({'input': input_text, 'output': output_text})
								current_segment = new_remaining_text
						return file_data
					file_data = process_content(content=original_content)
				from tempfile import NamedTemporaryFile
				with NamedTemporaryFile(suffix='.json', delete=False) as temporary_file: temporary_path = temporary_file.name
				from json import dump
				with open(temporary_path, 'w', encoding='utf-8') as temporary_file: dump(file_data, temporary_file)
				dataset = load_dataset('json', data_files={'train': temporary_path}, field='data')
				from os import path, remove
				if path.exists(temporary_path): remove(temporary_path)
		else:
			print('Path: '+file_path)
			print('The given data file does not exist at the specified path.')
		return dataset
	except: return {}
def set_model_type(model_path=''):
	try:
		model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
		from os import path
		if len(model_path) < 1 or not path.isdir(model_path): return False
		from sapiens_transformers.adaptations import (HURLM_COMPATIBILITY, SAPI_ZERO_COMPATIBILITY, SAPIENS_COMPATIBILITY, SASTRAL_COMPATIBILITY, MODULAR_ENTITY_COMPATIBILITY,
		SAPIENS_VISION_COMPATIBILITY, SAPI_IMAGE_COMPATIBILITY, SAPIENS_IMAGEGEN_COMPATIBILITY, SAPI_IMAGEGEN_COMPATIBILITY, SAPI_PHOTOGEN_COMPATIBILITY, SAPI_AUDIO_COMPATIBILITY,
		SAPI_AUDIOGEN_COMPATIBILITY, SAPI_MUSICGEN_COMPATIBILITY, SAPI_VIDEO_COMPATIBILITY, SAPIENS_VIDEOGEN_COMPATIBILITY, SAPI_VIDEOGEN_COMPATIBILITY)
		configuration_path, configuration_json, architecture, change_json = get_configuration_path(model_path=model_path), {}, '-', False
		if path.isfile(configuration_path): configuration_json = get_dictionary_from_json(configuration_path=configuration_path)
		else: return False
		architecture, key_name = search_model_type(data=configuration_json, return_key=True)		
		if architecture == HURLM_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=HURLM_COMPATIBILITY[-1])
		elif architecture == SAPI_ZERO_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_ZERO_COMPATIBILITY[-1])
		elif architecture == SAPIENS_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPIENS_COMPATIBILITY[-1])
		elif architecture == SASTRAL_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SASTRAL_COMPATIBILITY[-1])
		elif architecture == MODULAR_ENTITY_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=MODULAR_ENTITY_COMPATIBILITY[-1])
		elif architecture == SAPIENS_VISION_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPIENS_VISION_COMPATIBILITY[-1])
		elif architecture == SAPI_IMAGE_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_IMAGE_COMPATIBILITY[-1])
		elif architecture == SAPIENS_IMAGEGEN_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPIENS_IMAGEGEN_COMPATIBILITY[-1])
		elif architecture == SAPI_IMAGEGEN_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_IMAGEGEN_COMPATIBILITY[-1])
		elif architecture == SAPI_PHOTOGEN_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_PHOTOGEN_COMPATIBILITY[-1])
		elif architecture == SAPI_AUDIO_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_AUDIO_COMPATIBILITY[-1])
		elif architecture == SAPI_AUDIOGEN_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_AUDIOGEN_COMPATIBILITY[-1])
		elif architecture == SAPI_MUSICGEN_COMPATIBILITY[2] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_MUSICGEN_COMPATIBILITY[-2])
		elif architecture == SAPI_VIDEO_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_VIDEO_COMPATIBILITY[-1])
		elif architecture == SAPIENS_VIDEOGEN_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPIENS_VIDEOGEN_COMPATIBILITY[-1])
		elif architecture == SAPI_VIDEOGEN_COMPATIBILITY[0] and key_name in ('model_type', 'model'): change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_VIDEOGEN_COMPATIBILITY[-1])
		return change_json
	except: return False
def back_model_type(model_path='', change_json=True):
	try:
		model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
		change_json = bool(change_json) if type(change_json) in (bool, int, float) else True
		from os import path
		if len(model_path) < 1 or not path.isdir(model_path) or not change_json: return False
		from sapiens_transformers.adaptations import (HURLM_COMPATIBILITY, SAPI_ZERO_COMPATIBILITY, SAPIENS_COMPATIBILITY, SASTRAL_COMPATIBILITY, MODULAR_ENTITY_COMPATIBILITY,
		SAPIENS_VISION_COMPATIBILITY, SAPI_IMAGE_COMPATIBILITY, SAPIENS_IMAGEGEN_COMPATIBILITY, SAPI_IMAGEGEN_COMPATIBILITY, SAPI_PHOTOGEN_COMPATIBILITY, SAPI_AUDIO_COMPATIBILITY,
		SAPI_AUDIOGEN_COMPATIBILITY, SAPI_MUSICGEN_COMPATIBILITY, SAPI_VIDEO_COMPATIBILITY, SAPIENS_VIDEOGEN_COMPATIBILITY, SAPI_VIDEOGEN_COMPATIBILITY)
		configuration_path, configuration_json, architecture = get_configuration_path(model_path=model_path), {}, '-'
		if path.isfile(configuration_path): configuration_json = get_dictionary_from_json(configuration_path=configuration_path)
		else: return False
		architecture, key_name = search_model_type(data=configuration_json, return_key=True)	
		if change_json and architecture == HURLM_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=HURLM_COMPATIBILITY[0])
		elif change_json and architecture == SAPI_ZERO_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_ZERO_COMPATIBILITY[0])
		elif change_json and architecture == SAPIENS_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPIENS_COMPATIBILITY[0])
		elif change_json and architecture == SASTRAL_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SASTRAL_COMPATIBILITY[0])
		elif change_json and architecture == MODULAR_ENTITY_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=MODULAR_ENTITY_COMPATIBILITY[0])
		elif change_json and architecture == SAPIENS_VISION_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPIENS_VISION_COMPATIBILITY[0])
		elif change_json and architecture == SAPI_IMAGE_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_IMAGE_COMPATIBILITY[0])
		elif change_json and architecture == SAPIENS_IMAGEGEN_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPIENS_IMAGEGEN_COMPATIBILITY[0])
		elif change_json and architecture == SAPI_IMAGEGEN_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_IMAGEGEN_COMPATIBILITY[0])
		elif change_json and architecture == SAPI_PHOTOGEN_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_PHOTOGEN_COMPATIBILITY[0])
		elif change_json and architecture == SAPI_AUDIO_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_AUDIO_COMPATIBILITY[0])
		elif change_json and architecture == SAPI_AUDIOGEN_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_AUDIOGEN_COMPATIBILITY[0])
		elif change_json and architecture == SAPI_MUSICGEN_COMPATIBILITY[-2]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_MUSICGEN_COMPATIBILITY[2])
		elif change_json and architecture == SAPI_VIDEO_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_VIDEO_COMPATIBILITY[0])
		elif change_json and architecture == SAPIENS_VIDEOGEN_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPIENS_VIDEOGEN_COMPATIBILITY[0])
		elif change_json and architecture == SAPI_VIDEOGEN_COMPATIBILITY[-1]: change_json = change_json_key_value(json_path=configuration_path, key_name=key_name, new_value=SAPI_VIDEOGEN_COMPATIBILITY[0])
		return change_json
	except: return False
def copy_and_overwrite_file(source_path='', destination_path=''):
	try:
		source_path = source_path.strip() if type(source_path) == str else str(source_path).strip()
		destination_path = destination_path.strip() if type(destination_path) == str else str(destination_path).strip()
		from os import path, remove
		from shutil import copy2
		if path.exists(destination_path): remove(destination_path)
		copy2(source_path, destination_path)
		return True
	except: return False
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
