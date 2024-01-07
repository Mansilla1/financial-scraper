from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from financial.apps.assets import services


class AssetsView(APIView):

    def get(self, request, *args, **kwargs):
        result = services.get_assets_data()

        status_code = status_code = status.HTTP_200_OK if result else status.HTTP_404_NOT_FOUND
        return Response(
            data=[
                d.serialize()
                for d in result
            ],
            status=status_code,
        )


# TODO: delete this
class ScrapeAssets(APIView):
    def get(self, request, *args, **kwargs):
        from financial.apps.web_scraping import services as web_scraping_services
        scrape = web_scraping_services.BolsaDeSantiagoWebScraping()
        data = scrape.get_nemos_price_data()
        if data:
            scrape.save_nemos(nemos_price_data=data)
        return Response(
            data=[
                d.serialize()
                for d in data
            ],
            status=status.HTTP_200_OK,
        )
