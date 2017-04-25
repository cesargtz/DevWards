from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, View # Importa vista generica, da funcionalidad extra para reutilizar metodos y atributos
from .forms import LoginForm, RegisterForm
from django.core.urlresolvers import reverse_lazy, reverse # Esto nos permitira redireccionar las urls con  namespace y names
from django.contrib.auth import login, authenticate, logout  # Para logearnos
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import json
import functools
import xmlrpc.client


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('main:home'))

class RegisterView(FormView):

    template_name = 'register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('main:home') #regresa a la url

    def form_valid(self, form):
        user = form.save() # Guarda los datos del form
        user.set_password(form.cleaned_data['password']) #codifica el passwors
        user.save() # Vuelve a guardar pero ya con el password codificado
        return super(RegisterView, self).form_valid(form) # Esta linea va por defecto

class LoginView(FormView):

    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('main:home')

    def form_valid(self, form): #cuanto en el form.py hace todas las validaciones este se vuelve a birnca a la vista. se Guardan los datos hasta cerrar sesion
        user = authenticate(
            username = form.cleaned_data['username'],
            password = form.cleaned_data['password']
        )
        login(self.request, user)
        return super(LoginView, self).form_valid(form)

@csrf_exempt
def UserOdooResponse(request):
    HOST = '54.187.237.193'
    PORT = 8069
    DB = 'sandbox'
    USER = 'admin'
    PASS = '1'
    ROOT = 'http://%s:%d/xmlrpc/' % (HOST,PORT)

    if request.method == 'POST':

        req = json.loads( request.body.decode('utf-8') )

        uid = xmlrpc.client.ServerProxy(ROOT + 'common').login(DB,USER,PASS)
        # Enable functions of the OdORM
        call = functools.partial(
            xmlrpc.client.ServerProxy(ROOT + 'object').execute,
            DB, uid, PASS)
        model = 'res.partner'
        domain = [('mobile','=',req['mobile'])]
        method_name = 'search_read'
        user_odoo = call(model, method_name, domain, ['mobile','fax'])
        if not user_odoo:
            return HttpResponse("401")
        else:
             if req['fax'] == user_odoo[0]['fax']:
                return HttpResponse(json.dumps(user_odoo))
             else:
                return HttpResponse("401")
        # if user_odoo != None:
        #     if req['fax'] == user_odoo[0]['fax']:
        #         return HttpResponse(json.dumps(user_odoo))
        #     else:
        #         return HttpResponse("401")
        # else:
        #     return HttpResponse("401")
