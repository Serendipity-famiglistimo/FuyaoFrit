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
import ghpythonlib.components as ghcomp
import Rhino.Geometry as rg
import scriptcontext

class ArcDotConfig:
    def __init__(self):
        self.lr = 0
        self.sr = 0
        self.angle = 0
    
    def top(self):
        return 0
    
    def bottom(self):
        return self.lr

class ArcDot(Dot):
    def __init__(self, x, y, config, theta):
        Dot.__init__(self, y, y, config, theta)
    
    def draw(self, display, display_color):
        # draw the large circle
        angle_start = (180 - self.config.angle)  / 2
        angle_end = angle_start + self.config.angle
        center_angle = ghcomp.ConstructDomain(angle_start * 1.0 / 180  * ghcomp.Pi(), angle_end * 1.0 / 180  * ghcomp.Pi())
        center_arc, _ = ghcomp.Arc(self.centroid, self.config.sr, center_angle)
        center_start_point = center_arc.StartPoint
        center_end_point = center_arc.EndPoint
        # left center
        left_x = (self.config.lr / self.config.sr) * (center_end_point.X - self.centroid.X) + center_end_point.X
        left_y = (self.config.lr / self.config.sr) * (center_end_point.Y - self.centroid.Y) + center_end_point.Y
        # right center
        right_x = (self.config.lr / self.config.sr) * (center_start_point.X - self.centroid.X) + center_start_point.X
        right_y = (self.config.lr / self.config.sr) * (center_start_point.Y - self.centroid.Y) + center_start_point.Y

        left_angle = ghcomp.ConstructDomain(ghcomp.Pi(1.5), ghcomp.Pi(1.5) + self.config.angle * 1.0 / 2 / 180.0 * ghcomp.Pi())
        right_angle = ghcomp.ConstructDomain(ghcomp.Pi(1.5) - self.config.angle * 1.0 / 2 / 180.0 * ghcomp.Pi(), ghcomp.Pi(1.5))
        left_arc, _ = ghcomp.Arc(rg.Point3d(left_x, left_y, 0), self.config.lr, left_angle)
        right_arc, _ = ghcomp.Arc(rg.Point3d(right_x, right_y, 0), self.config.lr, right_angle)

        crv = ghcomp.JoinCurves([left_arc, center_arc, right_arc])
        
        crv, _ = ghcomp.Pufferfish.CloseCurve(crv, 0, 0.5, 0)
        rotate_angle = ghcomp.Addition(self.theta, ghcomp.Pi())
        crv, _ = ghcomp.Rotate(crv, rotate_angle, self.centroid)
        display.AddCurve(crv, display_color, 1)

    def bake(self):
        # draw the large circle
        angle_start = (180 - self.config.angle)  / 2
        angle_end = angle_start + self.config.angle
        center_angle = ghcomp.ConstructDomain(angle_start * 1.0 / 180  * ghcomp.Pi(), angle_end * 1.0 / 180  * ghcomp.Pi())
        center_arc, _ = ghcomp.Arc(self.centroid, self.config.sr, center_angle)
        center_start_point = center_arc.StartPoint
        center_end_point = center_arc.EndPoint
        # left center
        left_x = (self.config.lr / self.config.sr) * (center_end_point.X - self.centroid.X) + center_end_point.X
        left_y = (self.config.lr / self.config.sr) * (center_end_point.Y - self.centroid.Y) + center_end_point.Y
        # right center
        right_x = (self.config.lr / self.config.sr) * (center_start_point.X - self.centroid.X) + center_start_point.X
        right_y = (self.config.lr / self.config.sr) * (center_start_point.Y - self.centroid.Y) + center_start_point.Y

        left_angle = ghcomp.ConstructDomain(ghcomp.Pi(1.5), ghcomp.Pi(1.5) + self.config.angle * 1.0 / 2 / 180.0 * ghcomp.Pi())
        right_angle = ghcomp.ConstructDomain(ghcomp.Pi(1.5) - self.config.angle * 1.0 / 2 / 180.0 * ghcomp.Pi(), ghcomp.Pi(1.5))
        left_arc, _ = ghcomp.Arc(rg.Point3d(left_x, left_y, 0), self.config.lr, left_angle)
        right_arc, _ = ghcomp.Arc(rg.Point3d(right_x, right_y, 0), self.config.lr, right_angle)

        crv = ghcomp.JoinCurves([left_arc, center_arc, right_arc])
        
        crv, _ = ghcomp.Pufferfish.CloseCurve(crv, 0, 0.5, 0)
        rotate_angle = ghcomp.Addition(self.theta, ghcomp.Pi())
        crv, _ = ghcomp.Rotate(crv, rotate_angle, self.centroid)
        # pts, _, _ = ghcomp.ControlPoints(crv)
        rc = scriptcontext.doc.Objects.AddCurve(crv)
        return rc
        # return rs.AddCircle(self.centroid, self.config.r)
          