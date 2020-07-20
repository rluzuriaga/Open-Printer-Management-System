from django.urls import path

from . import views

urlpatterns = [
    path('', views.homepage, name='opms-home'),
    path('how-to', views.homepage_demo_modal, name='opms-homepage-demo-modal'),
    path('refresh-toner', views.refresh_toner, name="refresh-toner"),
]
