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

class RoundRectConfig:
    def __init__(self):
        self.k = 0
        self.r = 0

class RoundRectDot(Dot):
    def __init__(self, x, y, k, r, theta):
        Dot.__init__(self)
        self.centroid.X = x
        self.centroid.Y = y
        self.k = k
        self.r = r
        self.theta = theta
    
    def draw(self, display):
        # display.AddCircle(rc.Geometry.Circle(self.centroid, self.radius), self.display_color, 1)
        display_color = rc.Display.ColorHSL(0.83,1.0,0.5)
        x = self.centroid.X
        y = self.centroid.Y
        x_domain = ghcomp.ConstructDomain(ghcomp.Subtraction(x, self.k / 2), ghcomp.Addition(x, self.k / 2))
        y_domain = ghcomp.ConstructDomain(ghcomp.Subtraction(y, self.k / 2), ghcomp.Addition(y, self.k / 2))
        rec, _ = ghcomp.Rectangle(ghcomp.XYPlane(), x_domain, y_domain, ghcomp.Division(self.r, 2))
        rec, _ = ghcomp.Rotate(rec, self.theta, rc.Geometry.Point3d(x, y, 0))
        display.AddCurve(rec, display_color, 1)

        