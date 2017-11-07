from django.shortcuts import render, redirect
# Importa vista generica, da funcionalidad extra para reutilizar metodos y
# atributos
from django.views.generic import TemplateView, FormView, View
from .forms import LoginForm, RegisterForm
# Esto nos permitira redireccionar las urls con  namespace y names
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import login, authenticate, logout  # Para logearnos
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from apps.users import config_odoo
import json
import functools
import xmlrpc.client
import datetime
from time import gmtime, strftime, strptime
import psycopg2
import requests
from PIL import Image


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('main:home'))


class RegisterView(FormView):

    template_name = 'register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('main:home')  # regresa a la url

    def form_valid(self, form):
        user = form.save()  # Guarda los datos del form
        # codifica el passwors
        user.set_password(form.cleaned_data['password'])
        user.save()  # Vuelve a guardar pero ya con el password codificado
        # Esta linea va por defecto
        return super(RegisterView, self).form_valid(form)


class LoginView(FormView):

    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('main:home')

    def form_valid(self, form):  # cuanto en el form.py hace todas las validaciones este se vuelve a birnca a la vista. se Guardan los datos hasta cerrar sesion
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)
        return super(LoginView, self).form_valid(form)


@csrf_exempt
def UserOdooResponse(request):
    param = config_odoo.connection()
    req = json.loads(request.body.decode('utf-8'))
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    model = 'res.partner'
    domain = [('mobile', '=', req['mobile'])]
    method_name = 'search_read'
    user_odoo = call(model, method_name, domain, ['name', 'fax', 'mobile'])
    if not user_odoo:
        return HttpResponse("401")
    else:
        if req['fax'] == user_odoo[0]['fax']:
            fecha = str(datetime.date.today())
            market_price = call("market.price", method_name, [
                                ('date', '=', fecha)], ['price_ton', 'date'])
            market_usd = call("market.usd", method_name, [
                              ('date', '=', fecha)], ['date', 'exchange_rate'])
            if bool(market_price) is True and bool(market_usd) is True:
                object_respose = {
                    'responseLogin': {
                        'user': user_odoo,
                        'marketPrice': market_price,
                        'market_usd': market_usd
                    }
                }
            else:
                market_price = {}
                market_usd = {}
                count = 0
                while bool(market_price) is False or bool(market_usd) is False:
                    count = count + 1
                    fecha = str(datetime.date.today() -
                                datetime.timedelta(days=count))
                    market_price = call("market.price", method_name, [
                                        ('date', '=', fecha)], ['price_ton', 'date'])
                    market_usd = call("market.usd", method_name, [
                                      ('date', '=', fecha)], ['date', 'exchange_rate'])

                object_respose = {
                    'responseLogin': {
                        'user': user_odoo,
                        'marketPrice': market_price,
                        'market_usd': market_usd
                    }
                }
            # print (object_respose)
            return HttpResponse(json.dumps(object_respose))
        else:
            return HttpResponse("401")


@csrf_exempt
def ContratctOdooResponse(request):
    param = config_odoo.connection()
    req = json.loads(request.body.decode('utf-8'))
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    model = 'purchase.order'
    domain = [('partner_id', '=', req['name']), ('state', '=',
                                                 'approved')]  # approved partner_id es el nombre no el id  =(  approved
    method_name = 'search_read'
    contracts = call(model, method_name, domain, [
                     'name', 'contract_type', 'date_order', 'state', 'partner_id'])

    if not contracts:
        return HttpResponse("Sin Contratos")
    else:
        model = 'purchase.order.line'
        model_truck = 'truck.reception'
        model_invoice = 'account.invoice'
        for line in contracts:
            domain = [('order_id', '=', line['id'])]
            line_contracts = call(model, method_name, domain, [
                                  'product_id', 'product_qty', 'order_id'])
            line['product_id'] = 0
            line['quantity'] = 0
            line['date_order'] = line['date_order'].split()[0]
            line['tons_delivered'] = 0
            line['partner_id'] = line['partner_id'][1]
            for ilc in line_contracts:
                if line['id'] == ilc['order_id'][0]:
                    line['product_id'] = ilc['product_id'][1]
                    line['quantity'] += ilc['product_qty']
            # Total entregado
            line['tons_delivered'] = getTrucks(line['id'])
            # line['ids_truck'] = getIdsTrucks(line['id'])
            # Total Facturado
            line['Inovice'] = getInvoices(line['id'])
            if line['Inovice']:
                tons_invoiced = 0
                for invoice in line['Inovice']:
                    tons_invoiced += invoice['tons']
                line['tons_invoiced'] = tons_invoiced
            line['closures'] = getClosures(line['id'])
            line['i_inovice'] = len(line['Inovice'])
            line['i_closures'] = len(line['closures'])
        return HttpResponse(json.dumps(contracts))


