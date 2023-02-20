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
import ghpythonlib.components as ghcomp
import rhinoscriptsyntax as rs
import scriptcontext

class RoundRectConfig:
    def __init__(self):
        self.k = 0
        self.r = 0
        #如下是奥迪复杂算法的参数初始化
        self.outer_block_k = 0
        self.outer_block_r = 0
        self.inner_block_k = 0
        self.inner_block_r = 0
        self.border_k = 0
        self.border_r = 0
        self.black_band_k1 = 0
        self.black_band_h1 = 0
        self.black_band_k2 = 0
        self.black_band_h2 = 0
        self.down_block_area_k1 = 0
        self.down_block_area_k2 = 0
        self.down_block_area_k3 = 0
        self.down_block_area_k4 = 0
        self.down_block_area_k5 = 0
        self.down_block_area_h1 = 0
        self.down_block_area_h2 = 0
        self.down_block_area_h3 = 0
        self.down_block_area_h4 = 0
        self.down_block_area_h5 = 0
        self.down_horizontal = 0
        self.down_vertical = 0
        
    
    def top(self):
        return self.k / 2
    
    def bottom(self):
        return self.k / 2

class RoundRectDot(Dot):
    def __init__(self, x, y, config, theta):
        Dot.__init__(self, x, y, config, theta)
    
    def draw(self, display, display_color):
        x = self.centroid.X
        y = self.centroid.Y
        x_domain = ghcomp.ConstructDomain(ghcomp.Subtraction(x, self.config.k / 2), ghcomp.Addition(x, self.config.k / 2))
        y_domain = ghcomp.ConstructDomain(ghcomp.Subtraction(y, self.config.k / 2), ghcomp.Addition(y, self.config.k / 2))
        rec, _ = ghcomp.Rectangle(rs.WorldXYPlane(), x_domain, y_domain, self.config.r)
        rec, _ = ghcomp.Rotate(rec, self.theta, self.centroid)
        self.curve = rec
        display.AddCurve(rec, display_color, 1)
    
    def bake(self):
        if self.curve:
            rc = scriptcontext.doc.Objects.AddCurve(self.curve)
            return rc
        return None
        