from rest_framework.response import Response


class CTMException(Exception):
    def __init__(self, msg, code):
        self.code = code
        self.message = msg
        super().__init__(self.message)


class DataNotFoundException(CTMException):
    def __init__(self, target_model, data, field=None, code=400):
        self.code = code
        self.message = f"No data found for {target_model.__name__}{f'.{field}' if field else ''} [ {data} ]"
        super().__init__(msg=self.message, code=self.code)


class ErrorResponse:
    def __init__(self, code, msg, details=None):
        self.code = code
        self.msg = msg
        self.details = details
        self.response = Response({
            'error': {
                'code': self.code,
                'message': self.msg,
                'details': self.details
            }
        }, 400)
