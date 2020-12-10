from django.http import HttpRequest

import json

def getJsonFromResponse(response):
        content_decoded = response.content.decode()
        return json.loads(content_decoded)

emptyRequest = HttpRequest()
emptyRequest._body = b""
emptyRequest.META['CONTENT_LENGTH'] = len(emptyRequest._body)
emptyRequest.META['SERVER_NAME'] = "testserver"
emptyRequest.META['SERVER_PORT'] = 8080
emptyRequest.META['QUERY_STRING'] = "/api/"

baseKwargs = {
    'request': emptyRequest,
    'return_': 1,
    'limit': 1,
}
