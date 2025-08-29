#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import os
import termios
import select
import tty


def pause():
    print("Press any key to continue...")
    old_settings = termios.tcgetattr(sys.stdin)  # get settings for stdin
    new_settings = old_settings[:]

    # [3]means c_lflag local mode
    new_settings[3] &= ~termios.ICANON  # use non-canonical mode
    new_settings[3] &= ~termios.ECHO  # no echo

    termios.tcsetattr(sys.stdin, termios.TCSANOW, new_settings)  # apply new settings
    os.read(sys.stdin.fileno(), 7)  # read characters
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)  # recover terminal


def timeout(seconds):
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    for second in range(seconds - 1, -1, -1):
        print(f"Waiting {second}s , press any key to continue...", end="\r")
        break_flag = False
        for i in range(1000):
            time.sleep(0.001)
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                sys.stdin.read(1)
                break_flag = True
                break
        if break_flag:
            break
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)  # recover terminal


if __name__ == "__main__":
    pause()
