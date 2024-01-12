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


class AssetsHistoricalPricesView(APIView):
    def get(self, request, *args, **kwargs):
        params = request.query_params
        nemos_param = params.get("nemos")

        if not nemos_param:
            return Response(
                data=[],
                status=status.HTTP_400_BAD_REQUEST,
            )

        nemos = list(map(lambda x: x.strip(), nemos_param.split(",")))
        result = services.get_assets_prices_data_by_assets_ids(assets_ids=nemos)

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


class ScrapeHistoricalAssetsPrices(APIView):
    def get(self, request, *args, **kwargs):
        from financial.apps.web_scraping import services as web_scraping_services
        params = request.query_params
        nemos_param = params.get("nemos")
        if not nemos_param:
            return Response(
                data=[],
                status=status.HTTP_400_BAD_REQUEST,
            )

        nemos = list(map(lambda x: x.strip(), nemos_param.split(",")))
        scrape = web_scraping_services.BolsaDeSantiagoWebScraping()

        data = {}
        for nemo in nemos:
            data[nemo] = scrape.get_historical_prices_by_nemo(nemo=nemo)

        if data:
            scrape.save_nemos_historical_prices(nemos_price_data=data)

        return Response(
            data=[
                {
                    "nemo": nemo,
                    "historical_prices": [
                        d.serialize()
                        for d in historical_prices
                    ]
                }
                for nemo, historical_prices in data.items()
            ],
            status=status.HTTP_200_OK,
        )
