'''
IRIS Native API for Python.

This module provides highly efficient and lightweight access to IRIS, including the Global Module and object oriented programming environment.
'''

# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'intersystems_irispython.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-intersystems_irispython-5.2.1')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-intersystems_irispython-5.2.1')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

import sys

import iris.irissdk as irissdk
import iris._Callback
import iris._GatewayEvent
import iris._GatewayUtility
import iris._IRISGlobalNode
import iris._IRISGlobalNodeView
import iris._IRISIterator
import iris._LegacyIterator
import iris._ModuleBank
import iris._PrintStream

class GatewayContext(irissdk.GatewayContext): pass
class GatewayEvent(iris._GatewayEvent._GatewayEvent): pass
class IRIS(irissdk.IRIS):
    __doc__ = irissdk.IRIS.__doc__
    pass
class IRISConnection(irissdk.IRISConnection):
    __doc__ = irissdk.IRISConnection.__doc__
    pass
class IRISGlobalNode(iris._IRISGlobalNode._IRISGlobalNode): pass
class IRISGlobalNodeView(iris._IRISGlobalNodeView._IRISGlobalNodeView): pass
class IRISIterator(iris._IRISIterator._IRISIterator): pass
class LegacyIterator(iris._LegacyIterator._LegacyIterator): pass
class IRISList(irissdk.IRISList): pass
class IRISObject(irissdk.IRISObject): pass
class IRISReference(irissdk.IRISReference): pass
class GatewayException(Exception): pass
class Constant(irissdk.Constant): pass

irissdk.initialize(iris._Callback._Callback._execute)

def connect(*args, **kwargs):
    '''Return a new open connection to an IRIS instance.

iris.connect(hostname,port,namespace,username,password,timeout,sharedmemory,logfile,sslconfig,autoCommit,isolationLevel,featureOptions,accessToken)

iris.connect(connectionstr,username,password,timeout,sharedmemory,logfile,sslconfig,autoCommit,isolationLevel,featureOptions,accessToken)

Parameters may be passed by position or keyword.

Parameters
----------
      hostname : (str) IRIS instance URL.
          port : (int) IRIS superserver port number.
     namespace : (str) IRIS namespace.
 connectionstr : (str) "hostname:port/namespace". Use this instead of the hostname, port, and namespace.
      username : (str) IRIS username. Optional if accessToken is used.
      password : (str) IRIS password. Optional if accessToken is used.
       timeout : (optional int) Maximum number of seconds to wait while attempting the connection. defaults to 10.
  sharedmemory : (optional bool) set to True to attempt a shared memory connection when the hostname.
                 is localhost or 127.0.0.1. set to false to force a connection over TCP/IP. defaults to True.
       logfile : (optional str) Client-side log file path. the maximum path length is 255 ASCII characters.
     sslconfig : (optional str) SSL configuration name as defined in an SSL Settings File.
                 On Windows, the file is SSLDefs.ini. On Unix, the file is pointed to by environment variable ISC_SSLconfigurations.
                 Here is the documentation on the SSL Settings File
                 https://docs.intersystems.com/iris20221/csp/docbook/DocBook.UI.Page.cls?KEY=GTLS_windotinifile
                 If None or empty string, a non-SSL connection will be used.
    autoCommit : (optional bool) Indicates if IRIS auto-commit is enabled.
isolationLevel : (optional int) Indicates iris.dbapi isolation level.
featureOptions : (optional str) With a series of bit flags, it specifies whether certain features are enabled or disabled.
   accessToken : (optional str) use accessToken for OAuth2 connection, instead of username/password.

Returns
-------
iris.IRISConnection
    A new client connection to an IRIS server

Please Note
-----------
If hostname is not a localhost, then sharedmemory is turned off.
If SSL is enabled, then sharedmemory is turned off.
'''
    return createConnection(*args, **kwargs)

def createConnection(*args, **kwargs):
    '''This method is an alias to the connect() method.'''
    connection = iris.IRISConnection()
    connection._connect(*args, **kwargs)
    return connection

def createIRIS(connection):
    '''Return a new iris.IRIS object that uses the given connection.

iris.createIRIS(conn)

Throw an exception if the connection is closed.

Parameters
----------
connection : iris.IRISConnection object to use

Returns
-------
iris.IRIS
    A new IRIS object that uses the given connection.
'''
    return irissdk.createIRIS(connection)

def startGatewayServer(*args):
    try:
        saved_stdout = sys.stdout
        saved_stderr = sys.stderr
        sys.stdout = iris._PrintStream._PrintStream(0)
        sys.stderr = iris._PrintStream._PrintStream(1)
        irissdk.startGatewayServer(*args)
        sys.stdout = saved_stdout
        sys.stderr = saved_stderr
    except Exception as e:
        sys.stdout = saved_stdout
        sys.stderr = saved_stderr
        print(e)
        input("Press ENTER to finish ... ")

def getSecureConnection(sharedmemory = True):
    if not hasattr(iris, "cls"):
        raise ModuleNotFoundError("IRIS Embedded Python module not found")
    values = iris.cls("%Net.Remote.Utility").getAuthenticationToken()
    if values == "": return None
    code = values.split(":",3)
    port = int(code[0])
    namespace = code[1]
    username = code[2]
    token = code[3]
    return iris.createConnection("127.0.0.1", port, namespace, username, token, 10, sharedmemory, "")
