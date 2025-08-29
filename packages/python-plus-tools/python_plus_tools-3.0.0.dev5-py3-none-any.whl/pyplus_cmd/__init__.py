import backup
import configurer

from importlib.metadata import version
from os import remove, system, makedirs
from packaging.version import parse
from pathlib import Path
from requests import get, Timeout, ConnectionError
from time import sleep
from webbrowser import open as op

from configurer import config, get_config, remove_config
from markdown import markdown
from toml import load

global_config_path = Path.home() / ".xystudio" / "pyplus" / "config.toml"
local_config_path = Path.cwd() / ".xystudio" / "pyplus" / "config.toml"
data_path = Path(__file__).parents[1] / "pyplus" / "data" / "config"
global_config = {}
local_config = {}

LOCAL = "local"
GLOBAL = "global"

ALL = "all"
NEW = "news"
WILL = "will"

configurer.init(
    default_config_type=LOCAL,
    global_config_path=global_config_path,
    local_config_path=local_config_path,
    must_two_texts=True,
)
configurer.init(
    default_config_type=configurer.get_config("library.firstUsedConfig", LOCAL)
)

makedirs(global_config_path.parent, exist_ok=True)

if not global_config_path.exists():
    global_config_path.touch()
else:
    with open(global_config_path, "r", encoding="utf-8") as f:
        global_config = load(f)

makedirs(local_config_path.parent, exist_ok=True)
if not (local_config_path.exists()):
    local_config_path.touch()

try:
    with open(local_config_path, "r", encoding="utf-8") as f:
        local_config = load(f)
except FileNotFoundError:
    pass

first_used_config = get_config("library.firstUsedConfig", LOCAL)

with open(data_path / "update.toml", "r", encoding="utf-8") as f:
    updates = load(f)

with open(
    data_path / "config_help.toml",
    "r",
    encoding="utf-8",
) as f:
    config_help = load(f)

with open(data_path / "alias.toml", "r", encoding="utf-8") as f:
    lang_alias = load(f)

with open(
    data_path / "doc_help.toml",
    "r",
    encoding="utf-8",
) as f:
    doc_help = load(f)


def get_update(namespace, version):
    """get the version update doc."""
    try:
        open_dict = updates["release"][namespace]["update_info"]
    except KeyError:
        raise ValueError("This namespace not found.")

    if version == ALL:
        out_obj = open_dict
    elif version == NEW:
        out_obj = open_dict.get(
            updates["release"][namespace]["version"],
            "This version is not found. Maybe it is not recorded.",
        )
    elif version == WILL:
        out_obj = open_dict.get(
            WILL, "This version is not found. Maybe it is not recorded."
        )
    else:
        out_obj = open_dict.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )

    print(out_obj)
    return out_obj


def get_version_update_time(namespace, version):
    """Get the version update time."""
    try:
        open_dict = updates["release"][namespace]["update_time"]
    except KeyError:
        raise ValueError("This namespace not found.")

    if version == ALL:
        out_obj = open_dict
    elif version == NEW:
        out_obj = open_dict.get(
            updates["release"][namespace]["version"],
            "This version is not found. Maybe it is not recorded.",
        )
    elif version == WILL:
        raise ValueError("`get_version_update_time` cannot get will update time.")
    else:
        out_obj = open_dict.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )

    print(out_obj)
    return out_obj


def get_version(namespace):
    """Get the version."""
    return updates["release"][namespace]["version"]


def get_pre_version():
    """Get the pre version."""
    return updates["pre-release"]["version"]


def get_pre_update(version):
    """Get the pre-release version update doc."""
    try:
        open_dict = updates["pre-release"]["update_info"]
    except KeyError:
        raise ValueError("This namespace not found.")

    if version == ALL:
        out_obj = open_dict
    elif version == NEW:
        out_obj = open_dict.get(
            updates["pre-release"]["version"],
            "This version is not found. Maybe it is not recorded.",
        )
    elif version == WILL:
        out_obj = open_dict.get(
            WILL, "This version is not found. Maybe it is not recorded."
        )
    else:
        out_obj = open_dict.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )

    print(out_obj)
    return out_obj


