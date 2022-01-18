import json
import xmlrpc.client
import functools

class ConnOdoo():

    def Connection(self, model, domain, fields):
        param = connection()
        uid = xmlrpc.client.ServerProxy(
                param['ROOT'] + 'common').login(param['DB'], param['USER'], param['PASS'])
        call = functools.partial(
            xmlrpc.client.ServerProxy(param['ROOT'] + 'object').execute,
            param['DB'], uid, param['PASS'])
        method_name = 'search_read'
        response = call(model, method_name, domain, fields)
        return response


def connection():
    HOST = 'localhost'
    PORT = 8068
    settings = {
        'DB' : 'sandbox',
        'USER' : 'admin',
        'PASS' : '1',
        'ROOT' : 'http://%s:%d/xmlrpc/' % (HOST,PORT)
    }
    return  settings
