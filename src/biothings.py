from config import *
from utils import find_xref_api_and_url, find_query_api_and_url, find_annotate_api_and_url, compose_query_parameter_from_uri, dictkeys_to_string
from biothings_client import ClientRedirect
from jsonld_processor import fetch_doc_from_api


class Biothings:
	def __init__(self):
		print('Welcome to Biothings Explorer!!!')

	def available_ids(self):

		'''
		list all ids for query or annotate or link
		in biothings,
		e.g. drugbank id, hgvs id, gene id, dbsnp id
		'''

		print("available ids for query, annotate and link: {}".format(AVAILABLE_IDS.keys()))


	def available_apis(self):

		'''
		list all apis available in biothings
		'''
		print("available apis for query, annotate and link: {}".format(AVAILABLE_API_SOURCES.keys()))

class BiothingsExplorer:
	def __init__(self, _id, value):
		self.results = {'annotate': None, 'query': None, 'xref': None}
		self.annotate = find_annotate_api_and_url(_id, value)
		self.query = find_query_api_and_url(_id, value)
		for k, v in self.annotate.items():
			self._url = v
			self._api = k
		self.xref = find_xref_api_and_url(self._url, self._api)
		self.results = {'annotate': self.annotate, 'query': self.query, 'xref': self.xref}
		self._id = _id
		self.value = value
		print('Summary of resources to explore for {} {}\n'.format(_id, value))
		print('Annotation Resources: {}\n'.format(dictkeys_to_string(self.annotate.keys())))
		print('Query Resources: {}\n'.format(dictkeys_to_string(self.query.keys())))
		print('Linked Annotation Resources: {}\n'.format(dictkeys_to_string(self.xref['annotate'].keys())))
		print('Linked Query Resources: {}\n'.format(dictkeys_to_string(self.xref['query'].keys())))
	
	def ExploreQueryResults(self):
		return QueryExplorer(self._id, self.value, self.query)

	def ExploreAnnotateResults(self):
		return AnnotateExplorer(self._id, self.annotate)

class QueryExplorer:
	def __init__(self, _id, value, query_results):
		self.value = value
		self.query_results = query_results
		self.cr = ClientRedirect()
		self.uri = AVAILABLE_IDS[_id]["uri"]

	def results(self):
		return self.query_results

	def get_client(self, api, fields=None, fetch_all=True):
		query_info = compose_query_parameter_from_uri(self.uri, self.value, api)
		client = self.cr.query(api, query_info, fields=fields, fetch_all=fetch_all)
		return client

	def get_id_list(self, api):
		query_info = compose_query_parameter_from_uri(self.uri, self.value, api)
		return self.cr.get_id_list(api, query_info)

	def get_json_doc(self, api):
		return fetch_doc_from_api(self.query_results[api])

class AnnotateExplorer:
	def __init__(self, _id, annotate_results):
		self.annotate_results = annotate_results
		self.cr = ClientRedirect()
		self._id = _id

	def results(self):
		return self.annotate_results

	def get_json_doc(self, api):
		return fetch_doc_from_api(self.annotate_results[api])

	def get_client(self, api, fields=None):
		client = self.cr.annotate(self._id, api, fields=fields)
		return client

class XrefExplorer:
	def __init__(self, _id, xref_results):
		self._id = _id
		self.xref_results = xref_results

	def results(self):
		return self.xref_results


