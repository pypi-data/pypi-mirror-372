"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
class DownloadHF():
	def __init__(self, model_path=''):
		model_path = model_path.strip() if type(model_path) == str else str(model_path).strip()
		if 'https://huggingface.co/' in model_path:
			url = model_path
			if url[-1] == '/': url = url[:-1]
			url = url.split('https://huggingface.co/')[-1]
			if url.count('/') > 1:
				url = url.split('/', 2)
				url.pop()
				url = url[0]+'/'+url[-1]
			model_path = url
		try: from huggingface_hub import snapshot_download
		except: snapshot_download = None
		from os import makedirs
		from requests import Session
		session = Session()
		session.timeout = 3600
		self.__model_path, self.__makedirs, self.__snapshot_download = model_path, makedirs, snapshot_download
		self.__warning = 'Set the model name or address in the "model_path" parameter of the class constructor.'
	def native_snapshot_download(self, destination_path=''):
		try:
			if len(self.__model_path) > 0:
				destination_path = destination_path.strip() if isinstance(destination_path, str) else str(destination_path).strip()
				if len(destination_path) < 1: destination_path = self.__model_path.split('/')[-1].strip()
				self.__makedirs(destination_path, exist_ok=True)
				api_url = f'https://huggingface.co/api/models/{self.__model_path}'
				from requests import get
				from os import path
				from tqdm import tqdm
				response = get(api_url)
				if response.status_code != 200: return False
				files = [file['rfilename'] for file in response.json().get('siblings', [])]
				base_url = f'https://huggingface.co/{self.__model_path}/resolve/main/'
				for file in files:
					url = base_url + file
					file_path = path.join(destination_path, file)
					response = get(url, stream=True)
					if response.status_code == 200:
						self.__makedirs(path.dirname(file_path), exist_ok=True)
						total_size = int(response.headers.get('content-length', 0))
						with open(file_path, 'wb') as local_file, tqdm(desc=file, total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as progress_bar:
							for chunk in response.iter_content(chunk_size=8192):
								local_file.write(chunk)
								progress_bar.update(len(chunk))
					else: return False
			else:
				print(self.__warning)
				return False
			return True
		except: return False
	def snapshot_download(self, destination_path=''):
		try:
			if len(self.__model_path) > 0:
				destination_path = destination_path.strip() if type(destination_path) == str else str(destination_path).strip()
				if len(destination_path) < 1: destination_path = self.__model_path.split('/')[-1].strip()
				self.__makedirs(destination_path, exist_ok=True)
				if self.__snapshot_download is None: return self.native_snapshot_download(destination_path=destination_path)
				else: self.__snapshot_download(repo_id=self.__model_path, local_dir=destination_path, force_download=True)
				return True
			else:
				print(self.__warning)
				return False
		except: return self.native_snapshot_download(destination_path=destination_path)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
