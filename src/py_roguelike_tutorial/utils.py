import os
import sys


def assets_filepath(path_relative_to_main: str):
    main_filepath = sys.modules["__main__"].__file__
    if main_filepath is None:
        raise SystemExit("TSTT: Entry point not found.")
    dirname = os.path.dirname(main_filepath)
    print("dirname", dirname)
    filename = os.path.join(dirname, path_relative_to_main)
    print("filename", filename)
    return filename
