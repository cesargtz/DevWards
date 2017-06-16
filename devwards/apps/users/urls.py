from django.conf.urls import url
from . import views
from .views import RegisterView, LoginView, LogoutView # vistas basadas en clase, se importa la vista.

urlpatterns = [
    url(r'^registrar$', RegisterView.as_view(), name='register'),
    url(r'^ingresar$', LoginView.as_view(), name='login'),
    url(r'^salir$', LogoutView.as_view(), name='logout'),
    url(r'^userodoo$', views.UserOdooResponse, name='user_odoo'),
    url(r'^contractodoo$', views.ContratctOdooResponse, name='user_odoo')
]
