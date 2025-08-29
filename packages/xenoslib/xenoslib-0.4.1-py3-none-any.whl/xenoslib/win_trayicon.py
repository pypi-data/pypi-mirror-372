#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This lib make it easy to create a windows tray icon application with console.
Thanks for Fumiya Shibamata from github:
https://github.com/sbfm/easyToast
"""
import logging
import os
import sys
import time
import threading
import ctypes
from functools import partial

import win32con
import win32console

try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

logger = logging.getLogger(__name__)


class Thread(threading.Thread):
    def kill(self):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(self.ident)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
        while self.is_alive():
            time.sleep(0.05)


class MenuItem:
    def __init__(self, checked=True, grayed=False):
        self.checked = checked
        self.grayed = grayed

    def action(self):
        self.checked = not self.checked
        logger.debug(f"[{self.__class__.__name__}] status: {self.checked}")


class MenuItemThread(MenuItem):
    def __init__(self, daemon=True, checked=True, **kwargs):
        self.kwargs = kwargs
        self.daemon = daemon
        super().__init__(checked=checked)

    def start_a_thread(self):
        self.thread = Thread(**self.kwargs, daemon=self.daemon)
        self.thread.start()

    @property
    def checked(self):
        if not hasattr(self, "thread"):
            return False
        return self.thread.is_alive()

    @checked.setter
    def checked(self, value):
        if value:
            self.start_a_thread()
        elif self.checked:
            self.thread.kill()
            logger.info(f"{self.thread.name} killed.")

    def action(self):
        super().action()


class MenuItemConsole(MenuItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hconsole = win32console.GetConsoleWindow()

    def is_window_visible_not_minimized(self):
        """返回窗口是否可见且不处于最小化状态"""
        visible = win32gui.IsWindowVisible(self.hconsole)
        minimized = win32gui.IsIconic(self.hconsole)
        logger.debug(f"window visible: {visible}, window minimized: {minimized}")
        return visible and not minimized

    def action(self, show=None):
        if show is None:
            # super().action()
            self.checked = not self.is_window_visible_not_minimized()
            # logger.info(self.checked)
        else:
            self.checked = show
        win32gui.ShowWindow(self.hconsole, self.checked)
        if self.checked:
            try:
                # win32gui.BringWindowToTop(self.hconsole)
                win32gui.SetForegroundWindow(self.hconsole)
                # ctypes.windll.user32.SetForegroundWindow(self.hconsole)
            except Exception as exc:
                logger.debug(exc, exc_info=True)

    def remove_close_button_from_console(self):
        hmenu = win32gui.GetSystemMenu(self.hconsole, 0)
        if hmenu:
            win32gui.DeleteMenu(hmenu, win32con.SC_CLOSE, win32con.MF_BYCOMMAND)


class SysTrayIcon:
    """sys tray icon app class"""

    FIRST_ID = 1023
    WINDOW_CLASS_NAME = "PySysTrayIcon"

    def init_icon(self, iconpath=None):
        if not iconpath:
            python_path = os.path.dirname(os.path.abspath(sys.executable))
            iconpath = os.path.join(python_path, "DLLs", "pyd.ico")
            logger.debug(f"Load icon from path: {iconpath}")
        if os.path.isfile(iconpath):
            hinst = win32gui.GetModuleHandle(None)
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst, iconpath, win32con.IMAGE_ICON, 0, 0, icon_flags)
        else:
            logger.warning("Can't find icon file - using default.")
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        self.hicon = hicon

    def quit(self):
        win32gui.DestroyWindow(self.hwnd)

    def __init__(self, icon=None, tips=None, menu_options=(), on_quit=None, left_click_action=None):
        self.init_icon(icon)
        self.tips = tips or os.path.basename(sys.argv[0])
        self.on_quit = on_quit
        self.left_click_action = left_click_action
        self.menu_options = dict(enumerate(menu_options, self.FIRST_ID))
        # menu_options should be like a list of ('text', function),
        # "function" could also be '-' for separate, MenuItem for checkable item, other type will make item disable
        self.create_window()
        self.draw_notify_icon(fresh=True)

    def create_window(self):
        message_map = {
            win32gui.RegisterWindowMessage("TaskbarCreated"): self.on_restart,
            win32con.WM_DESTROY: self.on_destroy,
            win32con.WM_COMMAND: self.on_command,
            win32con.WM_USER + 20: self.on_notify_icon,
        }
        # Register the Window class.
        window_class = win32gui.WNDCLASS()
        hinst = window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.lpszClassName = self.WINDOW_CLASS_NAME
        # window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW  # 垂直/水平方向变化自动重绘，似乎没啥用
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        window_class.lpfnWndProc = message_map
        classAtom = win32gui.RegisterClass(window_class)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(
            classAtom,
            self.WINDOW_CLASS_NAME,
            style,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            hinst,
            None,
        )
        win32gui.UpdateWindow(self.hwnd)

    def show_menu(self):
        hmenu = win32gui.CreatePopupMenu()
        self.create_menu(hmenu)

        pos = win32gui.GetCursorPos()
        # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        try:
            # 获取窗口当前状态
            placement = win32gui.GetWindowPlacement(self.hwnd)
            # 如果窗口当前是最小化状态，则还原窗口
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.hwnd)
        except Exception as exc:
            logger.debug(exc, exc_info=True)
            return
        win32gui.TrackPopupMenu(hmenu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
        win32gui.PostMessage(
            self.hwnd, win32con.WM_NULL, 0, 0
        )  # send a null message, seems useless

    def create_menu(self, hmenu):
        for option_id, option in self.menu_options.items():
            option_text, option_obj = option
            if callable(option_text):
                option_text = option_text()
            flag = win32con.MF_STRING
            if option_obj == "-":
                flag = win32con.MF_SEPARATOR
            elif isinstance(option_obj, MenuItem):
                flag = (
                    flag
                    | win32con.MF_GRAYED * option_obj.grayed
                    | win32con.MF_CHECKED * option_obj.checked
                )
            elif callable(option_obj):
                pass
            else:  # option_obj is None
                flag = flag | win32con.MF_GRAYED
            win32gui.AppendMenu(hmenu, flag, option_id, option_text)
        if self.menu_options.get(self.FIRST_ID):
            win32gui.SetMenuDefaultItem(hmenu, self.FIRST_ID, 0)

    def start(self):
        win32gui.PumpMessages()

    def draw_notify_icon(self, title="", info="", hicon=None, fresh=False):
        # See https://docs.microsoft.com/en-us/windows/win32/api/shellapi/ns-shellapi-notifyicondataw
        NIIF_USER = 0x00000004
        NIIF_NOSOUND = 0x00000010
        NIIF_LARGE_ICON = 0x00000020
        flag = win32gui.NIF_INFO if info else win32gui.NIF_MESSAGE
        notify_id = (
            self.hwnd,
            0,
            win32gui.NIF_ICON | win32gui.NIF_TIP | flag,
            win32con.WM_USER + 20,
            hicon if hicon else self.hicon,
            self.tips,
            info,
            4,
            title,
            (NIIF_USER | NIIF_NOSOUND | NIIF_LARGE_ICON),
        )
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD if fresh else win32gui.NIM_MODIFY, notify_id)

    def on_restart(self, hwnd, msg, wparam, lparam):
        self.draw_notify_icon()

    def on_destroy(self, hwnd, msg, wparam, lparam):
        if callable(self.on_quit):
            self.on_quit()
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)  # Terminate the app.
        return True

    def on_notify_icon(self, hwnd, msg, wparam, lparam):
        """callback on catch tray icon events"""
        if lparam == win32con.WM_LBUTTONDBLCLK:
            self.execute_menu_option(self.FIRST_ID)
        elif lparam == win32con.WM_RBUTTONUP:
            self.draw_notify_icon()
            self.show_menu()
        elif lparam == win32con.WM_LBUTTONDOWN:
            self.draw_notify_icon()
            if callable(self.left_click_action):
                self.left_click_action()
        return True

    def on_command(self, hwnd, msg, wparam, lparam):
        # option_id = win32gui.LOWORD(wparam)
        # self.execute_menu_option(option_id)
        self.execute_menu_option(wparam)
        return True

    def execute_menu_option(self, option_id):
        menu_text, menu_action = self.menu_options[option_id]
        if callable(menu_text):
            menu_text = menu_text()
        logger.debug(f"menu action: [{menu_text}]")
        if callable(menu_action):
            menu_action()
        elif isinstance(menu_action, MenuItem):
            menu_action.action()


class SysTrayIconApp(SysTrayIcon):
    def __init__(self, extra_menu_options=(), hide_console_at_start=True, *args, **kwargs):
        self.console_switcher = MenuItemConsole()
        self.enable_notifications = MenuItem()
        if hide_console_at_start:
            self.console_switcher.action()
        title = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        menu_options = (
            (f"[{title}] Show Console (&S)", partial(self.console_switcher.action, True)),
            ("Hide Console (&H)", partial(self.console_switcher.action, False)),
            ("-", "-"),
            *extra_menu_options,
            *((("-", "-"),) if extra_menu_options else ()),
            ("Enable Notifications (&N)", self.enable_notifications),
            ("-", "-"),
            ("Clear Console (&C)", partial(os.system, "cls")),
            ("Open Containing Folder (&O)", partial(os.system, "explorer .")),
            ("Restart (&T)", self.restart_script),
            ("Exit (&X)", self.quit),
        )
        super().__init__(
            menu_options=menu_options,
            left_click_action=self.console_switcher.action,
            *args,
            **kwargs,
        )

    @staticmethod
    def restart_script():
        python = sys.executable
        os.execl(python, python, *[f'"{i}"' if " " in i else i for i in sys.argv])

    def toast(self, title="", info="", levelname=None):
        if not self.enable_notifications.checked:
            return
        icon_map = {
            # 'INFO': win32con.IDI_INFORMATION,
            "WARNING": win32con.IDI_WARNING,
            "ERROR": win32con.IDI_ERROR,
            "CRITICAL": win32con.IDI_ERROR,
        }
        icon_id = icon_map.get(levelname)
        hicon = win32gui.LoadIcon(0, icon_id) if icon_id else None
        self.draw_notify_icon(title=title, info=info, hicon=hicon)

    def start(self):
        """rewrite To make Ctrl-C works"""
        while True:
            result = win32gui.PumpWaitingMessages()
            if result:
                return
            time.sleep(0.05)


class ToastLogHandler(logging.Handler):
    """
    log handler for SysTrayIcon
    Usage:
    tray_app = SysTrayIconApp(**kwargs)
    toasthandler = ToastLogHandler(tray_app.toast)
    logging.getLogger(__name__).addHandler(toasthandler)
    """

    def __init__(self, callback, level=logging.INFO, *args, **kwargs):
        super().__init__(level=level, *args, **kwargs)
        self.callback = callback

    def emit(self, record):
        title = record.filename if record.name == "__main__" else record.name
        self.callback(title=title, info=self.format(record), levelname=record.levelname)
