import requests
import json
from datetime import datetime


def create_error_status(req, err_msg):
    """
    Takes a requests.models.Response object and creates an error dict using its information
    
    @params req, the requests.models.Response object\n
    @params err_msg, the custom error message string given by the calling function
    """
    data = {'status_error': 'Object not an instance of requests.models.Response, cant create an error status',
            'time_stamp': str(datetime.now())
            }
    if isinstance(req, requests.models.Response):
        data = {'status_error': err_msg,
                'time_stamp': str(datetime.now()),
                'html_information': {'text': str(req.text), 'status_code': str(req.status_code), 'headers': str(req.headers)}
                }
    
    with open('log.txt', 'a') as outfile:
        json.dump(data, outfile)
        outfile.write('\n')
    
    return data


def is_dict_an_error_dict(d):
    """
    Takes a dict and checks if the dict is an error dict
    
    @params d, the dictionary to check
    """
    if isinstance(d, dict):
        for keys in d:
            if keys == 'status_error':
                return True

    return False


def is_dict_a_success_dict(d):
    """
    Takes a dict and checks if the dict is a success dict
    
    @params d, the dictionary to check
    """
    if isinstance(d, dict):
        for keys in d:
            if keys == 'status_success':
                return True

    return False
