import arrow

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from financial.apps.assets import services
from financial.apps.utils.constants import PRICES_DATE_RANGE_FORMAT_STRING


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

        range_param = PRICES_DATE_RANGE_FORMAT_STRING.get(params.get("range"))
        if not range_param:
            return Response(
                data=[],
                status=status.HTTP_400_BAD_REQUEST,
            )

        nemos = list(map(lambda x: x.strip(), nemos_param.split(",")))
        nemos_prices = services.get_assets_prices_data_by_nemos(nemos=nemos, range_string=range_param, until_date=arrow.now())

        status_code = status_code = status.HTTP_200_OK if nemos_prices else status.HTTP_404_NOT_FOUND
        result = {}
        allowed_historical_prices_fields = [
            "adj_close",
            "close",
            "date",
            "high",
            "low",
            "open",
            "volume",
        ]
        for nemo_price in nemos_prices:
            nemo = nemo_price.get("nemo")
            historical_prices = []
            for historical_price in nemo_price.get("historical_prices") or []:
                data_ = historical_price.serialize()
                historical_prices.append({
                    k: v
                    for k, v in data_.items()
                    if k in allowed_historical_prices_fields
                })
            result[nemo] = historical_prices

        return Response(
            data=result,
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
