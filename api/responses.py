from django.http import JsonResponse

class CORSResponse(JsonResponse):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['Access-Control-Allow-Origin'] = '*'
        self['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'


class APIResponse(CORSResponse):

    def __init__(self, code, reason, data={}, *args, **kwargs):
        super().__init__({
            'statuscode': code,
            'reason': reason,
            'data': data
        }, safe=False, status=code, *args, **kwargs)


class NotImplemented(APIResponse):

    def __init__(self, *args, **kwargs):
        super().__init__(501, "Verbs not implemented", *args, **kwargs)


class ExceptionCaught(APIResponse):

    def __init__(self, exception, *args, **kwargs):
        super().__init__(500, f"Exception caught: {str(exception)}", *args, **kwargs)


class NotAllowed(APIResponse):

    def __init__(self, *args, **kwargs):
        super().__init__(405, "Verb not allowed", *args, **kwargs)


class TokenExpired(APIResponse):

    def __init__(self, *args, **kwargs):
        super().__init__(401, "Token expired", *args, **kwargs)


class InvalidToken(APIResponse):

    def __init__(self, reason, *args, **kwargs):
        super().__init__(401, f"Invalid token: {reason}", *args, **kwargs)
