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
