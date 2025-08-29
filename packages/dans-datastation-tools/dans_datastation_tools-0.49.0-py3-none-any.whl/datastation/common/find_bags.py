import os


def find_bags(path, max_depth=1) -> list:
    """
    Find all bags in the given path, up to the given depth. If the path is a bag, it will be returned. If the path is
    a directory, it will be searched for bags. If the path is a file, it will be ignored.

    Note that, for the purposes of this function, a bag is defined as a directory that contains a file named bagit.txt.
    The function does not check the contents of the file, nor does it check that the directory contains any other
    files or directories required to make it a valid bag.

    :param path: The path to search for bags.
    :param max_depth: The maximum depth to search for bags. 0 means only
      the given path will be examined to see if the directory is bag, 1 means the given path and its immediate children
      will be searched, 2 will include grandchildren, etc. A negative value means the search will be unlimited.
    """
    if os.path.isfile(path):
        return
    if is_bag(path):
        yield path
    if max_depth == 0:
        return
    for entry in os.listdir(path):
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            yield from find_bags(entry_path, max_depth - 1)


def is_bag(path: str) -> bool:
    return os.path.exists(os.path.join(path, 'bagit.txt'))
