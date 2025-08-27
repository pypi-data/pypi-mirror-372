import threading
import iris

class _Callback(object):

    all_module_banks = {}

    @classmethod
    def _execute(cls, code, arg = None, *args):
        try:
            if code == "load_module":
                thread_id = threading.get_ident()
                filename_full = arg
                process_wide = args[0]
                module_bank = cls.all_module_banks.get(thread_id)
                if module_bank == None:
                    module_bank = iris._ModuleBank._ModuleBank()
                    cls.all_module_banks[thread_id] = module_bank
                module_bank._load_one_module(filename_full, process_wide)
                return None
            elif code == "find-class":
                thread_id = threading.get_ident()
                class_name = arg
                module_bank = cls.all_module_banks.get(thread_id)
                if module_bank == None:
                    module_bank = iris._ModuleBank._ModuleBank()
                    cls.all_module_banks[thread_id] = module_bank
                return module_bank._find_class(class_name)
            elif code == "get-type-hints":
                thread_id = threading.get_ident()
                classname = arg
                instance = args[0]
                method_name = args[1]
                cardinality = args[2]
                module_bank = cls.all_module_banks.get(thread_id)
                if module_bank == None:
                    module_bank = iris._ModuleBank._ModuleBank()
                    cls.all_module_banks[thread_id] = module_bank
                return module_bank._get_type_hints(classname, instance, method_name, cardinality)
            elif code == "initialize-thread-data":
                thread_id = threading.get_ident()
                cls.all_module_banks.pop(thread_id, None)
                return None
            elif code == "terminate-thread-data":
                thread_id = threading.get_ident()
                cls.all_module_banks.pop(thread_id, None)
                return None
            elif code == "call-gateway-thread-exit-handlers":
                iris.GatewayEvent._call_gateway_thread_exit_handlers()
                return None
            elif code == "call-gateway-process-exit-handlers":
                iris.GatewayEvent._call_gateway_process_exit_handlers()
                return None
            else:
                print("Invalid Python callback code")
                raise Exception("Invalid Python callback code")
        except Exception as e:
            raise e
