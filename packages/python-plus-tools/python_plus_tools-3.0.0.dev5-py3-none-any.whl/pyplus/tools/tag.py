file = None
OR = "any"
AND = "all"


def get_doc(func) -> str:
    """Get the function's doc."""
    assert isinstance(func, function)
    return func.__doc__


def get_tag(func) -> list[str]:
    """
    Get the function's tag

    :param tag: the function's doc's tag.it starts in # and end in space
    :return: tag list
    """
    assert isinstance(func, function)
    start = None
    end = None
    taglist = []
    index = 0
    for i in get_doc(func):
        # print(get_doc(func)[index], end="")
        if i == "#":
            start = index
        if i == " " and start is not None:
            end = index
            output = get_doc(func)[start + 1 : end]
            if get_doc(func)[start + 1 : end] != "":
                taglist.append(output)
        index += 1

    return taglist


def tag_in_func(func, tag: str) -> bool:
    """
    Operator the tag in function

    :return: tag in function's tag.
    """
    assert isinstance(func, function) and isinstance(tag, str)
    return tag in get_tag(func)


def tags_in_func(func, tags: list[str], rule: str) -> bool:
    """
    Operator the tag list in function.

    :param rule: set the mode.if the mode is OR, any item in the list then return true.if the mode is AND, all item in the list then return true.
    :return: please look the previous.
    """
    assert isinstance(func, function) and isinstance(tag, str) and isinstance(rule, str)
    tag = get_tag(func)
    if rule == OR:
        for i in tag:
            if i in tags:
                return True
        return False
    elif rule == AND:
        for i in tag:
            if i not in tags:
                return False
        return True
    else:
        raise KeyError("rule'" + str(rule) + "'is not a tick type.")
