from django.urls import path

from financial.apps.base import views


app_name = 'base'

urlpatterns = [
    path(
        'health-check/',
        views.HealthCheckView.as_view(),
        name='health_check',
    ),
]
