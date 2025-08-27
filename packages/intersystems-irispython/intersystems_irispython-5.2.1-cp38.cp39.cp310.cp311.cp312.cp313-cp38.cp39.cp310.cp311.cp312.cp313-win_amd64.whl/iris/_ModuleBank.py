import datetime
import decimal
import importlib
import inspect
import os
import sys
import threading
import zipfile
import iris

class _ModuleBank(object):

    def __init__(self):
        self._sys_modules_lock = threading.RLock()
        self._thread_modules = {}
        return

    def _load_one_module(self, filename_full, process_wide):
        if filename_full is None: return
        if os.path.isdir(filename_full):
            if filename_full[-1] == os.sep:
                filename_full = os.path.join(filename_full,"__init__.py")
            else:
                filename_full = filename_full + ".__init__.py"
        if filename_full.endswith(".py"):
            filename_path = os.path.dirname(filename_full)
            filename_name = os.path.basename(filename_full)
            filename_short = filename_name.rsplit('.', 1)[0]
            with self._sys_modules_lock:
                self.__save_sys_module(process_wide)
                sys.path.insert(0,filename_path)
                importlib.import_module(filename_short)
                del sys.path[0]
                self.__restore_sys_module(process_wide)
            return
        elif filename_full.endswith(".whl"):
            ziplist = zipfile.ZipFile(filename_full).namelist()
            with self._sys_modules_lock:
                self.__save_sys_module(process_wide)
                sys.path.insert(0,filename_full)
                for file in ziplist:
                    if file.endswith(".py"):
                        package_name = file[0:-3].replace("/",".")
                        importlib.import_module(package_name)
                del sys.path[0]
                self.__restore_sys_module(process_wide)
            return
        else:
            # import built-in modules
            package_name = filename_full
            self.__save_sys_module(process_wide)
            importlib.import_module(package_name)
            self.__restore_sys_module(process_wide)
        return

    def __save_sys_module(self, process_wide):
        if process_wide: return
        self._saved_modules = sys.modules.copy()
        return

    def __restore_sys_module(self, process_wide):
        if process_wide: return
        new_modules = [key for key in sys.modules if key not in self._saved_modules] 
        for key in new_modules:
            self._thread_modules[key] = sys.modules[key]
            del sys.modules[key]
        return

    def _find_class(self, class_name):
        if class_name == "":
            return sys.modules["builtins"]
        if class_name == "**Utility**":
            class_name = "iris._GatewayUtility._GatewayUtility"
        if "." in class_name:
            module_name = class_name.rsplit(".", 1)[0]
            class_name_short = class_name.rsplit(".", 1)[1]
        else:
            module_name = None
            class_name_short = class_name
        if class_name_short == "":
            try:
                return self._thread_modules[module_name]
            except Exception as ex:
                pass
            try:
                with self._sys_modules_lock:
                    return sys.modules[module_name]
            except Exception as ex:
                pass
            raise iris.GatewayException("Module not found: " + module_name)
        else:
            for module in self._thread_modules:
                try:
                    class_object = getattr(self._thread_modules[module], class_name_short)
                    if module_name == None:
                        return class_object
                    if class_object.__module__ == module_name:
                        return class_object
                except Exception as ex:
                    pass
            with self._sys_modules_lock:
                for module in sys.modules:
                    try:
                        class_object = getattr(sys.modules[module], class_name_short)
                        if module_name == None:
                            return class_object
                        if class_object.__module__ == module_name:
                            return class_object
                    except Exception as ex:
                        pass
            raise iris.GatewayException("Class not found: " + class_name)
        return

    def _get_type_hints(self, classname, instance, method_name, cardinality):
        hints = [iris.Constant.MetaType_VARIANT]*cardinality
        try:
            if instance != None:
                method_object = getattr(instance, method_name)
            elif classname != "":
                class_object = self._find_class(classname)
                method_object = getattr(class_object, method_name)
            else:
                method_object = getattr(sys.modules["builtins"],method_name)
            pointer = 0
            params = inspect.signature(method_object).parameters
            for key in params:
                if pointer >= cardinality:
                    break
                if key == "self":
                    continue
                if params[key].kind == inspect.Parameter.POSITIONAL_ONLY or params[key].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    hints[pointer] = self._convert_type_to_meta(params[key].annotation)
                    pointer += 1
                    continue
                if params[key].kind == inspect.Parameter.VAR_POSITIONAL:
                    while (pointer<cardinality):
                        hints[pointer] = self._convert_type_to_meta(params[key].annotation)
                        pointer += 1
                    break
        except Exception as ex:
            pass
        return hints

    def _convert_type_to_meta(self, typeobject):
        try:
            if typeobject == bool:
                return iris.Constant.MetaType_BOOL
            if typeobject == int:
                return iris.Constant.MetaType_INTEGER
            if typeobject == float:
                return iris.Constant.MetaType_DOUBLE
            if typeobject == decimal.Decimal:
                return iris.Constant.MetaType_DECIMAL
            if typeobject == bytes:
                return iris.Constant.MetaType_BYTES
            if typeobject == str:
                return iris.Constant.MetaType_STRING
            if typeobject == datetime.date:
                return iris.Constant.MetaType_DATE
            if typeobject == datetime.time:
                return iris.Constant.MetaType_TIME
            if typeobject == datetime.datetime:
                return iris.Constant.MetaType_DATETIME
            if typeobject == iris.IRISList:
                return iris.Constant.MetaType_IRISLIST
            else:
                return iris.Constant.MetaType_VARIANT
        except Exception as ex:
            pass
        return iris.Constant.MetaType_VARIANT
