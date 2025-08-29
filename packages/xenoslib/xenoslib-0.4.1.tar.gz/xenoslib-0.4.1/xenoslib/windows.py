#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import ctypes
import time
import msvcrt
import winreg


class RunAsAdmin:
    """
    Usage: RunAsAdmin(main, cmd=True)
    """

    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as exc:
            print(exc)
            return False

    def __init__(self, func, cmd=False):
        if self.is_admin():
            func()
            return
        elif cmd:
            self.run_as_admin_in_cmd()
        else:
            self.run_as_admin()
        print("Need administrator privilege, trying run as admin...")
        # self.show_cmd_line()

    @staticmethod
    def show_cmd_line():
        print(sys.executable, " ".join(sys.argv))
        line = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
        print(line)
        return line

    @staticmethod
    def run_as_admin():
        args = [os.path.abspath(sys.argv[0]), *sys.argv[1:]]
        args_with_quotes = " ".join([f'"{arg}"' if " " in arg else arg for arg in args])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, args_with_quotes, None, 1
        )

    @staticmethod
    def run_as_admin_in_cmd():
        args = [sys.executable, os.path.abspath(sys.argv[0]), *sys.argv[1:]]
        args_with_quotes = " ".join([f'"{arg}"' if " " in arg else arg for arg in args])
        arg_line = f'/k "{args_with_quotes}"'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd", arg_line, None, 1)


def pause():
    """pause"""
    print("Press any key to continue...")
    msvcrt.getch()
    while msvcrt.kbhit():
        msvcrt.getch()


def timeout(seconds):
    for second in range(seconds - 1, -1, -1):
        if msvcrt.kbhit():
            break
        print(f"Waiting {second}s , press any key to continue...", end="\r")
        time.sleep(1)
    print()  # make sure the message won't be covered


class Environment:
    reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"

    def __init__(self):
        pass

    def refresh(self):
        """refresh environment after updated"""
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002

        result = ctypes.c_long()
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result),
        )

    def set(self, key, value):
        print(f"Setting [{key}] to windows environment...")
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, self.reg_path, 0, winreg.KEY_ALL_ACCESS
        ) as reg_key:
            winreg.SetValueEx(reg_key, key, 0, winreg.REG_EXPAND_SZ, value)
            print(f"Setted [{key}] to windows environment.")

    def get(self, key):
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, self.reg_path, 0, winreg.KEY_ALL_ACCESS
        ) as reg_key:
            value, _ = winreg.QueryValueEx(reg_key, key)
            return value

    def update(self, environs):
        for key, value in environs.items():
            self.set(key, value)
        self.refresh()


def add_windows_path_env(new_path):
    """Add directory to Windows path environment variable"""
    env = Environment()
    path_str = env.get("Path")
    path_list = path_str.split(";")
    if new_path in path_list:
        print(f"{new_path} already exists in the path, skip.")
        return False
    else:
        path_list.append(new_path)
        new_path_list = ";".join(path_list)
        try:
            env.update({"Path": new_path_list})
            print(f"Added {new_path} to the path")
            return True
        except Exception as exc:
            print(f"Failed to update the path: {str(exc)}")
            return False


def test():
    """test only"""
    add_windows_path_env("c:\\abcdx")
    pause()


if __name__ == "__main__":
    RunAsAdmin(test, cmd=False)
