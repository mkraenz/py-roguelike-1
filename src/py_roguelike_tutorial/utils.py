import os
import sys


def assets_filepath(filename: str):
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = sys.prefix  # datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        main_filepath = sys.modules["__main__"].__file__
        if main_filepath is None:
            raise SystemExit("TSTT: Entry point not found.")
        dirname = os.path.dirname(main_filepath)
        filename = os.path.join(dirname, filename)
        return filename
    return os.path.join(datadir, filename)