def get_pre_version_update_time(version):
    """Get the pre-release version update time."""
    try:
        open_dict = updates["pre-release"]["update_time"]
    except KeyError:
        raise ValueError("This namespace not found.")

    if version == NEW:
        out_obj = open_dict
    elif version == NEW:
        out_obj = open_dict.get(
            updates["pre-release"]["version"],
            "This version is not found. Maybe it is not recorded.",
        )
    elif version == WILL:
        raise ValueError("`get_version_update_time` cannot get will update time.")
    else:
        out_obj = open_dict.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )
    print(out_obj)
    return out_obj


def open_doc(doc_name, lang="en"):
    doc_html_path = Path.cwd() / ".xystudio" / "pyplus" / "cache" / "doc.html"
    doc_name = doc_name.lower()

    for key, values in lang_alias.items():
        if lang.lower() in values:
            lang = key
    lang = lang.lower()

    makedirs(doc_html_path.parent, exist_ok=True)

    if doc_name == "index":
        op(data_path.parent / "docs" / "web" / lang / "index.html")
    else:
        with open(
            data_path.parent / f"docs" / "markdown" / lang / f"{doc_name}.md",
            "r",
            encoding="utf-8",
        ) as f:
            html = markdown(f.read())

        with open(doc_html_path, "w", encoding="utf-8") as f:
            f.write(html)

        op(doc_html_path)
        sleep(1)
        remove(doc_html_path)


def get_doc_help(doc_name=ALL):
    print()
    if doc_name == ALL:
        for doc_namespace, doc_des in doc_help.items():
            print(f"{doc_namespace} : {doc_des}")
    else:
        print(f"{doc_name}: {doc_help.get(doc_name, 'Not found.')}")


def get_alias(lang=ALL):
    print()
    match_alias = None
    for k, v in lang_alias.items():
        if lang.lower() in v:
            match_alias = k
            break

    if lang == ALL:
        for k, v in lang_alias.items():
            print(f"alias {k} -> {', '.join(v)}")
    elif match_alias is not None:
        print(f"alias {match_alias} -> {lang}")
    else:
        print(f"alias {lang} -> {', '.join(lang_alias.get(lang, ["Not found."]))}")


def get_config_help(config_type=ALL):
    if config_type == ALL:
        for config_t, config_docs in config_help.items():
            print("*" * 22 + "-" * 8 + config_t + "-" * 8 + "*" * 22)
            for doc_name, doc_des in config_docs.items():
                print()
                print(f"{doc_name} : {doc_des}")
            print(f"\n{'-'*30}\n")
        print(
            "\nWhen you set config,you need use 'pyplus config set local name.config value'"
        )
    else:
        print("*" * 22 + "-" * 8 + config_type + "- " * 8 + "*" * 22)
        try:
            for doc_name, doc_des in config_help[config_type].items():
                print(f"{doc_name} : {doc_des}")
        except KeyError:
            print("This document is not found.")
        else:
            print(
                "When you set config,you need use 'pyplus config set local name.config value'"
            )


def open_doc(doc_name, lang="en"):
    doc_html_path = Path.cwd() / ".xystudio" / "pyplus" / "cache" / "doc.html"
    doc_name = doc_name.lower()

    for key, values in lang_alias.items():
        if lang.lower() in values:
            lang = key
    lang = lang.lower()

    makedirs(doc_html_path.parent, exist_ok=True)

    if doc_name == "index":
        op(data_path.parent / "docs" / "web" / lang / "index.html")
    else:
        with open(
            data_path.parent / f"docs" / "markdown" / lang / f"{doc_name}.md",
            "r",
            encoding="utf-8",
        ) as f:
            html = markdown(f.read())

        with open(doc_html_path, "w", encoding="utf-8") as f:
            f.write(html)

        op(doc_html_path)
        sleep(1)
        remove(doc_html_path)


def xml_to_json(xmlFile, jsonFile):
    from xmltodict import parse
    from json import dumps

    with open(xmlFile, "r", encoding="utf-8") as f:
        json = dumps(parse(f.read()), indent=4)

    with open(jsonFile, "w", encoding="u8") as f:
        f.writelines(json)

    return "".join(json)


def csv_to_tsv(csvFile, tsvFile):
    with open(csvFile, "r", encoding="utf-8") as f:
        csv = f.readlines()

    o = []
    for i in csv:
        o.append(i.replace(", ", "\t"))

    with open(tsvFile, "w", encoding="utf-8") as f:
        f.writelines(o)
    return o