def getTrucks(id_contract):
    param = config_odoo.connection()
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    domain = [('contract_id', '=', id_contract), ('state', '=', 'done')]
    line = call('truck.reception', 'search_read', domain,
                ['stock_picking_id', 'clean_kilos'])
    tons = 0
    for l in line:
        tons += l['clean_kilos'] / 1000
    return tons


def getInvoices(id_contract):
    invoice_ids = GetIdInvRel(id_contract)
    param = config_odoo.connection()
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    domain = [('id', '=', invoice_ids), ('state', '=', ['open', 'paid'])]
    line = call('account.invoice', 'search_read', domain, [
                'number', 'state', 'amount_total', 'tons', 'payment_ids', 'date_invoice', 'supplier_invoice_number'])
    amount_total = 0
    for lp in line:
        for pay in lp['payment_ids']:
            amounts = call('account.move.line', 'search_read',
                           [('id', '=', pay)], ['debit'])
            amount_total = 0
            for amount in amounts:
                amount_total += amount['debit']
        lp['payment_ids'] = amount_total
        # # # # # # # # # # # # # #
        conn = psycopg2.connect(dbname='sandbox', user='odoo', host='localhost', password='odoo')
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM account_invoice_line WHERE invoice_id = %s """ % (lp['id']))
        rows = cursor.fetchall()
        price_unit = 0
        product = ""
        for row in rows:
            price_unit = row[8]
            cursor.execute("""SELECT product_tmpl_id  FROM product_product WHERE id = %s """ % (row[13]))
            product_id = cursor.fetchall()
            cursor.execute("""SELECT name FROM product_template WHERE id = %s """ % (product_id[0]))
            product_name = cursor.fetchall()
            product = product_name[0][0]
            break
        lp['price_unit'] = float(price_unit)
        lp['product'] = str(product)
    return line


def GetIdInvRel(id_purchase):
    try:
        conn = psycopg2.connect(
            dbname='sandbox', user='odoo', host='localhost', password='odoo')
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM purchase_invoice_rel WHERE purchase_id = %d""" % (id_purchase))
        rows = cursor.fetchall()
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


@csrf_exempt
def BillsOdooResponse(request):
    param = config_odoo.connection()
    req = json.loads(request.body.decode('utf-8'))
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    model = 'purchase.order'
    domain = [('partner_id', '=', req['name']), ('state', '=',
                                                 'approved')]  # partner_id es el nombre no el id  =(
    method_name = 'search_read'
    contracts = call(model, method_name, domain, [
                     'name', 'contract_type', 'date_order', 'state', 'partner_id'])
    pass


def getClosures(id_contract):
    param = config_odoo.connection()
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])

    line = call('pinup.price.purchase', 'search_read', [('purchase_order_id', '=', id_contract), ('state', '=', ['invoiced','close'])], [
                'name', 'tons_reception', 'tons_priced', 'request_date', 'price_mxn', 'pinup_tons'])
    return line


@csrf_exempt
# necesitamos un offset que indica cuantos registros va a ignorar  y un
# feth que seran cuantos mas va a buscar osea 10

