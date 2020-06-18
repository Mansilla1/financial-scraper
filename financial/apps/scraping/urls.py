from django.urls import path

from financial.apps.scraping import views


app_name = 'scraping'

urlpatterns = [
    path(
        'initial/',
        views.ScrapingView.as_view(),
        name='initial',
    ),
]
