#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Python Stack Exchange library customized for Google App Engine
"""
import app.lib.simplejson as simplejson 
from google.appengine.api import urlfetch
from app.config.constant import KEY_TEMPLATE_ERROR
import logging
try:
    from key import api_key
except ImportError: 
    logging.error(KEY_TEMPLATE_ERROR)

__api_version = '1.0'
__default_page_size = 100
__default_page = 1

class ApiRequestError(Exception):
    def __init__(self, url, code, message):
        self.args = (url, code, message)
        self.url = url
        self.code = code
        self.message = message

def get_question(question_id, api_endpoint, body = False, comments = False, pagesize = 1):
    """
    Get the question of a given question_id 
    """
    path = "questions/%d" % question_id
    results = __fetch_results(path, api_endpoint, body = body, comments = comments, pagesize = pagesize)
    return results

def get_answer(answer_id, api_endpoint, body = False, comments = False, pagesize = 1):
    """
    Get the answer of a given answer_id 
    """
    path = "answers/%d" % answer_id
    results = __fetch_results(path, api_endpoint, body = body, comments = comments, pagesize = pagesize)
    return results   
        
def get_answers(question_id, api_endpoint, rpc = None, page = 1, body = False, comments = False, pagesize = 100, sort = 'votes'):
    """
    Get the answers list of a given question_id 
    """
    path = "questions/%d/answers" % question_id
    results = __fetch_results(path, api_endpoint, rpc = rpc, body = body, page = page, comments = comments, pagesize = pagesize, sort = sort)
    return results

def get_favorites_questions(user_id, api_endpoint, page = 1, body = False, comments = False, pagesize = 100, sort = 'added'):
    """
    Get the favorites questions list of a given user_id
    """
    path = "users/%d/favorites" % user_id
    results = __fetch_results(path, api_endpoint, body = body, page = page, comments = comments, pagesize = pagesize, sort = sort)
    return results

def get_questions_by_tags(tagged, api_endpoint, page = 1, pagesize = 30, sort = 'votes'):
    """
    Get questions list filtered by tags
    """
    path = "questions" 
    results = __fetch_results(path, api_endpoint, tagged = tagged, page = page, pagesize = pagesize, sort = sort)
    return results

def get_questions(api_endpoint, page = 1, pagesize = 30, sort = 'votes'):
    """
    Get questions list sorted by votes
    """
    path = "questions" 
    results = __fetch_results(path, api_endpoint, page = page, pagesize = pagesize, sort = sort)
    return results

def get_users(filter, api_endpoint, page = 1, pagesize = 30, sort = 'reputation'):
    """
    Get a list of users filtered by display name
    """
    path = "users"
    results = __fetch_results(path, api_endpoint, filter= filter, page = page, pagesize = pagesize, sort = sort)
    return results

def get_tags(filter, api_endpoint, page = 1, pagesize = 10, sort = 'popular'):
    """
    Get a list of tags filtered by text
    """
    path = "tags"
    results = __fetch_results(path, api_endpoint, filter= filter, page = page, pagesize = pagesize, sort = sort)
    return results

def get_users_by_id(user_id, api_endpoint, page = 1, pagesize = 30, sort = 'reputation'):
    """
    Get a users of a given user_id
    """
    path = "users/%d" % user_id
    results = __fetch_results(path, api_endpoint, id = user_id, page = page, pagesize = pagesize, sort = sort)
    return results

def get_sites():
    """
    Get a list of Stack Exchange sites using Stackauth service
    """
    results = __gae_fetch('http://stackauth.com/sites')
    response = simplejson.loads(results.content)
    return response

def __fetch_results(path, api_endpoint, rpc = None, **url_params ):
    """
    Fetch results
    """
    params = {
        "key": api_key,
        "pagesize": __default_page_size,
        "page": __default_page
        }
    params.update(url_params)

    url = __build_url(path, api_endpoint, **params)
    
    results = __gae_fetch(url, rpc = rpc)
    if rpc:
        pass
    else:
        return handle_response(results)

def __build_url(path, api_endpoint, **params):
    """
    Builds the API URL for fetching results.
    """
    query = ["%s=%s" % (key, params[key]) for key in params if (params[key] or key == 'pagesize') ]
    query_string = "&".join(query)
    url = "%s/%s/%s?" % (api_endpoint, __api_version, path)
    url += query_string
    return url
    
def __gae_fetch(url, rpc = None):
    if rpc:
        return urlfetch.make_fetch_call(rpc, url, headers = {'User-Agent': 'StackPrinter','Accept-encoding': 'gzip, deflate'})
    else:
        return urlfetch.fetch(url, headers = {'User-Agent': 'StackPrinter','Accept-encoding': 'gzip, deflate'}, deadline = 10)


def handle_response(results):
    """
    Load results in JSON
    """
    response = simplejson.loads(results.content)
    if "error" in response:
        error = response["error"]
        code = error["code"]
        message = error["message"]
        raise ApiRequestError(url, code, message)
    return response    