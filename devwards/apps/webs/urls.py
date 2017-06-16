from django.conf.urls import url
from . import views
from .views import SendWebsiteView, WebSiteDetail, WebsiteVoteView, VoteAjax # El punto hace referencia al mimmo arvhico que esta dentro de la app

urlpatterns = [  # El / al final de la url sirve para hacerla dinamica. pasar objetos. La "P" singnifica que todo despues de la P va ser un parametro, el [-\w] dice que va a acpetar tanto caracteries como letras y el + que puede ser mas de una palabra. /(?P<slug>[-\w]+)/
    url(r'^vote/$', VoteAjax.as_view(), name='vote'),
    url(r'^sitios/enviar/$', SendWebsiteView.as_view(), name='send'),
    url(r'^sitios/(?P<slug>[-\w]+)/$', WebSiteDetail.as_view(), name='website_detail'),
    url(r'^sitios/(?P<slug>[-\w]+)/votar/$', WebsiteVoteView.as_view(), name="website_vote"),
]
