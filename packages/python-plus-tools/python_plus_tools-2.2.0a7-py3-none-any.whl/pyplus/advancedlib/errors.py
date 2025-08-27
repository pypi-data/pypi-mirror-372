from errno import *
import warnings
from deprecated import deprecated


def NotCompleted(*args: object):
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*arg, **kwargs):
            raise NotImplementedError(*args)

        return wrapper

    return decorator


def assertTure(condition: bool, message: str = ""):
    if not condition:
        raise AssertionError(message)


def assertFalse(condition: bool, message: str = ""):
    if condition:
        raise AssertionError(message)


def show_lirary_deprecated_warning(library: str, version: str, message: str = ""):
    import configurer
    from pathlib import Path
    import colorama

    colorama.init(autoreset=True)
    configurer.init(
        default_config_type="local",
        local_config_path=Path.cwd() / ".xystudio" / "pyplus" / "config.toml",
        must_two_texts=True,
    )

    if configurer.get_config(
        f"library.showDeprecatedWarning", True, "all"
    ) and configurer.get_config(f"{library}.showDeprecatedWarning", True, "all"):
        warnings.warn(
            f"{colorama.Fore.YELLOW}{library} is deprecated since version {version}. {message}",
            DeprecationWarning,
        )
