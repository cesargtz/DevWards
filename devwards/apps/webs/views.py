from django.shortcuts import render
from django.http import JsonResponse # Para mandar una respuesta al ajax
from .forms import CreateWebsite
from django.views.generic import CreateView, DetailView, View
from django.core.urlresolvers import reverse_lazy
from .models import WebSite, Vote

class SendWebsiteView(CreateView):  # Para guardar el formulario en la base de datos

    template_name = "sitio.html"
    form_class = CreateWebsite
    success_url = reverse_lazy('webs:send')    # Despues de crarse el objeto este redirecionsa

class WebSiteDetail(DetailView): # El detialview es para cuando pasas valores. esta manda los detalles de un objeto

    template_name = "detalle.html"
    model = WebSite
    context_object_name = 'website' #almacena el detalle del objeto en la variable 'website'

class WebsiteVoteView(DetailView):

    template_name = "vote.html"
    model = WebSite
    context_object_name = 'website'

    def get_context_data(self, **kwargs):
        context = super(WebsiteVoteView, self).get_context_data(**kwargs)
        print(kwargs['object'])
        context['already_vote'] = Vote.objects.filter(
            user = self.request.user,
            website = kwargs['object']
        ).exists()# estamos haciendo una consulta al modelo vote para saber si el usuario  y el website ya votaron. Devuelve true o false
        print(context['already_vote'])
        return context

class VoteAjax(View):

    def get(self, request, *args, **kwargs):
        website = WebSite.objects.get(id = request.GET['websiteID'])
        Vote.objects.create(
            user =request.user,
            website =website,
            desing =int(request.GET['valDesign']),
            usability = int(request.GET['valUsability']),
            creativity = int(request.GET['valCreativity']),
            content = int(request.GET['valCreativity']),
        )
        return JsonResponse({ 'suceess':True })
