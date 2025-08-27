import inspect
import platform
import sys
import iris

class _GatewayUtility(object):

    @staticmethod
    def getLanguageName():
        return "Python"

    @staticmethod
    def getLanguageVersion():
        return platform.python_version()

    @staticmethod
    def getProductVersion():
        return iris.IRIS.getProductVersion()

    @staticmethod
    def writeOutput(data):
        if data is None:
            data = ""
        connection = iris.GatewayContext.getConnection()
        method_object = connection._output_redirect_handler
        if method_object is None:
            print(data, end="", flush=True)
        else:
            args = [ data ]
            method_object(*args)
