from django.conf.urls import url
from . import views
from .views import RegisterView, LoginView, LogoutView # vistas basadas en clase, se importa la vista.

urlpatterns = [
    # url(r'^registrar$', RegisterView.as_view(), name='register'),
    # url(r'^ingresar$', LoginView.as_view(), name='login'),
    # url(r'^salir$', LogoutView.as_view(), name='logout'),
    url(r'^userodoo$', views.UserOdooResponse),
    url(r'^contractodoo$', views.ContratctOdooResponse),
    url(r'^billsodoo$', views.BillsOdooResponse),
    url(r'^trucksodoo$', views.TruckOdooResponse),
    url(r'^truckdetailodoo$', views.TruckDetailOdooResponse),
    url(r'^truckscontract$', views.truckcontractResponse),
    url(r'^newsyecora$', views.newsYecora),
    url(r'^newsimage/(?P<id>\d+)$', views.newsImage),
    url(r'^urlprice$', views.urlPrice),
    url(r'^exchange$', views.exchange),
    url(r'^detailreception$', views.DetailReception),
]
