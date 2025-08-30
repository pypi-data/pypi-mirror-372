###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.server.applications import create_application
from everysk.server.endpoints import JSONEndpoint
from everysk.server.routing import Route, RouteLazy


###############################################################################
#   TestPublicEndpoint Class Implementation
###############################################################################
class TestPublicEndpoint(JSONEndpoint):
    rest_key_name: str = None
    rest_key_value: str = None

    async def get(self):
        return {'message': 'Hello, World!'}


###############################################################################
#   TestPrivateEndpoint Class Implementation
###############################################################################
class TestPrivateEndpoint(JSONEndpoint):
    rest_key_name: str = 'X-Api-Key'
    rest_key_value: str = '123456'

    async def get(self):
        return {'message': 'Hello, World Private!'}


###############################################################################
#   Application Implementation
###############################################################################
routes = [
    RouteLazy(path='/', endpoint='everysk.server.example_api.TestPublicEndpoint'),
    Route(path='/private', endpoint=TestPrivateEndpoint)
]

app = create_application(routes=routes)


###############################################################################
#   How to run this example
###############################################################################
## To run this example, execute the following command:
# ./run.sh starlette everysk.server.example_api:app

## To test using requests:
# ./run.sh shell
#
# In [1]: import requests
#
# In [2]: requests.get('http://127.0.0.1:8000')
# Out[2]: <Response [200]>
#
# In [3]: requests.get('http://127.0.0.1:8000').content
# Out[3]: b'{"message":"Hello, World!"}'
#
# In [4]: requests.get('http://127.0.0.1:8000/private').content
# Out[4]: b'{"error":"401 -> Unauthorized access to this resource.","code":401,"trace_id":""}'
#
# In [5]: requests.get('http://127.0.0.1:8000/private', headers={'X-Api-Key': '123456'}).content
# Out[5]: b'{"message":"Hello, World Private!"}'
