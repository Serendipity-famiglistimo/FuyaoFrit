#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, August 18th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
from frits import FritType
from frits.CircleDot import CircleDotConfig
from frits.RoundRectDot import RoundRectConfig

class RowRelationType:
    ALIGN=0
    CROSS=1
    @staticmethod
    def get_relations_strings():
        return ['对齐', '交错']

class RowFrits:
    def __init__(self):
        self.row_id = 0
        self.dot_type = FritType.CIRCLE_DOT
        self.dot_config = CircleDotConfig()
        self.stepping = 0
        self.position = 0

        self.circle_config = CircleDotConfig()
        self.round_rect_config = RoundRectConfig()

        self.relations = []
    
    def get_first_relation(self):
        if len(self.relations) == 0:
            return {'row_id': self.row_id - 1, 'type': RowRelationType.CROSS}
        else:
            return self.relations[0]

