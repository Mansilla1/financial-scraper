from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from financial.apps.scraping.exceptions import InvalidResponse
from financial.apps.scraping.services import ScrapingServices


class ScrapingViews(APIView):

    def get(self, request):
        scraping_services = ScrapingServices()

        try:
            result = scraping_services.get_nemos()
            status_code = status.HTTP_200_OK
        except InvalidResponse:
            result = {'error': 'No se puede establecer conexión'}
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(
            data=result,
            status=status_code,
        )
