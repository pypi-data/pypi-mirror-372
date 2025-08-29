import importlib
import pkgutil

__all__ = []

# automatically import all submodules and gather their public symbols
for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{module_name}")
    if hasattr(module, "__all__"):
        __all__.extend(module.__all__)
    else:
        # include all public names (not starting with _)
        __all__.extend([name for name in dir(module) if not name.startswith("_")])
    globals().update(
        {
            name: getattr(module, name)
            for name in dir(module)
            if not name.startswith("_")
        }
    )
