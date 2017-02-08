from config import *
from jsonld_processor import load_context, fetch_doc_from_api, jsonld_converter, nquads_transform, get_uri_value_pairs

def dictkeys_to_string(keys):
    string = ''
    for _key in keys:
        string += _key + ', '
    return string.strip(', ')
def find_id_from_uri(uri):
    for _id in AVAILABLE_IDS.keys():
        if AVAILABLE_IDS[_id]["uri"] == uri:
            return _id

def find_annotate_api_and_url(_id, value):
    '''
    Give an ID, look through all availalble api sources,
    if the ID can be annotated by this API, return API name and annotate_url
    '''
    annotate = {}
    for _source in AVAILABLE_API_SOURCES:
        if "annotate_ids" in AVAILABLE_API_SOURCES[_source] and _id in AVAILABLE_API_SOURCES[_source]["annotate_ids"]:
            annotate.update({_source: AVAILABLE_API_SOURCES[_source]["annotate_syntax"].replace("*", str(value))})
    return annotate

def find_annotate_api_and_url_for_explore(_id, value):
    annotate = {}
    for _source in AVAILABLE_API_SOURCES:
        if "annotate_ids" in AVAILABLE_API_SOURCES[_source] and _id in AVAILABLE_API_SOURCES[_source]["annotate_ids"]:
            annotate.update({_source: {value: AVAILABLE_API_SOURCES[_source]["annotate_syntax"].replace("*", str(value))}})
    return annotate

def get_uri_list(context):
    '''
    get uri and related path ina context file
    '''
    uri_path_dict = {}
    for path, v in context.items():
        for field_name, value in v["@context"].items():
            new_path = path.replace("/", ".") + "." + field_name
            if value not in uri_path_dict:
                uri_path_dict[value] = [new_path]
            else:
                uri_path_dict[value].append(new_path)
    return uri_path_dict

def compose_query_parameter_from_uri(uri, value, api):
    context = load_context(api)
    context.pop('root')
    query_string = ''
    if uri in get_uri_list(context):
        path_list = get_uri_list(context)[uri]
        for _item in path_list:
            query_string = query_string + ' ' + _item + ':' + value + ' OR'
    return query_string.strip(' OR')

def compose_query_syntax_from_uri(uri, value, api):
    '''
    give an uri, transform it into API query syntax
    '''
    query_parameter = compose_query_parameter_from_uri(uri, value, api)
    query_string = AVAILABLE_API_SOURCES[api]["query_syntax"].replace("*", query_parameter)
    return query_string


def find_query_api_and_url(_id, value):
    query = {}
    for _source in AVAILABLE_API_SOURCES:
        if "query_ids" in AVAILABLE_API_SOURCES[_source] and _id in AVAILABLE_API_SOURCES[_source]["query_ids"]:
            if "jsonld" in AVAILABLE_API_SOURCES[_source]:
                query.update({_source: compose_query_syntax_from_uri(AVAILABLE_IDS[_id]["uri"], value, _source)})
            else:
                query.update({_source: AVAILABLE_API_SOURCES[_source]["query_syntax"].replace("*", value)})
    return query

def find_query_api_and_url_for_explore(_id, value):
    query = {}
    for _source in AVAILABLE_API_SOURCES:
        if "query_ids" in AVAILABLE_API_SOURCES[_source] and _id in AVAILABLE_API_SOURCES[_source]["query_ids"]:
            if "jsonld" in AVAILABLE_API_SOURCES[_source]:
                query.update({_source: {value: compose_query_syntax_from_uri(AVAILABLE_IDS[_id]["uri"], value, _source)}})
            else:
                query.update({_source: {value: AVAILABLE_API_SOURCES[_source]["query_syntax"].replace("*", value)}})
    return query


def update_annotate_query_for_explore(explore, annotate, query):
    if annotate:
        for _source, _value in annotate.items():
            if _source in explore['annotate']:
                explore['annotate'][_source].update(_value)
            else:
                explore['annotate'][_source] = _value
    if query:
        for _source, _value in query.items():
            if _source in explore['query']:
                explore['query'][_source].update(_value)
            else:
                explore['query'][_source] = _value
    return explore


def find_xref_api_and_url(url, api):
    explore = {"annotate": {}, "query": {}}
    if 'jsonld' in AVAILABLE_API_SOURCES[api]:
        json_doc = fetch_doc_from_api(url)
        jsonld_doc = jsonld_converter(json_doc, api)
        nquads = nquads_transform(jsonld_doc)
        uri_value_pairs = get_uri_value_pairs(nquads)
        for uri, value in uri_value_pairs.items():
            _id = find_id_from_uri(uri)
            if type(value) == list:
                for _value in value:
                    annotate = find_annotate_api_and_url_for_explore(_id, _value)
                    query = find_query_api_and_url_for_explore(_id, _value)
                    explore = update_annotate_query_for_explore(explore, annotate, query)
                    annotate = {}
                    query = {}
            else:
                    annotate = find_annotate_api_and_url_for_explore(_id, value)
                    query = find_query_api_and_url_for_explore(_id, value)
                    explore = update_annotate_query_for_explore(explore, annotate, query)
                    annotate = {}
                    query = {}
    return explore