def tsv_to_csv(tsvFile, csvFile):
    with open(tsvFile, "r", encoding="utf-8") as f:
        csv = f.readlines()
    o = []

    for i in csv:
        o.append(i.replace("\t", ", "))
    with open(csvFile, "w", encoding="utf-8") as f:
        f.writelines(o)
    return o


def csv_to_json(csvFile, jsonFile):
    from json import dump

    with open(csvFile, "r", encoding="utf-8") as f:
        csv = f.read()

    with open(jsonFile, "w", encoding="utf-8") as f:
        dump(csv.split(","))


def json_to_xml(jsonFile, xmlFile):
    from json import load
    from xml.etree.ElementTree import Element, tostring

    with open(jsonFile, "r", encoding="utf-8") as f:
        json_obj = load(f)

    if isinstance(json_obj, dict):
        element = Element(json_obj.get("tag", "root"))
        for key, value in json_obj.items():
            if key == "tag":
                continue  # Skip the 'tag' key
            sub_element = Element(key)
            sub_element.text = str(value)
            element.append(sub_element)
    elif isinstance(json_obj, list):
        element = Element("root")
        for item in json_obj:
            sub_element = Element("item")
            if isinstance(item, dict):
                for k, v in item.items():
                    sub_sub_element = Element(k)
                    sub_sub_element.text = str(v)
                    sub_element.append(sub_sub_element)
            else:
                sub_element.text = str(item)
            element.append(sub_element)

    o = (
        tostring(element, encoding="utf-8", method="xml", xml_declaration=True).decode(
            "utf-8"
        )
    ).splitlines()[1]
    with open(xmlFile, "w", encoding="utf-8") as f:
        f.write(o)
    return o


def pickle_to_json(pickleFile, jsonFile):
    from json import dump
    from pickle import load

    with open(pickleFile, "rb", encoding="utf-8") as f1, open(
        jsonFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2)


def json_to_pickle(jsonFile, pickleFile):
    from pickle import dump
    from json import load

    with open(pickleFile, "wb", encoding="utf-8") as f2, open(
        jsonFile, "r", encoding="utf-8"
    ) as f1:
        dump(load(f1), f2)


def yaml_to_json(yamlFile, jsonFile):
    from yaml import load
    from json import dump

    with open(yamlFile, "r", encoding="utf-8") as f1, open(
        jsonFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2)


def json_to_yaml(jsonFile, yamlFile):
    from json import load
    from yaml import dump

    with open(jsonFile, "r", encoding="utf-8") as f1, open(
        yamlFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2, allow_unicode=True)


def toml_to_json(tomlFile, jsonFile):
    from toml import load
    from json import dump

    with open(tomlFile, "r", encoding="utf-8") as f1, open(
        jsonFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2)


def json_to_toml(jsonFile, tomlFile):
    from json import load
    from toml import dump

    with open(jsonFile, "r", encoding="utf-8") as f1, open(
        tomlFile, "w", encoding="utf-8"
    ) as f2:
        dump(load(f1), f2, allow_unicode=True)


def json_to_csv(jsonFile, csvFile):
    from json import load
    import csv

    with open(jsonFile, "r", encoding="utf-8") as f1, open(
        csvFile, "w", encoding="utf-8", newline=""
    ) as f2:
        json_obj = load(f1)
        if isinstance(json_obj, dict):
            writer = csv.DictWriter(f2, fieldnames=json_obj.keys())
            writer.writeheader()
            writer.writerow(json_obj)
        elif isinstance(json_obj, list):
            keys = set()
            for item in json_obj:
                keys.update(item.keys())
            writer = csv.DictWriter(f2, fieldnames=keys)
            writer.writeheader()
            for item in json_obj:
                writer.writerow(item)


def fetch_url(main_url, backup_urls=[], retries=3, timeout=5, **kwargs):
    all_urls = [main_url] + backup_urls

    for idx, url in enumerate(all_urls):
        for attempt in range(retries + 1):
            try:
                response = get(url, timeout=timeout, **kwargs)
                response.raise_for_status()
                return response
            except (Timeout, ConnectionError) as e:
                if attempt == retries:
                    if url != all_urls[-1]:
                        pass
                    break
    raise TimeoutError


