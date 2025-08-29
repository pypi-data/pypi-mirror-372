# snaketrail

Trace the snake 🐍: list **transitive local imports** (files & namespace packages) and report **unused .py files** under your project root — without executing your code.

## Install
```bash
pip install snaketrail
```

lets say you have a Handler.py
thats your main entrypoint to your project,
and you want to see which files it uses.
but you more importantly want to see which files
it DOESNT use and to tell what is deprecated and 
just test files.

```
# from your project root
snaketrail Handler.py
snaketrail Handler.py --verbose
snaketrail Handler.py --root /path/to/project

> Unused local Python files:
>  - debug.py
>  - test.py

```

now you can safely burn those deprecated files
that your main program never touches, or tuck
them away into a deprecated/ folder and nobody will
ever look at them again.

probably.
