# Py Roguelike Tutorial

[Ref](https://rogueliketutorials.com/tutorials/tcod/v2/part-0/)

## Get Started

```sh
uv sync
```

Restart your terminal to make sure the virtual env gets activated.

Make sure your vscode instance is using the virtual env. (Command palette -> Python: Select Interpreter -> Select the virtual env in `.venv/...`)

```sh
python ./src/main.py
```

### Type checking

```sh
pyright .
```

## Package and Deploy

Following this [comment on reddit](https://www.reddit.com/r/roguelikedev/comments/st5imr/comment/hx1pwdb/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button), we use pyinstaller but copy assets manually instead of fiddling with pyinstaller's `--add-data`.

```sh
rm -rf dist build
pyinstaller src/main.py -n tstt_rl --noconfirm
cp -r assets dist/tstt_rl
zip -r dist/tstt_rl dist
```

The zip is what is getting shared. This works under Ubuntu 24.04.

You should now be able to run the game (including assets)

```sh
cd dist/tstt_rl
./tstt_rl
```
