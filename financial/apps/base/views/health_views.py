from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):

    def get(self, request):
        return Response(
            data={'status': True},
            status=status.HTTP_200_OK,
        )
