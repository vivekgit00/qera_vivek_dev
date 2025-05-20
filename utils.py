from rest_framework.response import Response

def custom_response(message="OK", status=1, data=""):
    return Response({
        "message": message,
        "status": status,
        "data": data
    })