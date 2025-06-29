# main entrypoint file. I would love to name this `main.py` but nuitka drops file extensions if I use --output-filename=tstt_rl

from py_roguelike_tutorial.main import main

if __name__ == "__main__":
    main()