def TruckOdooResponse(request):
    try:
        param = config_odoo.connection()
        req = json.loads(request.body.decode('utf-8'))
        if req['idsContract']:
            conn = psycopg2.connect(
                dbname='sandbox', user='odoo', host='localhost', password='odoo')
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id FROM truck_reception WHERE contract_id in %s ORDER BY id DESC OFFSET %d ROWS FETCH NEXT 10 ROWS ONLY """ % (str(req['idsContract']).replace('[', '(').replace(']', ')') , req['offset']))
            rows = cursor.fetchall()
            list_ids = []
            for row in rows:
                list_ids.append(str(row[0]))
            if list_ids:
                uid = xmlrpc.client.ServerProxy(
                    param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
                # Enable functions of the Odoo
                call = functools.partial(
                    xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
                    param['DB'], uid, param['PASS'])
                domain = [('id', 'in',list_ids )]
                line = call('truck.reception', 'search_read', domain,
                            ['name', 'contract_id' ,'date','clean_kilos','hired','delivered','pending'])
                for l in line:
                    l['contract_id'] = l['contract_id'][1]
                return HttpResponse(json.dumps(line))
            else:
                return False
        else:
            return False
    except Exception as e:
        print("can't connect. Invalid dbname, user or password?")
        print(e)
        return False

@csrf_exempt
def TruckDetailOdooResponse(request):
    param = config_odoo.connection()
    req = json.loads(request.body.decode('utf-8'))
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    domain = [('id', '=', req )]
    line = call('truck.reception', 'search_read', domain,
                ['name', 'contract_id' ,'date','clean_kilos','partner_id','driver','car_plates','hired','delivered','pending',
                'humidity_rate','density','temperature','damage_rate','break_rate','impurity_rate','input_kilos','output_kilos','raw_kilos',
                'broken_kilos', 'impure_kilos', 'damaged_kilos','humid_kilos'])
    return HttpResponse(json.dumps(line))

@csrf_exempt
def truckcontractResponse(request):
    param = config_odoo.connection()
    req = json.loads(request.body.decode('utf-8'))
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    domain = [('contract_id', '=', req )]
    line = call('truck.reception', 'search_read', domain,
                ['name', 'contract_id' ,'date','clean_kilos','hired','delivered','pending'])
    for l in line:
        l['contract_id'] = l['contract_id'][1]
    return HttpResponse(json.dumps(line))

@csrf_exempt
def newsYecora(request):
    try:
        param = config_odoo.connection()
        req = json.loads(request.body.decode('utf-8'))
        conn = psycopg2.connect(
            dbname='sandbox', user='odoo', host='localhost', password='odoo')
        cursor = conn.cursor()
        if req == 0:
            cursor.execute(
                """SELECT title, id, sub_title, message  FROM news_app ORDER BY id DESC OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY """)
        else:
            cursor.execute(
                """SELECT title, id FROM news_app where id = %s ORDER BY id DESC OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY """) % (req)
        rows = cursor.fetchall()
        news = []
        for row in rows:
                 obj = {'id':row[1],'title':row[0], 'subTitle':row[2], 'message':row[3], 'image':'http://www.yecora.mx:8000/newsimage/' + str(row[1])}
                 news.append(obj)
        return HttpResponse(json.dumps(news))
    except Exception as e:
        print("can't connect. Invalid dbname, user or password?")
        print(e)
        return False

@csrf_exempt
def newsImage(request, id):
    param = config_odoo.connection()
    # req = json.loads(request.body.decode('utf-8'))
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    domain = [('res_model', '=', 'news.app' ),('res_id', '=', id)]
    res = call('ir.attachment', 'search_read', domain,['store_fname','name'])
    path = False
    name = False
    for value in res:
        path = value['store_fname']
        name = value['name']
        break
    #Dar permisos al directorio chmod
    # print("/home/odoo/.local/share/Odoo/filestore/sandbox/" + path)
    img = Image.open("/home/odoo/.local/share/Odoo/filestore/sandbox/" + path)
    # img = img.resize((100, 100))
    response = HttpResponse(content_type='image/jpg')
    img.save(response, "JPEG")
    # response['Content-Disposition'] = 'attachment; filename=%s' % (name)
    return response

@csrf_exempt
def urlPrice(request):
    param = config_odoo.connection()
    req = json.loads(request.body.decode('utf-8'))
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    res = call('market.base', 'search_read', [],['url_price_corn'])
    size = len(res) - 1
    url = res[size]['url_price_corn']
    resp = requests.get(url + "&start_date=" + req) # yyyy-mm-dd
    if resp.status_code != 200:
       _logger.error("Error to get price corn to quandl")
    response = resp.json()
    data = response['dataset']['data']
    date = []
    price = []
    for i in data:
        date.append(i[0])
        price.append(i[6])
    json_array = {'pricecorn':{'date':date, 'price':price}}
    return HttpResponse(json.dumps(json_array))

@csrf_exempt
def exchange(request):
    param = config_odoo.connection()
    req = json.loads(request.body.decode('utf-8'))
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    # Enable functions of the Odoo
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    line = call('market.usd', 'search_read', [('date','>=', req)],
                ['exchange_rate', 'date'])
    return HttpResponse(json.dumps(line))

@csrf_exempt
def DetailReception(request):
    param = config_odoo.connection()
    req = json.loads(request.body.decode('utf-8'))
    uid = xmlrpc.client.ServerProxy(
        param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
    call = functools.partial(
        xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
        param['DB'], uid, param['PASS'])
    line = call('truck.reception', 'search_read', [('contract_id','>=', req['contract_ids']),('state','=','done')],
            ['delivered','pending'])
    return HttpResponse(json.dumps(line))
