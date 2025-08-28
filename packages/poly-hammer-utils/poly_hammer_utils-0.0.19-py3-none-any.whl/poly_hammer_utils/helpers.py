import os
import sys
import importlib
from types import ModuleType


def deep_reload(m: ModuleType):
    name = m.__name__  # get the name that is used in sys.modules
    name_ext = name + '.'  # support finding sub modules or packages

    def compare(loaded: str):
        return (loaded == name) or loaded.startswith(name_ext)

    all_mods = tuple(sys.modules)  # prevent changing iterable while iterating over it
    sub_mods = filter(compare, all_mods)
    for pkg in sorted(sub_mods, key=lambda item: item.count('.'), reverse=True):
        importlib.reload(sys.modules[pkg])  # reload packages, beginning with the most deeply nested


def reload_addon_source_code(addons: list[str], only_unregister: bool = False):
    """"
    Reloads the specified addons directly from their source code in the repository.
    This function forces the reloading of modules, regeneration of properties, and sends all errors
    to stderr instead of a dialog. It is the preferred method for development, as stack traces will
    link back to the source code.

    Args:
        addons (list[str]): A list of addon module names to reload.
        only_unregister (bool, optional): If True, only un-registers the addon code without re-registering. Defaults to False.
    """
    # forces reloading of modules, regeneration of properties, and sends all errors
    # to stderr instead of a dialog
    for addon in addons:
        os.environ[f'{addon.upper()}_DEV'] = '1'
        addon = importlib.import_module(addon)

        addon.unregister()
        deep_reload(addon)
        # importlib.reload(addon)

        if not only_unregister:
            addon.register()