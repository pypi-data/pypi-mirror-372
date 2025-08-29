import os
import sys
import re
import netrc
import logging
import requests
import json
import pprint
import traceback

logger = logging.getLogger(__name__)
logging.basicConfig(
		format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s",datefmt='%Y-%m-%d %H:%M:%S',
		handlers=[
			logging.StreamHandler(sys.stdout)
		],
		level=logging.INFO
	)


class NotFoundError(Exception):    
	def __init__(self, message):
		super().__init__(message)

class ArgumentNotFoundError(Exception):    
	def __init__(self, message):
		super().__init__(message)
	
class InternalServerError(Exception):    
	def __init__(self, message):
		super().__init__(message)

class PermissionDeniedError(Exception):    
	def __init__(self, message):
		super().__init__(message)

class API:
	
	api_url = "https://openadb.dgfi.tum.de/api/v2/"
	
	def __init__(self, **kwargs):
		
		log_level = kwargs.get('log_level',logging.INFO)
		debug = kwargs.get('debug',0)	
		self.username = None
		self.api_key = kwargs.get('api_key',None)
		
		' set log level '
		logger.setLevel(log_level)
		
		if debug == 1:
			self.api_url = "https://openadb.dgfi.tum.de:8001/api/v2/"
			logger.warning("Debug-API enabled ("+str(self.api_url)+")!")
				
		if self.api_key == None:
			' read credential from ~/.netrc '		
			n = netrc.netrc()
			credentials = n.authenticators('openadb.dgfi.tum.de')
			if credentials == None:
				logger.error('No credentials found in ~/.netrc')
				sys.exit(0)
			
			self.username = credentials[0]
			self.api_key = credentials[2]
			
		logger.info('Username: '+str(self.username))
		logger.info('API-Key: '+str(self.api_key))

		' authenicate user '		
		response = self.send_api_request(
			self.api_url+'auth/',
			{			
				'api_key' :  self.api_key
			}
		)		
		if response.status_code == 200:
			logger.info('Authentication successful!')		
		
	def send_api_request(self, url, args):
		
		
		response = requests.post(url, json=args)							
		if response.status_code == 400:	
			json_response = json.loads(response.text)			
			logger.error('400 - OpenADB-API url not found!')
			raise ArgumentNotFoundError(json_response['message'])
		elif response.status_code == 403:	
			json_response = json.loads(response.text)
			logger.error('403 - Permission denied!')
			raise PermissionDeniedError(json_response['message'])			
		elif response.status_code == 500:
			json_response = json.loads(response.text)
			logger.error('500 - Internal Server Error')			
			raise InternalServerError(json_response['message'])	
					
		return response
		
	def get_mva_config(self, mission):
		
		logger.info('Get MVA config ...')
		
		args = {}
		args['api_key'] = self.api_key
		args['mission'] = mission
		
		response = self.send_api_request(
			self.api_url+'get-mva-config/',
			args
		)
				
		if type(response) == requests.models.Response:
			json_response = json.loads(response.text)
			return json_response
			
		return response
	
	def list_products(self, args):
		
		logger.info('List products ...')
		
		#~ args = {}
		args['api_key'] = self.api_key
		#~ args['mission'] = mission
		
		response = self.send_api_request(
			self.api_url+'list-products/',
			args
		)
		print (response.status_code)
		if type(response) == requests.models.Response:
			json_response = json.loads(response.text)
			return json_response
			
		return response
		
	def search(self, dataset, args={}):
		
		logger.info('Search passes ...')
		
		#~ args = {}
		args['api_key'] = self.api_key
		args['dataset'] = dataset
		#~ args['mission'] = mission
		
		response = self.send_api_request(
			self.api_url+'search/',
			args
		)
		print (response.status_code)
		if type(response) == requests.models.Response:
			json_response = json.loads(response.text)
			return json_response
			
		return response