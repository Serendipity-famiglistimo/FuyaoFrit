#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, August 22nd 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
from Zone import Zone
import math
from frits import FritType
from frits.CircleDot import CircleDot, CircleDotConfig
from frits.RoundRectDot import RoundRectConfig, RoundRectDot
import Rhino.Geometry as rg
import ghpythonlib.components as ghcomp

class dzBlockZone(Zone):
    def __init__(self):
        Zone.__init__(self)
        self.type = 'block'
        # 每一排都包括row id
        # row从下往上编号为0， 1， 2， 3， 4...
        # row 从上往下编号为-1, -2, -3...
        self.rows = list()
        self.holes = list()
        self.curves = [None, None, None, None, None, None]
        self.is_flip = [False, False, False, False, False, False]
        self.block_dots = []
        self.dots = []