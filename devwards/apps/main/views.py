from django.shortcuts import render
from django.views.generic import TemplateView
from apps.webs.models import WebSite

class HomeView(TemplateView):

    template_name = "home.html"

    def get_context_data(self, **kargs): # con este metodo pasas una consulta a la vista
        context = super(HomeView, self).get_context_data(**kargs)
        context['last_website'] = WebSite.objects.last() # Primer argumento una clave de indentificador devuelve un objeto
        context['websites'] = WebSite.objects.exclude(id = context['last_website'].id) #Devuelve una lista de objetos
        return context


















# from django.http import HttpResponse
# import functools
# import xmlrpc.client

# Create your views here.

# HOST = '54.191.157.205'
# PORT = 8069
# DB = 'productiva2'
# USER = 'admin'
# PASS = 'admingys'
# ROOT = 'http://%s:%d/xmlrpc/' % (HOST,PORT)


#def home(request):   Cremos la funcion que llama la url, y esta llama al template
    # 1. Login
    # uid = xmlrpc.client.ServerProxy(ROOT + 'common').login(DB,USER,PASS)
    # # Enable functions of the OdORM
    # call = functools.partial(
    #     xmlrpc.client.ServerProxy(ROOT + 'object').execute,
    #     DB, uid, PASS)
    # model = 'truck.internal'
    # domain = []
    # method_name = 'search_read'
    # truck_internals = call(model, method_name, domain, ['name','ticket_dest'])
    # return HttpResponse("Camiones Internos: %s" % (truck_internals))


    #return HttpResponse("Logged in as %s (uid:%d)" % (USER,uid))
    #return render(request,'home.html')
