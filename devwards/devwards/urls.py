"""devwards URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings #media files import, tambien se modifica el archivo local.py para poner la tura static_url
from django.conf.urls.static import static #media files import

urlpatterns = [
    url(r'^', include('apps.main.urls', namespace="main")),   # Incluir otro archivo de urls. importa la libreria include, despues agrega la direcion. para esto crear el arhchivo url
    url(r'^', include('apps.users.urls', namespace="users")),
    url(r'^', include('apps.webs.urls', namespace="webs")),
    # El url sirve para hacer referencias a las rutas
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  #eso es media files para poder usar las url de las imagenes.
