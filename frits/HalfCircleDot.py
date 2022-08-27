#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, August 27th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''

import Rhino as rc
from frits.Dot import Dot
import rhinoscriptsyntax as rs

class HalfCircleDotConfig:
    def __init__(self):
        self.r = 0
    
    def top(self):
        return self.r
    
    def bottom(self):
        return self.r

class HalfCircleDot(Dot):
    def __init__(self, x, y, config):
        Dot.__init__(self)
        self.centroid.X = x
        self.centroid.Y = y
        self.config = config
     
    
    def draw(self, display, display_color):
        display.AddCircle(rc.Geometry.Circle(self.centroid, self.config.r), display_color, 1)
    
    def bake(self):
        return rs.AddCircle(self.centroid, self.config.r)