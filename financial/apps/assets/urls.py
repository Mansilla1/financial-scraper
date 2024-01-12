from django.urls import path

from financial.apps.assets import views


app_name = "assets"

urlpatterns = [
    path(
        "",
        views.AssetsView.as_view(),
        name="initial",
    ),
    path(
        "web-scraping/",
        views.ScrapeAssets.as_view(),
        name="web-scraping",
    ),
    path(
        "web-scraping/historical-prices/",
        views.ScrapeHistoricalAssetsPrices.as_view(),
        name="web-scraping-historical-prices",
    ),
]
