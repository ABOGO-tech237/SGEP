from rest_framework import status
from rest_framework.exceptions import APIException


class NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "NOT_FOUND"


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "CONFLICT"


class AccountSuspendedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "ACCOUNT_SUSPENDED"
    default_detail = "Compte parent suspendu. Veuillez renouveler l'inscription."
