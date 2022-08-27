#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Tuesday, August 16th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import Rhino as rc
from frits.Dot import Dot
import rhinoscriptsyntax as rs
import scriptcontext

class CircleDotConfig:
    def __init__(self):
        self.r = 0
    
    def top(self):
        return self.r
    
    def bottom(self):
        return self.r

class CircleDot(Dot):
    def __init__(self, x, y, config, theta=0):
        Dot.__init__(self, x, y, config, theta)
    
    def draw(self, display, display_color):
        self.curve = rc.Geometry.Circle(self.centroid, self.config.r)
        display.AddCircle(self.curve, display_color, 1)
    
    def bake(self):
        if self.curve:
            rc = scriptcontext.doc.Objects.AddCircle(self.curve)
            return rc
        return None
            