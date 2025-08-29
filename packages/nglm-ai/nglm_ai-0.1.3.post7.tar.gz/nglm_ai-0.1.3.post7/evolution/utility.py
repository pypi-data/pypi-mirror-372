import importlib
import sys

def load_class(class_package: str, class_name: str, class_ref: type):
    try:
        module = importlib.import_module(class_package)
        the_class = getattr(module, class_name)
        the_instance = the_class()
        if isinstance(the_instance, class_ref):
            return the_instance
        else:
            print("unable to load plugin {}, expected {}".format(class_package, class_ref))
    except(ModuleNotFoundError, ImportError) as e:
        print(e)
        print("unable to load plugin {}, as {}".format(class_package, e))
        sys.exit(1)