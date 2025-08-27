from pathlib import Path

if not __import__("os").path.exists(
    __import__("sys").prefix + "\\share_variables\\"
) and __import__("os").path.isdir(__import__("sys").prefix + "\\share_variables"):
    if __import__("os").path.isdir(__import__("sys").prefix + "\\share_variables\\"):
        __import__("os").remove(__import__("sys").prefix + "\\share_variables\\")
    __import__("os").mkdir(__import__("sys").prefix + "\\share_variables\\")

var_path = Path(__import__("sys").prefix, "share", "pyplus", "variables")
share_temp = {}
UPLOAD = "upload"
DELETE = "delete"


def append(**kwargs):
    """Add the variable to temp, if variable in temp, set the variable."""
    for k, v in kwargs.items():
        share_temp[k] = v


def get_this_file(key: str = None) -> dict:
    """get the keys variable, if keys is none, return the temp list, else return the key variable`s value."""
    try:
        return share_temp[key]
    except KeyError:
        raise NameError(key + " is not in temp.")


def delete(key: str):
    """delete the temp keys."""
    try:
        del share_temp[key]
    except KeyError:
        raise NameError(key + " is not in temp.")


def set(**kwargs):
    """Same as add."""
    for k, v in kwargs.items():
        share_temp[k] = v


def change(key: str, op, dv):
    """change the variable"""
    try:
        share_temp[key] = op(share_temp[key], dv)
    except KeyError:
        raise NameError(key + " is not in temp.")


def in_temp(key: str, false_output=None, true_output=None):
    """Choose the temp, if false_output is not None and key not in temp, print it and return False, else return True.
    if true_output is not None and key in temp, print it and return True, else return False.
    """
    if false_output is not None and key not in share_temp:
        print(false_output)
    if true_output is not None and key in share_temp:
        print(true_output)
    return key in share_temp


def clear():
    "clear the temp."
    global share_temp
    share_temp = {}


def share(do_type: str, share_name: str):
    "share the file variables."
    if do_type == UPLOAD:
        import pickle

        with open(var_path / share_name + ".shr", "wb") as f:
            pickle.dump(share_temp, f)
    elif do_type == DELETE:
        __import__("os").remove(var_path / share_name + ".share")
    else:
        raise KeyError("key" + str(type) + "is not a select.")


def get_share_file(share_name: str):
    "get the share file variables."
    from pickle import load

    with open(var_path / (share_name + ".shr"), "rb") as f:
        return load(f)


del Path
