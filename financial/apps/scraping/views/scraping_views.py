from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from financial.apps.scraping.exceptions import InvalidResponse
from financial.apps.scraping.services import ScrapingServices
from financial.apps.scraping.serializers import ScrapingSerializer

class ScrapingView(APIView):

    def post(self, request):
        scraping_services = ScrapingServices()
        serialized_data = ScrapingSerializer(data=request.data)
        if serialized_data.is_valid():
            try:
                result = scraping_services.get_nemos(save=serialized_data.validated_data['save'])
                status_code = status.HTTP_200_OK if result else status.HTTP_404_NOT_FOUND
            except InvalidResponse:
                result = {'error': 'No se puede establecer conexión'}
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            result = {'error': 'El valor debe enviado debe ser de tipo Boolean'}
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(
            data=result,
            status=status_code,
        )
