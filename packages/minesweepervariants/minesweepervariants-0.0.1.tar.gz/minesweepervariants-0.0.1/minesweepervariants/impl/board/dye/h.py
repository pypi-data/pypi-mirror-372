#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# @Time    : 2025/07/28 03:26
# @Author  : Wu_RH
# @FileName: h.py

from ....utils.tool import get_random
from . import AbstractDye


class DyeC(AbstractDye):
    name = "h"
    __doc__ = "随机染色(50%)"

    def dye(self, board):
        positions = [pos for pos, _ in board()]
        positions = get_random().sample(positions, len(positions) // 2)
        for pos in positions:
            board.set_dyed(pos, True)
