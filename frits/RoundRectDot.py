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

class RoundRectConfig:
    def __init__(self):
        self.k = 0
        self.r = 0

class RoundRectDot(Dot):
    def __init__(self, x, y, r):
        Dot.__init__(self)
        self.centroid.X = x
        self.centroid.Y = y
        self.left = r
        self.right = r
        self.top = r
        self.bottom = r
        
        self.radius = r
     
    
    def draw(self):
        if self.display:
            self.display.AddCircle(rc.Geometry.Circle(self.centroid, self.radius), self.display_color, 1)