import pandas as pd
import zlib
import pickle
import os

class Dummy:
	def __init__(self, log=False):
		self.currentFrame = None
		self.logging = log

	def create(self, **kwargs):
		if kwargs.get('messages'):
			df = pd.DataFrame(kwargs.get('messages'))
			df['role'] = df['role'].astype('category')
			df['content'] = df['content'].apply(lambda x: zlib.compress(x.encode()))  # Сжатие content
			self.currentFrame = df
		elif kwargs.get('prompt'):
			# Обработка ImageData
			ImageData = {
				'prompt': kwargs.get('prompt', 'anime neko girl'),
				'samples': int(kwargs.get('samples', 1)),
				'resolution': kwargs.get('resolution', (768, 512)),
				'negative_prompt': kwargs.get('negative_prompt', 'painting, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, deformed, ugly, blurry, bad anatomy, bad proportions, extra limbs, cloned face, skinny, glitchy, double torso, extra arms, extra hands, mangled fingers, missing lips, ugly face, distorted face, extra legs'),
				'seed': kwargs.get('seed', -1),
				'steps': int(kwargs.get('steps', 50))
			}
			df = pd.DataFrame([ImageData])
			# Оптимизация типов
			df['prompt'] = df['prompt'].astype('string')
			df['samples'] = df['samples'].astype('int8')
			df['seed'] = df['seed'].astype('int32')
			df['steps'] = df['steps'].astype('int8')
			df['negative_prompt'] = df['negative_prompt'].apply(lambda x: zlib.compress(x.encode()))
			df['res_width'] = df['resolution'].apply(lambda x: x[0]).astype('int16')
			df['res_height'] = df['resolution'].apply(lambda x: x[1]).astype('int16')
			df = df.drop('resolution', axis=1)
			self.currentFrame = df
		else:
			raise Exception('Unknown type.')

		if self.logging:
			print(f'[DUMMY] usage RAM (in bytes): {self.currentFrame.memory_usage(deep=True).sum()}')
		return self

	def save(self, filename='./context/data.bin'):
		"""Сохранение данных в .bin с сжатием zlib"""
		if self.currentFrame is None:
			raise ValueError("No data to save")
		# Создаем директорию, если она не существует
		os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
		compressed_data = zlib.compress(pickle.dumps(self.currentFrame))
		with open(filename, 'wb') as f:
			f.write(compressed_data)
		if self.logging:
			print(f'[DUMMY] Saved to {filename}, size (bytes): {len(compressed_data)}')

	def load(self, filename='./context/data.bin'):
		"""Загрузка данных из .bin с разжатием zlib"""
		os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
		try:
			with open(filename, 'rb') as f:
				compressed_data = f.read()
		except FileNotFoundError:
			raise FileNotFoundError(f"File {filename} not found")
		self.currentFrame = pickle.loads(zlib.decompress(compressed_data))
		# Восстановление оптимизированных типов
		if 'role' in self.currentFrame.columns:
			self.currentFrame['role'] = self.currentFrame['role'].astype('category')
		if 'prompt' in self.currentFrame.columns:
			self.currentFrame['prompt'] = self.currentFrame['prompt'].astype('string')
			self.currentFrame['samples'] = self.currentFrame['samples'].astype('int8')
			self.currentFrame['seed'] = self.currentFrame['seed'].astype('int32')
			self.currentFrame['steps'] = self.currentFrame['steps'].astype('int8')
			self.currentFrame['res_width'] = self.currentFrame['res_width'].astype('int16')
			self.currentFrame['res_height'] = self.currentFrame['res_height'].astype('int16')
		if self.logging:
			print(f'[DUMMY] Loaded from {filename}, RAM usage (bytes): {self.currentFrame.memory_usage(deep=True).sum()}')
		return self

	def get_data(self):
		"""Метод для извлечения данных из currentFrame с разжатием."""
		if self.currentFrame is None:
			return None
		df = self.currentFrame.copy()
		if 'content' in df.columns:
			df['content'] = df['content'].apply(lambda x: zlib.decompress(x).decode())
			return df.to_dict('records')
		elif 'prompt' in df.columns:
			df['negative_prompt'] = df['negative_prompt'].apply(lambda x: zlib.decompress(x).decode())
			df['resolution'] = df.apply(lambda row: (row['res_width'], row['res_height']), axis=1)
			return df[['prompt', 'samples', 'resolution', 'negative_prompt', 'seed', 'steps']].to_dict('records')
		return None