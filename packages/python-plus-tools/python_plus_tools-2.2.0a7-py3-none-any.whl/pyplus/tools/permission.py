import operator

juris = {}
player_level = {}

LEVEL = "level"
JURIS_NAME = "juris"
PLAYER_NAME = "player"
if not __import__("os").path.exists(
    __import__("sys").prefix + "\\juris"
) and __import__("os").path.isdir(__import__("sys").prefix + "\\juris"):
    if __import__("os").path.isdir(__import__("sys").prefix + "\\juris"):
        __import__("os").remove(__import__("sys").prefix + "\\juris")
    __import__("os").mkdir(__import__("sys").prefix + "\\juris")


def append(**kwargs):
    """Add the juris to juris, if juris in juris, set the juris."""
    for k, v in kwargs.items():
        juris[k] = v


def get(key: str = None) -> dict:
    """get the keys juris, if keys is none, return the juris list, else return the key juris`s value."""
    try:
        return juris[key]
    except:
        raise NameError(key + " is not in juris.")


def set(**kwargs):
    """Same as and."""
    for k, v in kwargs.items():
        juris[k] = v


def judge(jurises, level):
    try:
        return juris[jurises] == level
    except Exception as e:
        raise NameError(e)


def juris_in_list(type, judge):
    if type == LEVEL:
        for k, v in juris.items():
            if v == judge:
                return True
        return False
    elif type == JURIS_NAME:
        return judge in juris
    else:
        raise NameError(type + " is not in temp.")


def get_player(key: str = None) -> dict:
    """get the player juris"""
    try:
        return player_level[key]
    except:
        raise NameError(key + " is not in juris.")


def change_player(func, num, key: str = None) -> dict:
    """get the player juris"""
    try:
        player_level[key] = func(player_level[key], num)
        return player_level[key]
    except:
        raise NameError(key + " is not in juris.")


def del_player(key: str):
    """delete the player keys."""
    try:
        del player_level[key]
    except:
        raise NameError(key + " is not in juris.")


def set_player(**kwargs):
    """Set the player Level"""
    for k, v in kwargs.items():
        player_level[k] = juris[v]


def player_judge(type, judge):
    if type == LEVEL:
        for k, v in player_level.items():
            if juris[k] == judge:
                return True
        return False
    elif type == PLAYER_NAME:
        return judge in player_level
    else:
        raise NameError(type + " is not in temp.")


def download(name):
    import pickle

    with open(__import__("sys").prefix + "\\juris\\" + name + ".jur", "rb") as f:
        pickle.load(f)


def upload(name):
    import pickle

    with open(__import__("sys").prefix + "\\juris\\" + name + ".jur", "wb") as f:
        pickle.dump([juris, player_level], f)


class User:
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def change(self, do, value):
        self.level = do(self.level, value)
        return self

    def operator(self, do, value):
        if isinstance(value, User):
            return do(self.level, value.level)
        elif isinstance(value, int):
            return do(self.level, value)
        else:
            raise TypeError(
                "value '"
                + str(value)
                + "' is"
                + str(type(value))
                + ", not User or int."
            )

    def __eq__(self, value: int):
        return self.operator(operator.eq, value)

    def __ne__(self, value: int):
        return self.operator(operator.ne, value)

    def __lt__(self, value: int):
        return self.operator(operator.lt, value)

    def __gt__(self, value: int):
        return self.operator(operator.gt, value)

    def __le__(self, value: int):
        return self.operator(operator.le, value)

    def __ge__(self, value: int):
        return self.operator(operator.ge, value)

    def __add__(self, value: int):
        return self.change(operator.add, value)

    def __sub__(self, value: int):
        return self.change(operator.sub, value)

    def __radd__(self, value: int):
        return self.change(operator.add, value)

    def __rsub__(self, value: int):
        return self.change(operator.sub, value)

    def __lshift__(self, value):
        return self.change(operator.sub, value)

    def __rlshift__(self, value):
        return self.change(operator.sub, value)

    def __rshift__(self, value):
        return self.change(operator.add, value)

    def __rrshift__(self, value):
        return self.change(operator.add, value)
