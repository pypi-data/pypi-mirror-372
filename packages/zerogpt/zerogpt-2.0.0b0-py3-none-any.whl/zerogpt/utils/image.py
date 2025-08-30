import httpx
from PIL import Image
from io import BytesIO
import os

class ZeroImage:
	def __init__(self, images: list):
		self.images = images

	def download(self, path='./__zerogpt__/image.png'):
		if isinstance(path, str):
			path = [path]
		if isinstance(path, list):
			with httpx.Client(http2=True, timeout=30) as client:
				for img, _path in zip(self.images, path):
					os.makedirs(os.path.dirname(_path) or '.', exist_ok=True)
					resp = client.get(img)
					if resp.status_code in [200, 201]:
						with open(_path, 'wb') as file:
							file.write(resp.content)
					else:
						raise Exception('[Error] Unknown')
	def open(self, idx=0):
		with httpx.Client(http2=True, timeout=30) as client:
			resp = client.get(self.images[idx])
			if resp.status_code in [200, 201]:
				img = Image.open(BytesIO(resp.content))
				img.show()
			else:
				raise Exception('[Error] Unknown')