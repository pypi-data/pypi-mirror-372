import importlib.metadata
import inspect

import xenoslib

__version__ = importlib.metadata.version("xenoslib")


def main():
    print(inspect.getsourcefile(xenoslib))
    print(f"installed version: {__version__}")
    print(f"code version: {xenoslib.__version__}")


if __name__ == "__main__":
    main()
