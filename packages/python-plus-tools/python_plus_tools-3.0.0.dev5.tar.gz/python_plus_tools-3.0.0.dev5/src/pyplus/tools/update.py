"""A version control moudle."""

from ..science.units import Version

VERSION = ""
UPDATE_DOC = {}
UPDATE_TIME = {}

PRE_VERSION = ""
PRE_UPDATE_DOC = {}
PRE_UPDATE_TIME = {}

ALL = "all"
NEW = "news"
WILL = "will"


def get_update(version: str):
    """get the version update doc."""
    if version == ALL:
        out_obj = UPDATE_DOC
    elif version == NEW:
        out_obj = UPDATE_DOC.get(
            str(VERSION), "This version is not found. Maybe it is not recorded."
        )
    elif version == WILL:
        out_obj = UPDATE_DOC.get(
            WILL, "This version is not found. Maybe it is not recorded."
        )
    else:
        out_obj = UPDATE_DOC.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )
    print(out_obj)
    return out_obj


def get_version_update_time(version: str):
    """Get the version update time."""
    if version == NEW:
        out_obj = UPDATE_TIME.get(
            str(VERSION), "This version is not found. Maybe it is not recorded."
        )
    elif version == ALL:
        out_obj = UPDATE_TIME
    elif version == WILL:
        raise ValueError("`get_version_update_time` cannot get will update time.")
    else:
        out_obj = UPDATE_TIME.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )
    print(out_obj)
    return out_obj


def get_will():
    """Get the will update doc."""
    return get_update(WILL)


def get_version():
    """Get the version."""
    return VERSION


def get_pre_version():
    """Get the pre version."""
    return PRE_VERSION


def get_news_update_time():
    """Get the new update time."""
    return get_version_update_time(NEW)


def get_new():
    """Get the new update doc."""
    return get_update(NEW)


def get_all():
    """Get the all update doc."""
    return get_update(ALL)


def get_will():
    """Get the will update doc."""
    return get_update(WILL)


def get_pre_update(version: str):
    """Get the pre-release version update doc."""
    if version == ALL:
        out_obj = PRE_UPDATE_DOC
    elif version == NEW:
        out_obj = PRE_UPDATE_DOC.get(str(version))
    elif version == WILL:
        out_obj = PRE_UPDATE_DOC.get(
            WILL, "This version is not found. Maybe it is not recorded."
        )
    else:
        out_obj = PRE_UPDATE_DOC.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )
    print(out_obj)
    return out_obj


def get_pre_version_update_time(version: str):
    """Get the pre-release version update time."""
    if version == NEW:
        out_obj = PRE_UPDATE_TIME.get(str(VERSION))
    elif version == ALL:
        out_obj = PRE_UPDATE_TIME.get(str(VERSION))
    elif version == WILL:
        raise ValueError("`get_version_update_time` cannot get will update time.")
    else:
        out_obj = PRE_UPDATE_TIME.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )
    print(out_obj)
    return out_obj


def get_pre_news_update_time():
    """Get the new update time."""
    return get_pre_version_update_time(NEW)


def get_pre_new():
    """Get the new pre-release update doc."""
    return get_pre_update(NEW)


def get_pre_all():
    """Get the all pre-release update doc."""
    return get_pre_update(ALL)


def get_update_from_toml(
    toml_file,
    code_name=None,
    uploaded: bool = True,
    has_pre: bool = False,
    encoding="utf-8",
):
    """
    Get the update info from toml file.
    Toml format example:
    [release]
    main.version = "1.0.0"
    main.update_info = { '1.0.0' = "Fix some bug.",'1.0.1' = "Modify code." }
    main.update_time = { '1.0.0' = 2025-06-01, '1.0.1' = 2025-06-05 }
    [pre-release]
    main.version = "1.0.2pre1"
    main.update_info = { '1.0.2pre1' = "Add a function" }
    main.update_time = { '1.0.2pre1' = 2025-06-06 }
    """
    import toml

    with open(toml_file, "r", encoding=encoding) as f:
        data = toml.load(f)

    VERSION = data["release"][code_name]["version"]
    UPDATE_DOC = data["release"][code_name]["update_info"]
    UPDATE_TIME = data["release"][code_name]["update_time"]
    if has_pre:
        PRE_VERSION = data["pre-release"][code_name]["version"]
        PRE_UPDATE_DOC = data["pre-release"][code_name]["update_info"]
        PRE_UPDATE_TIME = data["pre-release"][code_name]["update_time"]
    else:
        PRE_VERSION = ""
        PRE_UPDATE_DOC = {}
        PRE_UPDATE_TIME = {}

    if uploaded:
        upload(VERSION, UPDATE_DOC, UPDATE_TIME, PRE_VERSION)

    return (
        VERSION,
        UPDATE_DOC,
        UPDATE_TIME,
        PRE_VERSION,
        PRE_UPDATE_DOC,
        PRE_UPDATE_TIME,
    )


def upload(
    version: str = VERSION,
    update_info: dict[str, str] = UPDATE_DOC,
    time: dict[str, str] = UPDATE_TIME,
    pre_version: str = PRE_VERSION,
    pre_doc: dict[str, str] = PRE_UPDATE_DOC,
    pre_time: dict[str, str] = PRE_UPDATE_TIME,
):
    """Upload info.All the use module user can read this."""
    global VERSION, UPDATE_DOC, UPDATE_TIME, PRE_VERSION, PRE_UPDATE_DOC, PRE_UPDATE_TIME

    VERSION = version
    UPDATE_DOC = update_info
    UPDATE_TIME = time
    PRE_VERSION = pre_version
    PRE_UPDATE_DOC = pre_doc
    PRE_UPDATE_TIME = pre_time
