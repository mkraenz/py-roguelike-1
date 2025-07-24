# Py Roguelike Tutorial

[Ref](https://rogueliketutorials.com/tutorials/tcod/v2/part-0/)

## Get Started

```sh
uv sync
```

Restart your terminal to make sure the virtual env gets activated.

Make sure your vscode instance is using the virtual env. (Command palette -> Python: Select Interpreter -> Select the virtual env in `.venv/...`)

```sh
uv run python ./src/tstt_rl.py
```

### Type checking

```sh
pyright src
```

or more easily, run the vs code task `type-check`.

### Hot module reload

To some degree hot module reload is possible. Some parts do not allow hot modular reload unfortunately so be aware of that.
To enable hot module reload, run the vs code task: `hot-swap game`

## Package and Deploy

Following this [comment on reddit](https://www.reddit.com/r/roguelikedev/comments/st5imr/comment/hx1pwdb/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button), we use pyinstaller but copy assets manually instead of fiddling with pyinstaller's `--add-data`.

```sh
rm -rf dist
uv run nuitka src/tstt_rl.py \
        --mode=app \
        --output-dir=dist \
        --include-data-dir=src/assets=assets \
        --include-module=tcod
```

The `dist/tstt_rl.bin` or `dist/tstt_rl.exe` is what can be shared. This works under Ubuntu 24.04.

You should now be able to run the game (including assets).
