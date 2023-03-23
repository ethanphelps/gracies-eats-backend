class NotFoundException(Exception):
    status: 404

class ValidationException(Exception):
    status: 400