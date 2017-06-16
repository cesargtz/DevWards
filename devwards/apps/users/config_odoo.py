def connection():
    HOST = 'localhost'
    PORT = 8068
    settings = {
        'DB' : 'sandbox',
        'USER' : 'admin',
        'PASS' : 'yKEY9099',
        'ROOT' : 'http://%s:%d/xmlrpc/' % (HOST,PORT)
    }
    return  settings
