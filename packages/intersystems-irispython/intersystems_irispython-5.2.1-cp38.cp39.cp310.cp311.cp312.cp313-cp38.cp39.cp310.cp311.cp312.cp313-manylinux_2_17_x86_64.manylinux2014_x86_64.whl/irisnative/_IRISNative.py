import iris

def createConnection(*args, **kwargs):
    '''This method has been deprecated. Please use iris.createConnection(...)'''
    return iris.createConnection(*args, **kwargs)

def createIris(connection):
    '''This method has been deprecated. Please use iris.createIRIS(...)'''
    return iris.createIRIS(connection)
