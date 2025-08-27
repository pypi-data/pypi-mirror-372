# -*- coding: utf-8 -*-
""" Singleton pattern implementation for lazy-loading modules.

This module provides a Singleton class that allows lazy-loading of modules. The
:class:`Singleton` instance is used as a namespace for the modules that are
imported. When an attribute is accessed, the corresponding module is imported
and stored in the :attr:`_modules`

This pattern is particularly useful when the modules are not always needed, and
importing them would slow down the startup time of the application, or when
there are extra dependencies that are not always required.
"""


class SingletonBase:
    """Singleton pattern implementation for lazy-loading modules."""

    def __init__(self):
        self._modules = {}

    def __getattr__(self, module_name):
        if module_name not in self._modules:
            try:
                self._modules[module_name] = __import__(module_name)
            except (ModuleNotFoundError, ImportError) as me:
                if module_name in ("swifter", "py_fatigue"):
                    raise ImportError(
                        f"\033[31mThe \033[1m'{module_name}'\033[22m module "
                        f"is required for this functionality.\n"
                        "             Reinstall \033[31;1mapi-24sea\033[22m "
                        "with the \033[31;1m 'fatigue'\033[22m extra, i.e.,\n"
                        "\033[0m             >>> \033[32;1mpip \033[0minstall "
                        f"api-24sea[fatigue]"
                    )
                else:
                    raise me
        return self._modules[module_name]


Singleton = SingletonBase()
