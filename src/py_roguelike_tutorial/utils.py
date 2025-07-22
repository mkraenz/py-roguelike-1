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

        if main_filepath.endswith("pytest"):
            # If running tests, use the current working directory
            cwd = os.getcwd()
            result = os.path.join(cwd, "src", filename)
            return result

        dirname = os.path.dirname(main_filepath)
        result = os.path.join(dirname, filename)
        return result
    return os.path.join(datadir, filename)