def _get_latest_version(
    package_name,
    url="https://pypi.org/pypi/%P/json",
    extra_urls=[],
    retries=3,
    timeout=5,
    include_prerelease: bool = False,
    **kwargs,
):
    url = url.replace("%P", package_name)
    extra_urls = [i.replace("%P", package_name) for i in extra_urls]

    response = fetch_url(url, extra_urls, retries, timeout, **kwargs)

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
    installed_version = version(package_name)
    latest_version = _get_latest_version(
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


__version__ = get_version("main")
tools_version = "1.3.0"

def shell():
    print("starting shell...")

    import pyplus

    print(f'python-plus-tools {get_version("main")} ({get_pre_version()})')
    print("type exit to exit the shell.")

    all_code = []
    while True:
        try:
            code = input("pyplus >>> ")
            if code == "exit" or code == "quit" or code == "exit()" or code == "quit()":
                break
            exec(code)
            all_code.append(code)
        except KeyboardInterrupt:
            print("^C\nKeyboardInterrupt")
            break
        except EOFError:
            break
        except Exception as e:
            print(e.with_traceback(None))


def main() -> None:
    import argparse

    class globalAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            self.handle_output(parser, namespace, values)

        @staticmethod
        def handle_output(parser, namespace, values):
            setattr(namespace, "_global", values)

    class allAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            self.handle_output(parser, namespace, values)

        @staticmethod
        def handle_output(parser, namespace, values):
            setattr(namespace, "_all", values)

    class localAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            self.handle_output(parser, namespace, values)

        @staticmethod
        def handle_output(parser, namespace, values):
            setattr(namespace, "_local", values)

    parser = argparse.ArgumentParser(description="pyplus commands")
    subparsers = parser.add_subparsers(dest="command", required=False)
    
    parser.add_argument("-v", "--version", help="Get the version.", action="store_true")
    subparsers.add_parser("version", help="Get the version.").add_argument("namespace", help="A release version namespace.", nargs="?")

    config_cmd = subparsers.add_parser(
        "config",
        help="Set the config.Usage 'pyplus config get' to get all config.",
    )
    config_namespace = config_cmd.add_subparsers(dest="config_command", required=True)
    set_cmd = config_namespace.add_parser("set", help="Set the config")

    set_cmd.add_argument("setting", help="Config setting.")
    value = set_cmd.add_argument("value", help="Config value.", nargs="+")

    set_config_group = set_cmd.add_mutually_exclusive_group()
    set_config_group.add_argument(
        "-l" "--local",
        nargs=0,
        action=localAction,
        help="Config file only in your project.Local config in './.xystudio/pyplus/config.toml'",
    )
    set_config_group.add_argument(
        "-g",
        "--global",
        nargs=0,
        action=globalAction,
        help="Config file in all project.Global config in 'Users/Appdata/roaming/xystudio/pyplus/config.toml'",
    )

    get_conf = config_namespace.add_parser("get", help="Get the config.")
    config_type_group = get_conf.add_mutually_exclusive_group()
    config_type_group.add_argument(
        "-l",
        "--local",
        action=localAction,
        nargs=0,
        help="Get the local config in your project.Local config in './.xystudio/pyplus/config.toml'",
    )
    config_type_group.add_argument(
        "-g",
        "--global",
        action=globalAction,
        nargs=0,
        help="Output the global config.",
    )
    config_type_group.add_argument(
        "-a",
        "--all",
        nargs=0,
        action=allAction,
        help="Output all the config.This option is default option.",
    )

    config_namespace.add_parser("get_help", help="Get the config help.").add_argument(
        "-d",
        "--document_description",
        nargs="?",
        help="get one document description.",
        default=ALL,
    )

    remove_namespace = config_namespace.add_parser(
        "remove", help="Remove the config"
    ).add_subparsers(dest="remove_namespace", required=True)
    local_config_cmd = remove_namespace.add_parser(
        "local",
        help="Config file only in your project.Local config in './.xystudio/pyplus/config.toml'",
    )
    global_config_cmd = remove_namespace.add_parser(
        "global",
        help="Config file in all project.Global config in 'Users/Appdata/roaming/xystudio/pyplus/config.toml'",
    )

    local_config_cmd.add_argument("setting", help="Config setting.")
    global_config_cmd.add_argument("setting", help="Config setting.")
    doc_namespace = subparsers.add_parser(
        "document", help="Document name."
    ).add_subparsers(dest="doc_namespace", required=True)
    open_doc_command = doc_namespace.add_parser("open", help="Open the document.")
    open_doc_command.add_argument("doc_name", help="Document name.")
    open_doc_command.add_argument(
        "-l", "--lang", help="Document language.", nargs="?", default="en"
    )

    doc_namespace.add_parser("get_help", help="Get the document help.").add_argument(
        "-d",
        "--document_description",
        nargs="?",
        help="get one document description.",
        default=ALL,
    )

    update_namespace = subparsers.add_parser(
        "update", help="Get the update."
    ).add_subparsers(dest="update_namespace", required=True)

    pre_update_namespace = update_namespace.add_parser(
        "pre", help="Get the pre-release update."
    ).add_subparsers(dest="pre", required=True)

    release_update_namespace = update_namespace.add_parser(
        "release", help="Get the release update."
    ).add_subparsers(dest="release_namespace", required=True)

    release_update_namespace.add_parser(
        "version", help="Get a release version."
    ).add_argument("namespace", help="A release version namespace.")

    news = release_update_namespace.add_parser("news", help="Get the news.")
    news.add_argument("namespace", help="A release version namespace.", nargs="?")
    news.add_argument("version", help="release version.", nargs="?")

    time = release_update_namespace.add_parser("time", help="Get the time.")
    time.add_argument("namespace", help="A release version namespace.", nargs="?")
    time.add_argument("version", help="release version.", nargs="?")

    pre_update_namespace.add_parser("version", help="Get a pre-release version.")

    pre_update_namespace.add_parser(
        "news", help="Get the pre-release news."
    ).add_argument("version", help="pre-release version.", nargs="?")

    pre_update_namespace.add_parser(
        "time", help="Get the pre-release time."
    ).add_argument("version", help="pre-release version.", nargs="?")

    subparsers.add_parser("shell", help="run pyplus code.")

    get_alias_command = subparsers.add_parser("get_ailas", help="Get the alias.")

    get_alias_command.add_argument(
        "-l", "--lang", help="Document language.", nargs="?", default=ALL
    )

    check_namespace = subparsers.add_parser(
        "check",
        help="update & check pyplus.",
    )
    check_namespace.add_argument(
        "-a", "--auto_update", help="Auto update pyplus.", action="store_true"
    )
    check_namespace.add_argument(
        "-p", "--pre", help="Include pre-release version.", action="store_true"
    )
    check_namespace.add_argument(
        "-f",
        "--first-url",
        help="The first url to get the update.",
        default="https://pypi.org/pypi/%P/json",
    )
    check_namespace.add_argument(
        "-e", "--extra-urls", help="The extra urls to get the update.", nargs="+"
    )
    check_namespace.add_argument(
        "-r",
        "--retry-times",
        help="The retry times to get the update.",
        type=int,
        default=3,
    )
    check_namespace.add_argument(
        "-t", "--timeout", help="The timeout to get the update.", type=int, default=10
    )

    convert_namespace = subparsers.add_parser(
        "convert",
        help="convert some datafile.",
    )
    convert_namespace.add_argument("types_to_convert", help="convert types to convert.")
    convert_namespace.add_argument("convert_types", help="convert datafile to types.")
    convert_namespace.add_argument("convert_file", help="convert datafile.")
    convert_namespace.add_argument("output_file", help="output datafile.")

    backup_namespace = subparsers.add_parser(
        "backup",
        help="backup your project.",
    ).add_subparsers(dest="backup_command", required=True)

    backup.manager.exclude_rules = backup._read_exclude_rules()

    create_parser = backup_namespace.add_parser("create", help="Create a backup")
    create_parser.add_argument("name", help="Name of the backup")

    delete_parser = backup_namespace.add_parser("delete", help="Delete a backup")
    delete_parser.add_argument("name", help="Name of the backup")
    delete_parser.add_argument(
        "-i", "--index", type=int, help="Index of the backup to delete"
    )

    extract_parser = backup_namespace.add_parser("extract", help="Extract a backup")
    extract_parser.add_argument("name", help="Name of the backup")
    extract_parser.add_argument(
        "-i", "--index", type=int, help="Index of the backup to extract"
    )

    verify_parser = backup_namespace.add_parser("verify", help="Verify a backup")
    verify_parser.add_argument("name", help="Name of the backup")
    verify_parser.add_argument("hash", help="Expected SHA256 hash of the backup")
    verify_parser.add_argument(
        "-i", "--index", type=int, help="Index of the backup to verify"
    )

    exclude_parser = backup_namespace.add_parser(
        "exclude", help="Add an exclusion rule"
    )
    exclude_parser.add_argument("pattern", help="Pattern to exclude")
    exclude_parser.add_argument(
        "-t",
        "--type",
        default="wildcard",
        choices=["exact", "wildcard"],
        help="Type of match",
    )

    get_hash_parser = backup_namespace.add_parser(
        "get_hash", help="Get the SHA256 hash of a backup"
    )
    get_hash_parser.add_argument("name", help="Name of the backup")
    get_hash_parser.add_argument(
        "-i", "--index", type=int, help="Index of the backup to get the hash"
    )

    args = parser.parse_args()

    if args.command == "config":
        if args.config_command == "set":
            args.value = args.value[0] if len(args.value) == 1 else args.value
            if isinstance(args.value, str):
                if args.value.lower() == "true":
                    value = True
                elif args.value.lower() == "false":
                    value = False
                else:
                    value = args.value
            else:
                value = args.value
            if first_used_config == LOCAL:
                if hasattr(args, "_local"):
                    config(args.setting, value, LOCAL)
                    print(f"local config {args.setting} is set to {args.value}.")
                elif hasattr(args, "_global"):
                    config(args.setting, value, GLOBAL)
                    print(f"global config {args.setting} is set to {args.value}.")
                else:
                    config(args.setting, value, first_used_config)
            elif first_used_config == GLOBAL:
                if hasattr(args, "_global"):
                    config(args.setting, value, GLOBAL)
                    print(f"global config {args.setting} is set to {args.value}.")
                elif hasattr(args, "_local"):
                    config(args.setting, value, LOCAL)
                    print(f"local config {args.setting} is set to {args.value}.")
                else:
                    config(args.setting, value, first_used_config)
            else:
                print(
                    "Error: Invid config library.firstUsedConfig:"
                    + get_config("library.firstUsedConfig")
                )
        elif args.config_command == "get_help":
            get_config_help(args.document_description)
        elif args.config_command == "get":
            if first_used_config == LOCAL:
                if hasattr(args, "_all"):
                    if first_used_config == LOCAL:
                        print(global_config | local_config)
                    elif first_used_config == GLOBAL:
                        print(local_config | global_config)
                    else:
                        print(
                            "Error: Invid config library.firstUsedConfig:"
                            + get_config("library.firstUsedConfig")
                        )
                elif hasattr(args, "_local"):
                    print(local_config)
                elif hasattr(args, "_global"):
                    print(global_config)
                else:
                    print(local_config | global_config)
            elif first_used_config == GLOBAL:
                if hasattr(args, "_all"):
                    if first_used_config == LOCAL:
                        print(global_config | local_config)
                    elif first_used_config == GLOBAL:
                        print(local_config | global_config)
                    else:
                        print(
                            "Error: Invid config library.firstUsedConfig:"
                            + get_config("library.firstUsedConfig")
                        )
                elif hasattr(args, "_global"):
                    print(global_config)
                elif hasattr(args, "_local"):
                    print(local_config)
                else:
                    print(local_config | global_config)
            else:
                print(
                    "Error: Invid config library.firstUsedConfig:"
                    + get_config("library.firstUsedConfig")
                )
        elif args.config_command == "remove":
            remove_config(args.setting, args.remove_namespace)
    elif args.version:
        print("Version : pyplus pre:", get_pre_version())
        print("Version : pyplus :", get_version("main"))
        print("Version : command tools:", tools_version)
    elif args.command == "document":
        if args.doc_namespace == "open":
            open_doc(args.doc_name, args.lang)
        elif args.doc_namespace == "get_help":
            get_doc_help(args.document_description)
    elif args.command == "update":
        if args.update_namespace == "release":
            if args.release_namespace == "version":
                print(get_version(args.namespace))
            elif args.release_namespace == "news":
                print(get_update(args.namespace, args.version))
            elif args.release_namespace == "time":
                print(get_version_update_time(args.namespace, args.version))
        elif args.update_namespace == "pre":
            if args.pre == "version":
                print(get_pre_version())
            elif args.pre == "news":
                print(get_pre_update(args.version))
            elif args.pre == "time":
                print(get_pre_version_update_time(args.version))
    elif args.command == "shell":
        shell()
    elif args.command == "get_ailas":
        get_alias(args.lang)
    elif args.command == "check":
        check_update(
            "python-plus-tools",
            args.pre,
            args.auto_update,
            args.first_url,
            [] if args.extra_urls is None else args.extra_urls,
            args.retry_times,
            args.timeout,
        )
    elif args.command == "backup":
        if args.backup_command == "create":
            backup_path = backup.manager.create_backup(args.name)
            print(f"Backup created: {backup_path}")
        elif args.backup_command == "delete":
            backup.manager.delete_backup(args.name, args.index)
            print(f"Backup deleted: {args.name}")
        elif args.backup_command == "extract":
            backup.manager.extract_backup(args.name, args.index)
        elif args.backup_command == "verify":
            if backup.manager.verify_backup_hash(args.name, args.hash, args.index):
                print(f"Backup verified: {args.name}, result: {True}")
            else:
                print(f"Backup verification failed: {args.name}, result: {False}")
        elif args.backup_command == "exclude":
            backup.manager.add_exclusion_rule(args.pattern, args.type)
            backup._write_exclude_rules(backup.manager.exclude_rules)
            print(f"Exclusion rule added: {args.pattern}")
        elif args.backup_command == "get_hash":
            print(backup.manager.get_backup_hash(args.name, args.index))
    elif args.command == "convert":
        if args.types_to_convert == "json":
            if args.convert_types == "xml":
                xml_to_json(args.convert_file, args.output_file)
            elif args.convert_types == "csv":
                csv_to_json(args.convert_file, args.output_file)
            elif args.convert_types == "yaml":
                yaml_to_json(args.convert_file, args.output_file)
            elif args.convert_types == "toml":
                toml_to_json(args.convert_file, args.output_file)
            elif args.convert_types == "pickle":
                pickle_to_json(args.convert_file, args.output_file)
            else:
                print(
                    "Not support convert to json.(choose from `xml`, `csv`, `yaml`, `toml`, `pickle`."
                )
        elif args.types_to_convert == "xml":
            if args.convert_types == "json":
                json_to_xml(args.convert_file, args.output_file)
            else:
                print("Not support convert to xml.(choose from `json`)")
        elif args.types_to_convert == "csv":
            if args.convert_types == "json":
                json_to_csv(args.convert_file, args.output_file)
            else:
                print("Not support convert to csv.(choose from `json`)")
        elif args.types_to_convert == "yaml":
            if args.convert_types == "json":
                json_to_yaml(args.convert_file, args.output_file)
            else:
                print("Not support convert to yaml.(choose from `json`)")
        elif args.types_to_convert == "toml":
            if args.convert_types == "json":
                json_to_toml(args.convert_file, args.output_file)
            else:
                print("Not support convert to toml.(choose from `json`)")
        elif args.types_to_convert == "pickle":
            if args.convert_types == "json":
                json_to_pickle(args.convert_file, args.output_file)
            else:
                print("Not support convert to pickle.(choose from `json`)")
        else:
            print(
                f"Not support convert from {args.types_to_convert} to {args.convert_types}.(choose from `json`, `xml`, `csv`, `yaml`, `toml`, `pickle."
            )
    elif args.command == "version":
        if args.namespace == "pyplus": # namespaces, next version will move to data.
            print("Version : pyplus :", get_version("main"))
        elif args.namespace == "pyplus_pre":
            print("Version : pyplus pre:", get_pre_version())
        elif args.namespace == "command_tools":
            print("Version : command tools:", tools_version)
        else:
            print("Version : pyplus pre:", get_pre_version())
            print("Version : pyplus :", get_version("main"))
            print("Version : command tools:", tools_version)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
