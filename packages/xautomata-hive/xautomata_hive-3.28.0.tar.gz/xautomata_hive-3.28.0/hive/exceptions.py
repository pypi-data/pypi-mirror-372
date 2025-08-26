class UnauthorizedException(Exception):
    def __init__(self):
        message = '401 - UNAUTHORIZED'
        super().__init__(message)