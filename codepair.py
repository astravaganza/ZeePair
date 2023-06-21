import base64, time, json
import requests, uuid
import config
import logging

class ZeePair(object):
	def __init__(self):
		"""
		Initialises the ZeePair Object
		"""
		self.session = requests.Session()
		self.session.headers.update({'User-Agent': 'okhttp/4.9.3'})
		
		self.device_id = self.gen_uuid()
		self.esk = self.gen_esk()
		
		self.session.headers.update({
				'device_id': self.device_id,
				'token': self.device_id,
				'esk': self.esk
			})


	def get_code(self) -> str:
		"""
		Obtains the alphanumeric codepair code
		"""
		s = self.session.post(url=config.CODE_URL, params={
				'device_name': config.DEVICE_DICT['android_tv'] # use android tv
			}).json()

		return s['device_code']

	def get_token(self, code: str) -> dict:
		"""
		Retrieves the token after codepair is done
		by the client
		"""
		s = self.session.post(url=config.TOKEN_URL, params={
				'device_code': code,
				'device_name': config.DEVICE_DICT['android_tv']
			}).json()

		if s.get('token'):
			return s
		else:
			input("Codepair hasn't been initiated by the client. Please try again and press enter.")
			self.get_token(code)

	def gen_uuid(self) -> str:
		"""
		Generates a random uuid4 to be used as the device's
		unique id
		"""
		uuid4 = str(uuid.uuid4())

		logging.info("Generated UUID " + uuid4)
		return uuid4

	def gen_esk(self) -> bytes: 
		"""
		Generates the ESK based on the algorithm grabbed from 
		ZEETV APK
		"""
		esk_string = f'{self.device_id}__{config.ESK_SECRET_KEY}__{int(time.time()) * 1000}' 

		return base64.b64encode(esk_string.encode())
	
	def dump(self, token: dict) -> None:
		"""
		Dumps the token json to a file
		"""
		with open('token.json', 'w') as f:
			json.dump(token, f, indent=4)

def main() -> None:
	logging.info("ZEE5 Codepair Tool")
	
	zeepair = ZeePair()
	code = zeepair.get_code()

	input("Please Codepair using: " + code + " and press enter")

	zeepair.dump(zeepair.get_token(code))

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	main()
