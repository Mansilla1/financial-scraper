from django.urls import path

from financial.apps.scraping import views


app_name = 'scraping'

urlpatterns = [
    path(
        'nemos/',
        views.ScrapingView.as_view(),
        name='nemos',
    ),
    path(
        'details_by_nemo/',
        views.ScrapingView.as_view(),
        name='details_by_nemo',
    ),
]
