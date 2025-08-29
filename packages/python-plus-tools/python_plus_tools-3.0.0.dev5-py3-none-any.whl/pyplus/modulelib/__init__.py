from importlib import *

from toml import load, dump
from site import getsitepackages
from pathlib import Path
import configurer

configurer.init(
    default_config_type="local",
    global_config_path=Path.home() / ".xystudio" / "pyplus" / "config.toml",
    local_config_path=Path.cwd() / ".xystudio" / "pyplus" / "config.toml",
    must_two_texts=True,
)
configurer.init(default_config_type=configurer.get_config("library.firstUsedConfig"))


def get_import_moudle_path():
    from sys import modules

    if __name__ != "__main__":
        main_moudle = modules["__main__"]
        if hasattr(main_moudle, "__file__"):
            return main_moudle.__file__
        else:
            return None


def get_latest_version(package_name, include_prerelease: bool = False, url: str = None):
    import requests
    from packaging.version import parse

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://pypi.org/",
    }

    url = (
        f"https://pypi.org/pypi/{package_name}/json"
        if url is None
        else url.replace("%P", package_name)
    )
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    data = response.json()
    all_versions = list(data["releases"].keys())

    valid_versions = []
    for v in all_versions:
        version = parse(v)
        if not include_prerelease and version.is_prerelease:
            continue
        valid_versions.append(version)

    if not valid_versions:
        return None
    latest = max(valid_versions)
    return str(latest)


def check_update(
    package_name,
    include_prerelease=False,
    auto_update=False,
    first_url="https://pypi.org/pypi/%P/json",
    extra_urls=[],
    retry_times=3,
    timeout=10,
    **kwargs,
):
    from importlib.metadata import version
    from packaging.version import parse
    from os import system

    installed_version = version(package_name)
    latest_version = get_latest_version(
        package_name,
        first_url,
        extra_urls,
        retry_times,
        timeout,
        include_prerelease,
        **kwargs,
    )

    if latest_version:
        installed_parsed = parse(installed_version)
        latest_parsed = parse(latest_version)
        needs_update = installed_parsed < latest_parsed
    else:
        needs_update = False

    if latest_version and needs_update:
        if include_prerelease:
            print(
                f"New pre-release version available: {installed_version} → {latest_version}"
            )
        else:
            print(f"New version available: {installed_version} → {latest_version}")
        if auto_update:
            print("Auto-updating...")
            if include_prerelease:
                system(f"pip install --upgrade --pre {package_name}")
            else:
                system(f"pip install --upgrade {package_name}")
            print("Update complete.")
    else:
        print("Already up to date.")


class LazyImport:
    def __init__(self, module_name):
        self.module_name = module_name
        self._module = None

    def __getattr__(self, name):
        if self._module is None:
            self._module = import_module(self.module_name)
        return getattr(self._module, name)


del Path, load, dump, getsitepackages, configurer
