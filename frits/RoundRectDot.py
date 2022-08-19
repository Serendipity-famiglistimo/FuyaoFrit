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
    def __init__(self, x, y, k, r):
        Dot.__init__(self)
        self.centroid.X = x
        self.centroid.Y = y
        self.k = k
        self.r = r
    
    def draw(self, display):
        display = rc.Display.CustomDisplay(True)
        # display.AddCircle(rc.Geometry.Circle(self.centroid, self.radius), self.display_color, 1)
        display_color = rc.Display.ColorHSL(0.83,1.0,0.5)
        pts = []
        pts.append(rc.Geometry.Point3d(self.centroid.X - self.k / 2, self.centroid.Y - self.k / 2, 0))
        pts.append(rc.Geometry.Point3d(self.centroid.X - self.k / 2, self.centroid.Y + self.k / 2, 0))
        pts.append(rc.Geometry.Point3d(self.centroid.X + self.k / 2, self.centroid.Y + self.k / 2, 0))
        pts.append(rc.Geometry.Point3d(self.centroid.X + self.k / 2, self.centroid.Y - self.k / 2, 0))
        pts.append(rc.Geometry.Point3d(self.centroid.X - self.k / 2, self.centroid.Y - self.k / 2, 0))
        display.AddPolygon(pts, display_color, display_color, False, True)
        # display.AddLine(rc.Geometry.Line(), display_color, 1)
        # display.AddLine(rc.Geometry.Line(), display_color, 1)
        # display.AddLine(rc.Geometry.Line(), display_color, 1)
        # display.AddLine(rc.Geometry.Line(), display_color, 1)
        # display.AddArc(rc.Geometry.Arc(), display_color, 1)
        