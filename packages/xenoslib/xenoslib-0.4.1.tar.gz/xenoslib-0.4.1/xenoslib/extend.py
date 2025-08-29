#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import logging

import yaml
import requests

from xenoslib.tools import ConfigLoader  # noqa compactive


logger = logging.getLogger(__name__)


class YamlConfig(dict):
    """A thread unsafe yaml file config utility , can work as a dict except __init__"""

    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, name, value):
        try:
            getattr(super(), name)
        except AttributeError as exc:
            if str(exc).startswith("'super' object has no attribute "):
                self[name] = value
                return
            raise exc
        raise AttributeError(f"'{__class__.__name__}' object attribute '{name}' is read-only")

    def __str__(self):
        return yaml.safe_dump(self.copy(), allow_unicode=True)

    def __repr__(self):
        return repr(str(self))

    def __init__(self, conf_path=None):
        pass

    def __new__(cls, conf_path="config.yml", *args, **kwargs):
        if not hasattr(cls, "_instances"):
            cls._instances = {}
        if cls._instances.get(conf_path) is None:
            cls._instances[conf_path] = super().__new__(cls)
            super().__setattr__(cls._instances[conf_path], "_conf_path", conf_path)
        cls._instances[conf_path]._load_conf()
        return cls._instances[conf_path]

    def _load_conf(self):
        if os.path.exists(self._conf_path):
            with open(self._conf_path, encoding="utf-8") as r:
                self.update(yaml.safe_load(r))

    def save(self):
        data = str(self)
        with open(self._conf_path, "w", encoding="utf-8") as w:
            w.write(data)
            # yaml.safe_dump(self.copy(), w, allow_unicode=True)


class RequestAdapter:
    def request(self, method, path, *args, **kwargs):
        """to-do: support stream=True"""
        url = f"{self.base_url}/{path}"
        logger.debug(url)
        response = self.session.request(method, url, *args, **kwargs)
        logger.debug(response.text)
        response.raise_for_status()
        try:
            return response.json()
        except Exception as exc:
            logger.debug(exc)
            return response

    def get(self, path, *args, **kwargs):
        return self.request("get", path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        return self.request("post", path, *args, **kwargs)

    def put(self, path, *args, **kwargs):
        return self.request("put", path, *args, **kwargs)

    def delete(self, path, *args, **kwargs):
        return self.request("delete", path, *args, **kwargs)

    def patch(self, path, *args, **kwargs):
        return self.request("patch", path, *args, **kwargs)

    def head(self, path, *args, **kwargs):
        return self.request("head", path, *args, **kwargs)

    def __init__(self):
        self.session = requests.Session()


def del_to_recyclebin(filepath, on_fail_delete=False):
    """delete file to recyclebin if possible"""
    if not sys.platform == "win32":
        if on_fail_delete:
            os.remove(filepath)
            return True
        return False
    from win32com.shell import shell, shellcon

    res, _ = shell.SHFileOperation(
        (
            0,
            shellcon.FO_DELETE,
            filepath,
            None,
            shellcon.FOF_SILENT | shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION,
            None,
            None,
        )
    )
    return res == 0


def send_notify(msg, key):
    """send a message for ifttt"""
    url = f"https://maker.ifttt.com/trigger/message/with/key/{key}"
    data = {"value1": msg}
    return requests.post(url, data=data, timeout=(30, 30))


class IFTTTLogHandler(logging.Handler):
    """
    log handler for IFTTT
    usage：
    key = 'xxxxx.xxxzx.xxxzx.xxxzx'
    iftttloghandler = IFTTTLogHandler(key, level=logging.INFO)
    logging.getLogger(__name__).addHandler(iftttloghandler)
    """

    def __init__(self, key, level=logging.CRITICAL, *args, **kwargs):
        self.key = key
        super().__init__(level=level, *args, **kwargs)

    def emit(self, record):
        try:
            send_notify(self.format(record), self.key)
        except Exception as exc:
            print(exc)


class SlackLogHandler(logging.Handler):
    """
    log handler for Slack
    usage：
    slackloghandler = SlackLogHandler(webhook_url, level=logging.INFO)
    logging.getLogger(__name__).addHandler(slackloghandler)
    """

    def __init__(self, webhook_url, level=logging.CRITICAL, *args, **kwargs):
        self.url = webhook_url
        self.headers = {"Content-type": "application/json"}
        super().__init__(level=level, *args, **kwargs)

    def emit(self, record):
        try:
            data = {"text": self.format(record)}
            requests.post(self.url, headers=self.headers, json=data, timeout=(30, 30))
        except Exception as exc:
            print(exc)


class DingTalkLogHandler(logging.Handler):
    """
    log handler for DingTalk
    usage：
    token = 'xxxxx.xxxzx.xxxzx.xxxzx'
    dingtalkloghandler = DingTalkLogHandler(token, level=logging.INFO)
    logging.getLogger(__name__).addHandler(dingtalkloghandler)
    """

    def __init__(self, token, level=logging.CRITICAL, *args, **kwargs):
        self.token = token
        super().__init__(level=level, *args, **kwargs)

    def emit(self, record):
        headers = {"Content-Type": "application/json"}
        url = "https://oapi.dingtalk.com/robot/send"
        params = {"access_token": self.token}
        msg = self.format(record)
        data = {"msgtype": "text", "text": {"content": msg}}
        try:
            response = requests.post(
                url, headers=headers, params=params, json=data, timeout=(10, 10)
            )
            print(response.json())
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    pass
