import os

from ktoolkits.common.constants import (
                                KTOOL_DEBUG_ENV,
                                KTOOL_API_KEY_ENV,
                                KTOOL_API_VERSION_ENV
)

debug = os.environ.get(KTOOL_DEBUG_ENV,False)

api_version = os.environ.get(KTOOL_API_VERSION_ENV, 'v1')
# read the api key from env
api_key = os.environ.get(KTOOL_API_KEY_ENV)

# define api base url, ensure end /
base_http_api_url = os.environ.get(
    'KTOOL_HTTP_BASE_URL',
    'https://node1.cloudsoc.vip/console/api/%s' % (api_version))