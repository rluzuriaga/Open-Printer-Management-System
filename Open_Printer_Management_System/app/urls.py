from django.urls import path

from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('refresh-toner', views.refresh_toner, name="refresh-toner"),
]
