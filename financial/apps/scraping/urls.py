from django.urls import path

from financial.apps.scraping import views


app_name = 'scraping'

urlpatterns = [
    path(
        'initial/',
        views.ScrapingViews.as_view(),
        name='initial',
    ),
]
