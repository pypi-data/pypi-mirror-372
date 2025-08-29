from logging import getLogger
from importlib import import_module
import inspect
from itertools import chain
import sys
from shutil import get_terminal_size

from .samizdat import SamizdatView, SamizdatMaterializedView, SamizdatFunction, SamizdatTrigger, SamizdatMeta, SamizdatFunctionMeta, SamizdatTriggerMeta
from .const import env
from .exceptions import UnqualifiedModulePathException

logger = getLogger(__name__)

AUTOLOAD_MODULENAME = "dbsamizdat_defs"

def module_not_found_help(modulename, exception, pypath):
    separator = min(len(str(exception)), get_terminal_size().columns) * '='
    withsearchpath = f'''using Python import search path "{pypath}" ''' if pypath is not None else ''
    return f'''
Fatal: Loading module "{modulename}" {withsearchpath}failed with error:

{separator}
{exception}
{separator}

If you're unsure on how to solve this, try one of the following suggestions:

a.  Invoke dbsamizdat while you are one level below the directory
    (say, "somedirectory") in which your module resides.
    You can then use "somedirectory" as a package name.
    Thus `python -m somedirectory.{modulename}` should work from there, too.

b.  If passing module paths, try passing file paths instead, and vice versa.

c.  If the error points to problems importing third-party modules, and you're
    using these third-party packages from a virtual environment, it'd be best
    to simply install dbsamizdat inside that virtual environment, too, and
    to then invoke your virtualenv's version of dbsamizdat.
    If that's not possible try using the PYTHONPATH environment variable to
    make those other modules importable. You can see which paths you might want
    to add by loading your virtualenv and executing
    `python -c 'import sys; print("\\n".join(filter(None, sys.path)))'` .

    Documentation on the PYTHONPATH environment variable can be found here:
    https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH
'''


def get_samizdats(modulelist=tuple(), context=0):

    def issamizdat(thing):
        excluded_classes = {SamizdatView, SamizdatMaterializedView, SamizdatFunction, SamizdatTrigger}
        return inspect.isclass(thing) and isinstance(thing, (SamizdatMeta, SamizdatFunctionMeta, SamizdatTriggerMeta)) and (thing not in excluded_classes)

    sdmodules = []
    if not (context & env.DJANGO):
        for (pypath, modulepath) in modulelist:
            try:
                if pypath is None:
                    # it's a module path
                    if '.' not in modulepath:
                        raise UnqualifiedModulePathException(f'No package name supplied for module "{modulepath}".')
                    sys.path.insert(0, '.')
                    sdmodules.append(import_module(modulepath))
                else:
                    # it's a file path. Won't work so well for files directly in the root (/) as then there'll be no
                    # package namespace.
                    sys.path.insert(0, str(pypath.parent))
                    sdmodules.append(import_module(f'{pypath.name}.{modulepath}'))
            except (UnqualifiedModulePathException, ModuleNotFoundError) as notfounderror:
                if (context & env.CLI):
                    exit(module_not_found_help(modulepath, notfounderror, pypath))
                else:
                    raise
            finally:
                sys.path.pop(0)
    else:
        # if we're running in Django, we will autoload definitions from:
        # - the modules named in settings.DBSAMIZDAT_MODULES
        # - the module with name AUTOLOAD_MODULENAME of each app
        try:
            from django.core.exceptions import ImproperlyConfigured
            from django.conf import settings
            from django.apps import apps
        except ImportError as e:
            exit(f"Loading Django modules failed:\n{e}")
        else:
            try:
                django_sdmodules = [import_module(sdmod) for sdmod in getattr(settings, 'DBSAMIZDAT_MODULES', [])]
                for appconfig in apps.get_app_configs():
                    try:
                        django_sdmodules.append(import_module('{}.{}'.format(appconfig.module.__package__, AUTOLOAD_MODULENAME)))
                    except ModuleNotFoundError as err:
                        if not err.msg.endswith(f"{AUTOLOAD_MODULENAME}'"):
                            raise err
                if not django_sdmodules:
                    logger.warn(f"""No settings.DBSAMIZDAT_MODULES defined, and none of your apps contain any "{AUTOLOAD_MODULENAME}" module to autoload.""")
                sdmodules += django_sdmodules
            except ImproperlyConfigured:
                # assume we're not running in a fully booted Django
                pass


    def dep_closure(cls):
        yield cls
        for dep in cls.deps_on:
            if not issamizdat(dep):
                yield dep
            else:
                yield from dep_closure(dep)


    directly_imported_sds = {c for cname, c in chain.from_iterable(map(lambda m: inspect.getmembers(m, issamizdat), sdmodules))}
    sd_closure = set(chain.from_iterable((dep_closure(sd) for sd in directly_imported_sds)))
    return sd_closure
