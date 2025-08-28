"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
class Training():
	def __init__(self, base_model_path='', dataset_path='', dataset_string=None, progress=True):
		try:
			model_path = base_model_path.strip() if type(base_model_path) == str else str(base_model_path).strip()
			dataset_path = dataset_path.strip() if type(dataset_path) == str else str(dataset_path).strip()
			dataset_string = dataset_string.strip() if type(dataset_string) == str else None
			progress = bool(progress) if type(progress) in (bool, int, float) else True
			from logging import getLogger, WARNING, ERROR, disable, CRITICAL
			from torch import cuda, device, backends
			from sapiens_transformers.adaptations import STATE1X, STATE1Y, STATE2X, STATE2Y
			from sapiens_transformers.utils.functions import (update_tqdm, set_tqdm, model_conversion, find_config_or_model_index, set_model_type,
			back_model_type, get_dataset_from_file, get_configuration_path, copy_and_overwrite_file)
			from os import path
			from sapiens_transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
			from sapiens_transformers import default_data_collator
			if not progress: set_tqdm(disable=True)
			progress_bar = update_tqdm(total=4, description='Loading model')
			progress_bar.update(1)
			getLogger('sapiens_transformers').setLevel(WARNING)
			getLogger('sapiens_transformers').setLevel(ERROR)
			getLogger('datasets').setLevel(WARNING)
			getLogger('datasets').setLevel(ERROR)
			disable(CRITICAL)
			if cuda.is_available(): local_device = device('cuda')
			elif backends.mps.is_available(): local_device = device('mps')
			else: local_device = device('cpu')
			saf_model_conversion, change_json = bin_model_conversion = False, False
			saf_model_conversion = model_conversion(sapiens_path=model_path, to=STATE1X)
			if not saf_model_conversion: bin_model_conversion = model_conversion(sapiens_path=model_path, to=STATE2X)
			model_path = find_config_or_model_index(model_path=model_path)
			change_json = set_model_type(model_path=model_path)
			progress_bar.update(1)
			model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype='auto').to(local_device)
			progress_bar.update(1)
			tokenizer = AutoTokenizer.from_pretrained(model_path)
			progress_bar.update(1)
			progress_bar.close()
			set_tqdm(disable=True)
			back_model_type(model_path=model_path, change_json=change_json)
			if saf_model_conversion: model_conversion(sapiens_path=model_path, to=STATE1Y)
			elif bin_model_conversion: model_conversion(sapiens_path=model_path, to=STATE2Y)
			dataset = get_dataset_from_file(file_path=dataset_path, string_content=dataset_string)
			configuration_path = get_configuration_path(model_path=model_path)
			self.__default_epochs = len(dataset['train']) * 2
			self.__saf_model_conversion, self.__bin_model_conversion = saf_model_conversion, bin_model_conversion
			self.__model_path, self.__STATE1Y, self.__STATE2Y = model_path, STATE1Y, STATE2Y
			self.__model_conversion, self.__TrainingArguments, self.__Trainer = model_conversion, TrainingArguments, Trainer
			self.__local_device, self.__model, self.__tokenizer, self.__dataset, self.__default_data_collator = local_device, model, tokenizer, dataset, default_data_collator
			self.__progress, self.__set_tqdm, self.__path, self.__configuration_path, self.__copy_and_overwrite_file = progress, set_tqdm, path, configuration_path, copy_and_overwrite_file
			set_tqdm(disable=False)
		except: pass
	def train(self, system_instruction='', precision=0.1, epochs=None, output_path=''):
		try:
			train_loss, system_instruction = 1.0, system_instruction.strip() if type(system_instruction) == str else ''
			precision = min((1, max((0, int(precision))))) if type(precision) in (bool, int, float) else 0.1
			epochs = max((1, int(epochs))) if type(epochs) in (bool, int, float) else None
			output_path = output_path.strip() if type(output_path) == str else ''
			if len(system_instruction) < 1: system_instruction = 'You are Sapiens, a language model created by Sapiens Technology.'
			if epochs is None: epochs = self.__default_epochs
			if len(output_path) < 1: output_path = './sapiens_model'
			try: eos_token = self.__tokenizer.eos_token
			except: eos_token = self.__tokenizer.convert_ids_to_tokens([self.__tokenizer.eos_token_id])
			max_length = self.__model.config.max_position_embeddings
			if not self.__progress: self.__set_tqdm(disable=True)
			def tokenize_function_json(dataset={}):
				formatted_texts = [f'system: {system_instruction} user: {_input} assistant: {_output}{eos_token}' for _input, _output in zip(dataset['input'], dataset['output'])]
				tokenized = self.__tokenizer(formatted_texts, truncation=True, padding='longest', max_length=max_length)
				tokenized['labels'] = tokenized['input_ids'].copy()
				tokenized['labels'] = [[-100 if token == self.__tokenizer.pad_token_id else token for token in label] for label in tokenized['labels']]
				return tokenized
			def __adjust_hyperparameters(precision=0.1):
				precision = min((1, max((0, int(precision))))) if type(precision) in (bool, int, float) else 0.1
				return {'per_device_train_batch_size': int(4 + precision * (128 - 4)), 'gradient_accumulation_steps': int(8 + precision * (64 - 8)),
				'learning_rate': 0.0001 + precision * (0.001 - 0.0001), 'weight_decay': precision * 0.1}
			tokenized_datasets = self.__dataset.map(tokenize_function_json, batched=True)
			hyperparameters = __adjust_hyperparameters(precision=precision)
			per_device_train_batch_size, gradient_accumulation_steps = hyperparameters['per_device_train_batch_size'], hyperparameters['gradient_accumulation_steps']
			learning_rate, weight_decay = hyperparameters['learning_rate'], hyperparameters['weight_decay']
			from tqdm.auto import tqdm
			from sapiens_transformers import TrainerCallback
			class ProgressBarCallback(TrainerCallback):
				def __init__(self, total_epochs=1): self.total_epochs, self.progress_bar = total_epochs, None
				def on_train_begin(self, args=None, state=None, control=None, **kwargs): self.progress_bar = tqdm(total=self.total_epochs, desc='Training Progress', unit=' step')
				def on_epoch_end(self, args=None, state=None, control=None, **kwargs): self.progress_bar.update(1)
				def on_train_end(self, args=None, state=None, control=None, **kwargs): self.progress_bar.close()
			class TrainLossCallback(TrainerCallback):
				def __init__(self): self.train_loss = 1.0
				def on_log(self, args=None, state=None, control=None, logs=None, **kwargs):
					if logs and 'train_loss' in logs: self.train_loss = float(logs["train_loss"])
			train_loss_callback = TrainLossCallback()
			training_arguments = self.__TrainingArguments(output_dir=output_path, per_device_train_batch_size=per_device_train_batch_size, gradient_accumulation_steps=gradient_accumulation_steps,
			num_train_epochs=epochs, learning_rate=learning_rate, weight_decay=weight_decay, fp16=self.__local_device=='cuda', report_to='none', logging_strategy='no', save_strategy='no', disable_tqdm=True)			
			trainer = self.__Trainer(model=self.__model, args=training_arguments, train_dataset=tokenized_datasets['train'], tokenizer=self.__tokenizer, data_collator=self.__default_data_collator)
			trainer.add_callback(ProgressBarCallback(epochs))
			trainer.add_callback(train_loss_callback)
			import sys
			from io import StringIO
			old_stdout = sys.stdout
			sys.stdout = StringIO()
			trainer.train()
			sys.stdout = old_stdout
			train_loss = train_loss_callback.train_loss
			trainer.save_model(output_path)
			self.__tokenizer.save_pretrained(output_path)
			destination_path = self.__path.join(output_path, self.__path.basename(self.__configuration_path))
			if self.__saf_model_conversion: self.__model_conversion(sapiens_path=output_path, to=self.__STATE1Y)
			elif self.__bin_model_conversion: self.__model_conversion(sapiens_path=output_path, to=self.__STATE2Y)
			self.__set_tqdm(disable=False)
			return train_loss if self.__copy_and_overwrite_file(source_path=self.__configuration_path, destination_path=destination_path) else 1.0
		except:
			if self.__saf_model_conversion: self.__model_conversion(sapiens_path=self.__model_path, to=self.__STATE1Y)
			elif self.__bin_model_conversion: self.__model_conversion(sapiens_path=self.__model_path, to=self.__STATE2Y)
			self.__set_tqdm(disable=False)
			return 1.0
