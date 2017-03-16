from django.conf.urls import url
from .views import HomeView # El punto hace referencia al mimmo arvhico que esta dentro de la app

urlpatterns = [
    url(r'^$', HomeView.as_view(), name="home"),
]
