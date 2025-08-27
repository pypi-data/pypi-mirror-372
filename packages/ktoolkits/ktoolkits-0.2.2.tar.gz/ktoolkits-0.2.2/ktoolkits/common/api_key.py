
import ktoolkits

def get_default_api_key():
    if ktoolkits.api_key is not None:
        # user set environment variable KTOOL_API_KEY
        return ktoolkits.api_key