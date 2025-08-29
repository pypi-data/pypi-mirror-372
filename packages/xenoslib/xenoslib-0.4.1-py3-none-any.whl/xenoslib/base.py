#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
import time
import inspect
import logging
import os

from logging.handlers import TimedRotatingFileHandler


def init_logger(
    use_file: bool = False,
    backup_count: int = 0,  # New parameter: number of log files to retain (0 means keep all)
) -> logging.Logger:
    """
    Automatically names logger after caller's filename, rotates by time, and retains specified number of log files

    Args:
        use_file: Whether to enable file logging
        backup_count: Number of historical log files to retain (default 0=keep all)
    """
    formatter = logging.Formatter(
        "%(asctime)s %(filename)s %(levelname)s [line:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers = [console_handler]

    # File handler (daily rotation + file retention policy)
    if use_file:
        # Dynamically get caller's filename
        caller_frame = inspect.stack()[1]
        caller_path = caller_frame.filename
        caller_name = os.path.splitext(caller_path)[0]
        # Configure log directory and filename
        log_filename = f"{caller_name}.log"

        file_handler = TimedRotatingFileHandler(
            log_filename,
            when="midnight",  # Rotate daily
            interval=1,
            backupCount=backup_count,  # Key parameter: controls number of retained files
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    logging.basicConfig(level=logging.INFO, handlers=handlers)


def sleep(seconds, mute=False):
    """sleep with countdown show and prevent pause or sleep of PC"""
    end = time.time() + seconds
    while time.time() < end:
        if not mute:
            print(f"ETA {seconds:.0f}/{end - time.time():.0f}  s\t", end="\r")
        time.sleep(1)


def simple_color(value, color_name="BLUE"):
    """
    return text with color, default in blue.
    "Why is it blue?"
    "It's always blue."
    """
    if sys.platform == "win32":
        return value
    colors = {
        "RED": 31,
        "GREEN": 32,
        "YELLOW": 33,
        "BLUE": 34,
        "MAGENTA": 35,
        "CYAN": 36,
    }
    return f"\033[1;{colors[color_name]}m{value}\033[0m"


def color(value, color_name="BLUE"):
    """if have colorama then use it"""
    if sys.platform == "win32":
        try:
            from colorama import Fore, Style, init

            init()
            value = getattr(Fore, color_name) + Style.BRIGHT + value + Fore.RESET
        finally:
            return value
    return simple_color(value, color_name)


class NestedData:
    """
    Utilities for working with nested data structures such as lists, dictionaries, and tuples.

    This class provides a set of methods for searching and manipulating nested data structures.
    The find_keys(), find_values(), and find_keyvalues() methods are specialized find() methods
    that search for elements with matching keys, values, or key-value pairs. The find_any_keyvalues()
    method searches for elements that contain any key or value that matches a given variable.
    The find_any() method finds the first key or value that matches a given variable, while the
    other methods search for specific keys or values.

    The class maintains state through its result and path attributes, which are updated every time a
    result is found by one of the find() methods.

    :param data: The data structure to search.
    """

    def __init__(self, data):
        self.data = data
        self.result = None  # The most recently found result.
        self.path = None  # The path to the most recently found result.
        self._condition = None  # The condition function used by the find() method.

    def _find(self, obj, path=""):
        """
        Recursively search the nested data structure for elements that match the condition function.

        :param obj: The object to search.
        :param path: The path to the object.
        :yield: A generator that yields tuples of the object and its path.
        """
        if isinstance(obj, dict):
            iter_obj = obj.items()
        elif isinstance(obj, (list, tuple)):
            iter_obj = enumerate(obj)
        else:
            return
        for k, v in iter_obj:
            new_path = f"{path}[{repr(k)}]"
            try:
                if self._condition(k, v):
                    yield obj, new_path
                    continue
            except Exception as exc:
                if not self.ignore_exc:
                    raise exc
            yield from self._find(v, new_path)

    def find(self, condition, ignore_exc=False):
        """
        Find all elements in the nested data structure that match the condition function.

        :param condition: The condition function.
        :param ignore_exc: If True, ignore any exceptions raised by the condition function.
        :return: A generator that yields tuples of the object and its path.
        """
        self.ignore_exc = ignore_exc
        self._condition = condition
        return self._find(self.data)

    def _find_one(self, method, *args, **kwagrs):
        """
        Find the first result from a generator produced by one of the find() methods.

        :param method: The find() method to use.
        :param args: The arguments to pass to the find() method.
        :param kwagrs: The keyword arguments to pass to the find() method.
        :return: The object that matches the condition, or None if no object is found.
        """
        self.path = None
        self.result = None
        for obj, path in method(*args, **kwagrs):
            self.path = path
            self.result = obj
            return obj
        return None

    def find_keys(self, key):
        """
        Find all elements in the nested data structure with matching keys.

        :param key: The key to search for.
        :return: A generator that yields tuples of the object and its path.
        """
        return self.find(lambda k, v: k == key)

    def find_values(self, value):
        """
        Find all data that matches a given value within the nested data.

        Args:
            value: The value to match against the nested data.

        Returns:
            A list of tuples containing the matched values and their corresponding paths.
        """
        return self.find(lambda k, v: v == value)

    def find_keyvalues(self, key, value):
        """
        Find all data that matches a given key-value pair within the nested data.

        Args:
            key: The key to match against the nested data.
            value: The value to match against the nested data.

        Returns:
            A list of tuples containing the matched key-value pairs and their corresponding paths.
        """
        return self.find(lambda k, v: (k, v) == (key, value))

    def find_any_keyvalues(self, var):
        """
        Find all data that matches a given key or value within the nested data.

        Args:
            var: The key or value to match against the nested data.

        Returns:
            A list of tuples containing the matched keys or values and their corresponding paths.
        """
        return self.find(lambda k, v: var in (k, v), ignore_exc=True)

    def find_any(self, var):
        """
        Find all data that matches a given key or value within the nested data.

        Args:
            var: The key or value to match against the nested data.

        Returns:
            A tuple containing the first matched key or value and its corresponding path.
        """
        return self._find_one(self.find_any_keyvalues, var)

    def find_key(self, key):
        """
        Find the value associated with a given key within the nested data.

        Args:
            key: The key to search for in the nested data.

        Returns:
            The value associated with the given key if it is found in the nested data, otherwise None.
        """
        result = self._find_one(self.find_keys, key)
        if result is not None:
            return result[key]
        return None

    def find_value(self, value):
        """
        Find the key associated with a given value within the nested data.

        Args:
            value: The value to search for in the nested data.

        Returns:
            A tuple containing the first matched key and its corresponding path if the value is found in the nested data,
            otherwise None.
        """
        return self._find_one(self.find_values, value)

    def find_keyvalue(self, key, value):
        """
        Find the path to the key-value pair within the nested data.

        Args:
            key: The key to search for in the nested data.
            value: The value to search for in the nested data.

        Returns:
            A tuple containing the first matched key-value pair and its corresponding path if it is found in the nested
            data, otherwise None.
        """
        return self._find_one(self.find_keyvalues, key, value)

    def show_result(self):
        """
        Print the most recently found result and its corresponding path.
        """
        print("Nested data result: ")
        print(self.result)
        print("Nested data path:")
        print(self.path)


class Singleton:
    """Please note that __init__() will still run every time"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance


class SingletonWithArgs:
    """带参数的单例模式, 通过继承使用，需放到第一继承位
    Please note that __init__() will still run every time
    """

    def __new__(cls, *args, **kwargs):
        arg = f"{args}{kwargs}"
        if not hasattr(cls, "_instances"):
            cls._instances = {}
        return cls._instances.setdefault(arg, super().__new__(cls))


class ArgMethodBase:
    """auto generator arguments by static methods"""

    def __init__(self, epilog=None):
        """initialize arguments parser"""
        parser = argparse.ArgumentParser(
            description=self.__doc__,
            epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        subparsers = parser.add_subparsers(title="commands", dest="command")
        for arg_map in self.__get_arg_lists__():
            sub_parser = subparsers.add_parser(arg_map["command"], help=arg_map["help"])
            for arg in arg_map["required_args"]:
                sub_parser.add_argument(arg)
            for arg, value in arg_map["optional_args"]:
                sub_parser.add_argument("--%s" % arg, type=type(value), default=value)

        args = parser.parse_args()
        if args.command is None:
            parser.print_help()
        elif self.__run_command__(**vars(args)) is False:
            print(color("ERROR", "RED"), file=sys.stderr)
            exit(-1)
        else:
            print(color("OK", "GREEN"), file=sys.stderr)

    def __run_command__(self, command, **args):
        """run a certain staticmethod"""
        return getattr(self, command)(**args)

    def __get_arg_lists__(self):
        """get arguments info lists from self class staticmethods"""
        for obj_name in dir(self):
            func = getattr(self, obj_name)
            if obj_name.startswith("__") or not callable(func):
                continue
            default_len = 0
            default_values = []
            if func.__defaults__ is not None:
                default_len = len(func.__defaults__)
                default_values = func.__defaults__
            argcount = func.__code__.co_argcount
            required_args = func.__code__.co_varnames[: argcount - default_len]
            optional_args = func.__code__.co_varnames[argcount - default_len : argcount]  # noqa
            yield {
                "command": obj_name,
                "help": func.__doc__,
                "required_args": required_args,
                "optional_args": zip(optional_args, default_values),
            }


def monkey_patch(module, obj_name, obj, package=None):
    """recursively patch obj in module"""
    if isinstance(module, str):
        # to-do if '.' in module  # seems no need to bother
        module = sys.modules[module]
    if not inspect.ismodule(module):
        raise TypeError(f"'{module}' is not module")
    if package is None:
        package = module.__package__
    if obj_name in module.__dict__:
        module.__dict__[obj_name] = obj
        print(f"Monkey patched <{obj_name}> in <{module.__name__}>", file=sys.stderr)
    for k, v in module.__dict__.items():
        if inspect.ismodule(v) and v.__package__ == package:
            monkey_patch(v, obj_name, obj, package)


def get_dict_val(dictionary, *args):
    """
    Usage:
    my_dict = {"name": "John", "age": 30, "city": "New York"}
    result = filter_dict_by_keys(environ, "CLIENT_SECRET", "age")
    print(result)  # Output: {'name': 'John', 'age': 30}
    """
    return {key: value for key, value in dictionary.items() if key in args}


def get_attr_val(obj, *args):
    """
    Usage:
    class Person:
        def __init__(self, name, age, city):
            self.name = name
            self.age = age
            self.city = city

    person = Person("John", 30, "New York")
    attributes = get_attr_val(person, "name", "age")
    print(attributes)  # Output: {'name': 'John', 'age': 30}
    """
    return {attr: getattr(obj, attr) for attr in args}


if __name__ == "__main__":

    init_logger()
    logging.info("test")
