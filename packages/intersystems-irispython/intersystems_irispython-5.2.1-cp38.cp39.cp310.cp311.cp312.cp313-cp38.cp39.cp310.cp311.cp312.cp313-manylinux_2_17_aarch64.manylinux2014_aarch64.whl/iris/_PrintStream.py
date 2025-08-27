import io
import sys
import threading
import iris

class _PrintStream(io.StringIO):

    registry = {}

    def __init__(self, type):
        super().__init__()
        self.type = type

    @classmethod
    def _register(cls):
        thread_id = threading.get_ident()
        cls.registry[thread_id] = ""

    @classmethod
    def _unregister(cls):
        thread_id = threading.get_ident()
        cls.registry.pop(thread_id, None)
        
    def write(self, value):
        thread_id = threading.get_ident()
        if thread_id not in type(self).registry.keys():
            if self.type == 0:
                sys.__stdout__.write(value)
            else:
                sys.__stderr__.write(value)
        else:
            native = iris.GatewayContext.getOutputIRIS()
            formatted_value = "\r\n".join(value.splitlines())
            if value.endswith("\n"): formatted_value += "\r\n"
            iris.irissdk.writeRedirectedOutput(native, self.type, formatted_value)
        
