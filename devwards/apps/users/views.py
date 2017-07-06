from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, View # Importa vista generica, da funcionalidad extra para reutilizar metodos y atributos
from .forms import LoginForm, RegisterForm
from django.core.urlresolvers import reverse_lazy, reverse # Esto nos permitira redireccionar las urls con  namespace y names
from django.contrib.auth import login, authenticate, logout  # Para logearnos
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from apps.users import config_odoo
import json, functools ,xmlrpc.client, datetime
from time import gmtime, strftime
import psycopg2


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
    param = config_odoo.connection()
    req = json.loads( request.body.decode('utf-8') )
    uid = xmlrpc.client.ServerProxy(param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    model = 'res.partner'
    domain = [('mobile','=',req['mobile'])]
    method_name = 'search_read'
    user_odoo = call(model, method_name, domain, ['name','fax','mobile'])
    if not user_odoo:
        return HttpResponse("401")
    else:
         print (user_odoo)
         if req['fax'] == user_odoo[0]['fax']:
            fecha = str(datetime.date.today())
            market_price = call("market.price", method_name, [('date', '=', fecha)],['price_ton','date'])
            market_usd =  call("market.usd", method_name, [('date', '=', fecha)],['date','exchange_rate'])
            if bool(market_price) is True and bool(market_usd) is True:
                object_respose ={
                    'responseLogin' : {
                        'user' : user_odoo,
                        'marketPrice' : market_price,
                        'market_usd' : market_usd
                    }
                }
            else:
                market_price = {}
                market_usd = {}
                count = 0
                while bool(market_price) is False or bool(market_usd) is False:
                    count = count + 1
                    fecha = str(datetime.date.today() - datetime.timedelta(days=count))
                    market_price = call("market.price", method_name, [('date', '=', fecha)],['price_ton','date'])
                    market_usd =  call("market.usd", method_name, [('date', '=', fecha)],['date','exchange_rate'])



                object_respose ={
                    'responseLogin' : {
                        'user' : user_odoo,
                        'marketPrice' : market_price,
                        'market_usd' : market_usd
                    }
                }
            # print (object_respose)
            return HttpResponse(json.dumps(object_respose))
         else:
            return HttpResponse("401")


@csrf_exempt
def ContratctOdooResponse(request):
        param = config_odoo.connection()
        req = json.loads( request.body.decode('utf-8') )
        uid = xmlrpc.client.ServerProxy(param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
        # Enable functions of the Odoo
        call = functools.partial(
            xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
            param['DB'], uid, param['PASS'])
        model = 'purchase.order'
        domain = [('partner_id','=',req['name']),('state','=','approved')] #partner_id es el nombre no el id  =(
        method_name = 'search_read'
        contracts = call(model, method_name, domain, ['name','contract_type','date_order','state', 'partner_id'])

        # print (contracts)
        if not contracts:
            return HttpResponse("Sin Contratos")
        else:
            model = 'purchase.order.line'
            model_truck = 'truck.reception'
            model_invoice = 'account.invoice'
            for line in contracts:
                domain = [('order_id','=',line['id'])]
                line_contracts = call(model, method_name, domain, ['product_id','product_qty','order_id'])
                line['product_id'] = 0
                line['quantity'] = 0
                line['date_order'] = line['date_order'].split()[0]
                line['tons_delivered'] = 0
                line['partner_id'] = line['partner_id'][1]
                for ilc in line_contracts:
                    if line['id'] == ilc['order_id'][0]:
                        line['product_id'] = ilc['product_id'][1]
                        line['quantity'] += ilc['product_qty']
                #Total entregado
                line['tons_delivered'] = getTrucks(line['id'])
                #Total Facturado
                line['Inovice'] = getInvoices(line['id'])
                if line['Inovice']:
                    tons_invoiced = 0
                    for invoice in line['Inovice']:
                        tons_invoiced += invoice['tons']
                    line['tons_invoiced'] = tons_invoiced
            return HttpResponse(json.dumps(contracts))


def getTrucks(id_contract):
    param = config_odoo.connection()
    uid = xmlrpc.client.ServerProxy(param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    domain =  [('contract_id', '=', id_contract),('state','=','done')]
    line = call('truck.reception', 'search_read', domain, ['stock_picking_id','clean_kilos'])
    tons = 0
    for l in line:
        tons += l['clean_kilos'] / 1000
    return tons

def getInvoices(id_contract):
    invoice_ids = GetIdInvRel(id_contract)
    param = config_odoo.connection()
    uid = xmlrpc.client.ServerProxy(param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    domain =  [('id', '=', invoice_ids),('state','=',['open','paid'])]
    line = call('account.invoice', 'search_read', domain, ['number','state','amount_total','tons','payment_ids','date_invoice'])
    # print (line)
    return line

def GetIdInvRel(id_purchase):
    try:
        # connect_str = "dbname='sandbox' user='odoo' host='localhost' password='odoo'"
        conn = psycopg2.connect(dbname='sandbox', user='odoo', host='localhost', password='odoo')
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM purchase_invoice_rel WHERE purchase_id = %d""" % (id_purchase))
        rows = cursor.fetchall()
        print (rows)
        if rows:
            invoice_rel = []
            for row in rows:
                invoice_rel.append(row[1])
            return invoice_rel
        else:
            return False
    except Exception as e:
        print("can't connect. Invalid dbname, user or password?")
        print(e)
        return False
