#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import logging


logger = logging.getLogger(__name__)


class RestartWhenModified:
    """restart python script if scripts modified"""

    records = {}

    def __init__(self, *files):
        time_format = "%Y-%m-%d %H:%M:%S"
        files = list(files)
        files.append(os.path.abspath(sys.argv[0]))
        logger.debug(f"detecting file update for files: {files}")
        for file in files:
            file = os.path.abspath(file)
            mtime_now = os.path.getmtime(file)
            mtime_before = self.records.get(file)
            if self.records.get(file) and mtime_now != mtime_before:
                time_before = time.strftime(time_format, time.localtime(mtime_before))
                time_after = time.strftime(time_format, time.localtime(mtime_now))
                logger.info(
                    f"file [{file}] mtime changed from <{time_before}> to <{time_after}>, restarting..."
                )
                self.restart()
            self.records[file] = mtime_now

    @staticmethod
    def restart():
        python = sys.executable
        os.execl(python, python, *[f'"{i}"' if " " in i else i for i in sys.argv])
