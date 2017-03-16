from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, View # Importa vista generica, da funcionalidad extra para reutilizar metodos y atributos
from .forms import LoginForm, RegisterForm
from django.core.urlresolvers import reverse_lazy, reverse # Esto nos permitira redireccionar las urls con  namespace y names
from django.contrib.auth import login, authenticate, logout  # Para logearnos
from django.http import JsonResponse, HttpResponse
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

def UserOdooResponse(request):
    HOST = '54.187.237.193'
    PORT = 8069
    DB = 'productiva2'
    USER = 'admin'
    PASS = 'admingys'
    ROOT = 'http://%s:%d/xmlrpc/' % (HOST,PORT)


    uid = xmlrpc.client.ServerProxy(ROOT + 'common').login(DB,USER,PASS)
    # Enable functions of the OdORM
    call = functools.partial(
        xmlrpc.client.ServerProxy(ROOT + 'object').execute,
        DB, uid, PASS)
    model = 'res.partner'
    domain = ['|',('mobile','=','652 103 8859'),('mobile','=','625 101 1187')]
    method_name = 'search_read'
    user_odoo = call(model, method_name, domain, ['mobile','curp'])
    return HttpResponse("Usuario: %s" % (user_odoo))




    # uid = xmlrpc.client.ServerProxy(ROOT + 'common').login(DB,USER,PASS)
    # # Enable functions of the OdORM
    # call = functools.partial(
    #     xmlrpc.client.ServerProxy(ROOT + 'object').execute,
    #     DB, uid, PASS)
    # model = 'res.partner'
    # domain = ['vat', '=','MXBAUA800729EM7']
    # method_name = 'search_read'
    # user_odoo = call(model, method_name, domain, ['name','curp'])
    # return JsonResponse("Usuario: %s" % (user_odoo))
