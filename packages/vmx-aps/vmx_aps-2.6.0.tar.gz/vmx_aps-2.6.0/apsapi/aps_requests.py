# Copyright (c) 2025. Verimatrix. All Rights Reserved.
# All information in this file is Verimatrix Confidential and Proprietary.
import requests
import backoff
import logging

LOGGER = logging.getLogger(__name__)

def check_requests_response(response):
    """Check response from requests call. If there is an error message coming from
    APS backend, log and return it. Otherwise, raise an exception for HTTP errors."""
    try:
        # Check if the response has a JSON body
        if response.headers.get('Content-Type', '').startswith('application/json'):
            json_data = response.json()
            if (json_data is not None) and ('errorMessage' in json_data):
                LOGGER.error(f"APS Error: {json_data['errorMessage']}")
                return
    except ValueError:
        # If response.json() fails, the body is not valid JSON; proceed to raise HTTP error
        pass
    
    # Raise HTTP error for non-200 responses
    response.raise_for_status()

@backoff.on_exception(
    wait_gen=backoff.expo,  # Exponential backoff
    exception=(requests.exceptions.RequestException,),  # Retry only for network-related errors
    max_tries=3,  # Maximum number of retries
    max_time=30,  # Maximum total time for retries
    logger=LOGGER 
)
def request_with_retry(method, url, **kwargs):
    response = requests.request(method, url, **kwargs)
    check_requests_response(response)
    return response

class ApsRequest:
    @staticmethod
    def get(url, **kwargs):
         return request_with_retry('get', url, **kwargs)

    @staticmethod
    def put(url, **kwargs):
         return request_with_retry('put', url, **kwargs)

    @staticmethod
    def post(url, **kwargs):
         return request_with_retry('post', url, **kwargs)

    @staticmethod
    def patch(url, **kwargs):
         return request_with_retry('patch', url, **kwargs)

    @staticmethod
    def delete(url, **kwargs):
         return request_with_retry('delete', url, **kwargs)

    @staticmethod
    def get(url, **kwargs):
         return request_with_retry('get', url, **kwargs)