class FineTuning():
	def __init__(self, model_path='', output_path='', progress=True):
		try:
			model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
			output_path = output_path.strip() if type(output_path) == str else ''
			progress = bool(progress) if type(progress) in (bool, int, float) else True
			if len(output_path) < 1: output_path = './sapiens_adjusted'
			if len(model_path) < 1: model_path = output_path
			from logging import getLogger, WARNING, ERROR, disable, CRITICAL
			from torch import cuda, device, backends
			from sapiens_transformers.adaptations import STATE1X, STATE1Y, STATE2X, STATE2Y
			from sapiens_transformers.utils.functions import (set_tqdm, update_tqdm, model_conversion, find_config_or_model_index, set_model_type,
			back_model_type, get_configuration_path, copy_and_overwrite_file)
			from sapiens_transformers import AutoModelForCausalLM, AutoTokenizer
			if not progress: set_tqdm(disable=True)
			progress_bar = update_tqdm(total=4, description='Loading model')
			progress_bar.update(1)
			getLogger('sapiens_transformers').setLevel(WARNING)
			getLogger('sapiens_transformers').setLevel(ERROR)
			getLogger('datasets').setLevel(WARNING)
			getLogger('datasets').setLevel(ERROR)
			disable(CRITICAL)
			if cuda.is_available(): local_device = device('cuda')
			elif backends.mps.is_available(): local_device = device('mps')
			else: local_device = device('cpu')
			saf_model_conversion, change_json = bin_model_conversion = False, False
			saf_model_conversion = model_conversion(sapiens_path=model_path, to=STATE1X)
			if not saf_model_conversion: bin_model_conversion = model_conversion(sapiens_path=model_path, to=STATE2X)
			model_path = find_config_or_model_index(model_path=model_path)
			change_json = set_model_type(model_path=model_path)
			progress_bar.update(1)
			model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype='auto').to(local_device)
			progress_bar.update(1)
			tokenizer, dataset_path = AutoTokenizer.from_pretrained(model_path), ''
			progress_bar.update(1)
			progress_bar.close()
			set_tqdm(disable=True)
			back_model_type(model_path=model_path, change_json=change_json)
			if saf_model_conversion: model_conversion(sapiens_path=model_path, to=STATE1Y)
			elif bin_model_conversion: model_conversion(sapiens_path=model_path, to=STATE2Y)
			from tempfile import NamedTemporaryFile
			with NamedTemporaryFile(suffix='.json', delete=False) as temporary_file: dataset_path = temporary_file.name
			configuration_path = get_configuration_path(model_path=model_path)
			self.__saf_model_conversion, self.__bin_model_conversion = saf_model_conversion, bin_model_conversion
			self.__STATE1Y, self.__STATE2Y, self.__model_conversion = STATE1Y, STATE2Y, model_conversion
			self.__local_device, self.__model, self.__tokenizer = local_device, model, tokenizer
			self.__progress, self.__set_tqdm, self.__configuration_path, self.__copy_and_overwrite_file = progress, set_tqdm, configuration_path, copy_and_overwrite_file
			self.__dataset_dictionary, self.__dataset_path, self.__output_path, self.__trainer, self.__number_of_adjustments = {'data': []}, dataset_path, output_path, None, 0
			set_tqdm(disable=False)
		except: pass
	def addFit(self, Input='', Output=''):
		try:
			Input = Input.strip() if type(Input) == str else str(Input).strip()
			Output = Output.strip() if type(Output) == str else str(Output).strip()
			if not self.__progress: self.__set_tqdm(disable=True)
			self.__number_of_adjustments += 1
			from sapiens_transformers.utils.functions import update_tqdm, get_dataset_from_file
			progress_bar = update_tqdm(total=5, description='Adding adjustment '+str(self.__number_of_adjustments))
			progress_bar.update(1)
			self.__dataset_dictionary['data'].append({'input': Input, 'output': Output})
			from json import dump
			with open(self.__dataset_path, 'w', encoding='utf-8') as file: dump(self.__dataset_dictionary, file)
			self.__set_tqdm(disable=True)
			dataset = get_dataset_from_file(file_path=self.__dataset_path)
			try: eos_token = self.__tokenizer.eos_token
			except: eos_token = self.__tokenizer.convert_ids_to_tokens([self.__tokenizer.eos_token_id])
			max_length = self.__model.config.max_position_embeddings
			default_epochs = len(self.__dataset_dictionary['data']) + 10
			def tokenize_function_json(dataset={}):
				formatted_texts = [f'user: {_input} assistant: {_output}{eos_token}' for _input, _output in zip(dataset['input'], dataset['output'])]
				tokenized = self.__tokenizer(formatted_texts, truncation=True, padding='longest', max_length=max_length)
				tokenized['labels'] = tokenized['input_ids'].copy()
				tokenized['labels'] = [[-100 if token == self.__tokenizer.pad_token_id else token for token in label] for label in tokenized['labels']]
				return tokenized
			def __adjust_hyperparameters(precision=0.1):
				precision = min((1, max((0, int(precision))))) if type(precision) in (bool, int, float) else 0.1
				return {'per_device_train_batch_size': int(4 + precision * (128 - 4)), 'gradient_accumulation_steps': int(8 + precision * (64 - 8)),
				'learning_rate': 0.0001 + precision * (0.001 - 0.0001), 'weight_decay': precision * 0.1}
			tokenized_datasets = dataset.map(tokenize_function_json, batched=True)
			if self.__progress: self.__set_tqdm(disable=False)
			progress_bar.update(1)
			hyperparameters = __adjust_hyperparameters()
			per_device_train_batch_size, gradient_accumulation_steps = hyperparameters['per_device_train_batch_size'], hyperparameters['gradient_accumulation_steps']
			learning_rate, weight_decay = hyperparameters['learning_rate'], hyperparameters['weight_decay']
			progress_bar.update(1)
			from sapiens_transformers import TrainingArguments, Trainer
			training_arguments = TrainingArguments(output_dir=self.__output_path, per_device_train_batch_size=per_device_train_batch_size, gradient_accumulation_steps=gradient_accumulation_steps,
			num_train_epochs=default_epochs, learning_rate=learning_rate, weight_decay=weight_decay, fp16=self.__local_device=='cuda', report_to='none', logging_strategy='no', save_strategy='no', disable_tqdm=True)
			progress_bar.update(1)
			from sapiens_transformers import default_data_collator
			self.__trainer = Trainer(model=self.__model, args=training_arguments, train_dataset=tokenized_datasets['train'], tokenizer=self.__tokenizer, data_collator=default_data_collator)
			progress_bar.update(1)
			progress_bar.close()
			self.__set_tqdm(disable=False)
			return True
		except:
			self.__set_tqdm(disable=False)
			return False
	def fit(self):
		try:
			from sapiens_transformers import TrainerCallback
			class TrainLossCallback(TrainerCallback):
				def __init__(self): self.train_loss = 1.0
				def on_log(self, args=None, state=None, control=None, logs=None, **kwargs):
					if logs and 'train_loss' in logs: self.train_loss = float(logs["train_loss"])
			train_loss_callback = TrainLossCallback()
			self.__trainer.add_callback(train_loss_callback)
			import sys
			from io import StringIO
			old_stdout = sys.stdout
			sys.stdout = StringIO()
			self.__trainer.train()
			sys.stdout = old_stdout
			train_loss = train_loss_callback.train_loss
			self.__trainer.save_model(self.__output_path)
			self.__tokenizer.save_pretrained(self.__output_path)
			from os import path
			destination_path = path.join(self.__output_path, path.basename(self.__configuration_path))
			if self.__saf_model_conversion: self.__model_conversion(sapiens_path=self.__output_path, to=self.__STATE1Y)
			elif self.__bin_model_conversion: self.__model_conversion(sapiens_path=self.__output_path, to=self.__STATE2Y)
			self.__set_tqdm(disable=False)
			return train_loss if self.__copy_and_overwrite_file(source_path=self.__configuration_path, destination_path=destination_path) else 1.0
		except:
			self.__set_tqdm(disable=False)
			return 1.0
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
