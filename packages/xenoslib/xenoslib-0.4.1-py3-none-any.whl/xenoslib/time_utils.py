#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Xenos Lu
# @Created : 2023-01
# @Updated : 2025-08-14
import os
import logging
import inspect
from datetime import datetime

logger = logging.getLogger(__name__)


# 添加多语言支持
def get_system_language():
    """获取系统语言环境"""
    lang = os.getenv("LANG", "").split(".")[0]
    return lang if lang and "_" in lang else "en_US"


# 创建翻译字典
TRANSLATIONS = {
    "zh_CN": {
        "days": ("天", "天"),
        "hours": ("小时", "小时"),
        "minutes": ("分钟", "分钟"),
        "seconds": ("秒", "秒"),
        "updated": "最近更新",
        "ago": "前",
        "file_error": "获取文件信息失败",
    },
    "en_US": {
        "days": ("day", "days"),
        "hours": ("hour", "hours"),
        "minutes": ("minute", "minutes"),
        "seconds": ("second", "seconds"),
        "updated": "last updated",
        "ago": "ago",
        "file_error": "Failed to get file info",
    },
}


def timedelta_to_human_readable(delta, lang=None):
    """将时间差转换为人类可读格式（支持中英双语）"""
    if lang is None:
        lang = get_system_language()

    trans = TRANSLATIONS.get(lang, TRANSLATIONS["en_US"])
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_units = {
        "days": (days, trans["days"]),
        "hours": (hours, trans["hours"]),
        "minutes": (minutes, trans["minutes"]),
        "seconds": (seconds, trans["seconds"]),
    }

    for unit, (value, labels) in time_units.items():
        if value > 0:
            # 处理英文单复数
            if lang.startswith("en_") and value > 1:
                return f"{value} {labels[1]}"
            return f"{value}{labels[0]}" if lang.startswith("zh_") else f"{value} {labels[0]}"

    # 默认返回0秒
    zero_label = "0" + trans["seconds"][0] if lang.startswith("zh_") else f"0 {trans['seconds'][1]}"
    return zero_label


def log_file_update_time(lang=None):
    """显示调用文件最近更新时间（支持中英双语）"""
    if lang is None:
        lang = get_system_language()
    trans = TRANSLATIONS.get(lang, TRANSLATIONS["en_US"])

    try:
        stack = inspect.stack()
        for frame_info in stack:
            if frame_info.filename != __file__:
                file_path = frame_info.filename
                break
        else:
            file_path = __file__

        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        delta_str = timedelta_to_human_readable(datetime.now() - mtime, lang)
        filename = os.path.basename(file_path)

        # 双语日志输出
        log_msg = (
            f"{filename} {trans['updated']}: "
            f"{mtime:%Y-%m-%d %H:%M} ({delta_str} {trans['ago']})"
        )
        logger.info(log_msg)
    except Exception as e:
        logger.error(f"{trans['file_error']}: {e}")
