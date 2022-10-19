#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Saturday, October 15th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
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

class TriArcConfig:
    def __init__(self):
        self.lr = 0
        self.sr = 0
        self.angle = 0
    
    def top(self):
        return 0
    
    def bottom(self):
        return self.lr

class TriArc(Dot):
    def __init__(self, x, y, config, theta):
        Dot.__init__(self, x, y, config, theta)
    
    def draw(self, display, display_color):
        # draw the large circle
        angle1 = 34.256
        angle2 = 72.872
        angle_start = (180 - angle1)  / 2
        angle_end = angle_start + angle1
        center_angle = ghcomp.ConstructDomain(angle_start * 1.0 / 180  * ghcomp.Pi(), angle_end * 1.0 / 180  * ghcomp.Pi())
        center_arc, _ = ghcomp.Arc(self.centroid, self.config.lr, center_angle)
        center_start_point = center_arc.StartPoint
        center_end_point = center_arc.EndPoint
        # left center
        left_x = -(self.config.sr / self.config.lr) * (center_end_point.X - self.centroid.X) + center_end_point.X
        left_y = -(self.config.sr / self.config.lr) * (center_end_point.Y - self.centroid.Y) + center_end_point.Y
        # right center
        right_x = -(self.config.sr / self.config.lr) * (center_start_point.X - self.centroid.X) + center_start_point.X
        right_y = -(self.config.sr / self.config.lr) * (center_start_point.Y - self.centroid.Y) + center_start_point.Y
       
      
        left_angle = ghcomp.ConstructDomain( angle_end * 1.0 / 180  * ghcomp.Pi(), ghcomp.Pi())
        right_angle = ghcomp.ConstructDomain(0, angle_start * 1.0 / 180  * ghcomp.Pi())
        left_arc, _ = ghcomp.Arc(rg.Point3d(left_x, left_y, 0), self.config.sr, left_angle)
        right_arc, _ = ghcomp.Arc(rg.Point3d(right_x, right_y, 0), self.config.sr, right_angle)
        right_start_point = right_arc.StartPoint
        left_end_point = left_arc.EndPoint
        # left center
        left_x2 = (0.7 / self.config.sr) * (left_end_point.X - left_x) + left_end_point.X
        left_y2 = (0.7 / self.config.sr) * (left_end_point.Y - left_y) + left_end_point.Y
        # right center
        right_x2 = (0.7 / self.config.sr) * (right_start_point.X - right_x) + right_start_point.X
        right_y2 = (0.7 / self.config.sr) * (right_start_point.Y - right_y) + right_start_point.Y

        left_angle2 = ghcomp.ConstructDomain(ghcomp.Pi(1.5), ghcomp.Pi(2))
        right_angle2 = ghcomp.ConstructDomain(ghcomp.Pi(), ghcomp.Pi(1.5))
        left_arc2, _ = ghcomp.Arc(rg.Point3d(left_x2, left_y2, 0), 0.7, left_angle2)
        right_arc2, _ = ghcomp.Arc(rg.Point3d(right_x2, right_y2, 0), 0.7, right_angle2)


        crv = ghcomp.JoinCurves([left_arc2, left_arc, center_arc, right_arc, right_arc2])
        
        crv, _ = ghcomp.Pufferfish.CloseCurve(crv, 0, 0.5, 0)
        rotate_angle = ghcomp.Addition(self.theta, ghcomp.Pi())
        crv, _ = ghcomp.Rotate(crv, rotate_angle, self.centroid)
        display.AddCurve(crv, display_color, 1)

    def bake(self):
        # draw the large circle
        angle1 = 34.256
        angle2 = 72.872
        angle_start = (180 - angle1)  / 2
        angle_end = angle_start + angle1
        center_angle = ghcomp.ConstructDomain(angle_start * 1.0 / 180  * ghcomp.Pi(), angle_end * 1.0 / 180  * ghcomp.Pi())
        center_arc, _ = ghcomp.Arc(self.centroid, self.config.lr, center_angle)
        center_start_point = center_arc.StartPoint
        center_end_point = center_arc.EndPoint
        # left center
        left_x = -(self.config.sr / self.config.lr) * (center_end_point.X - self.centroid.X) + center_end_point.X
        left_y = -(self.config.sr / self.config.lr) * (center_end_point.Y - self.centroid.Y) + center_end_point.Y
        # right center
        right_x = -(self.config.sr / self.config.lr) * (center_start_point.X - self.centroid.X) + center_start_point.X
        right_y = -(self.config.sr / self.config.lr) * (center_start_point.Y - self.centroid.Y) + center_start_point.Y
        left_angle = ghcomp.ConstructDomain( angle_end * 1.0 / 180  * ghcomp.Pi(), ghcomp.Pi())
        right_angle = ghcomp.ConstructDomain(0, angle_start * 1.0 / 180  * ghcomp.Pi())
        left_arc, _ = ghcomp.Arc(rg.Point3d(left_x, left_y, 0), self.config.sr, left_angle)
        right_arc, _ = ghcomp.Arc(rg.Point3d(right_x, right_y, 0), self.config.sr, right_angle)
        right_start_point = right_arc.StartPoint
        left_end_point = left_arc.EndPoint
        # left center
        left_x2 = (0.7 / self.config.sr) * (left_end_point.X - left_x) + left_end_point.X
        left_y2 = (0.7 / self.config.sr) * (left_end_point.Y - left_y) + left_end_point.Y
        # right center
        right_x2 = (0.7 / self.config.sr) * (right_start_point.X - right_x) + right_start_point.X
        right_y2 = (0.7 / self.config.sr) * (right_start_point.Y - right_y) + right_start_point.Y

        left_angle2 = ghcomp.ConstructDomain(ghcomp.Pi(1.5), ghcomp.Pi(2))
        right_angle2 = ghcomp.ConstructDomain(ghcomp.Pi(), ghcomp.Pi(1.5))
        left_arc2, _ = ghcomp.Arc(rg.Point3d(left_x2, left_y2, 0), 0.7, left_angle2)
        right_arc2, _ = ghcomp.Arc(rg.Point3d(right_x2, right_y2, 0), 0.7, right_angle2)


        crv = ghcomp.JoinCurves([left_arc2, left_arc, center_arc, right_arc, right_arc2])
        
        crv, _ = ghcomp.Pufferfish.CloseCurve(crv, 0, 0.5, 0)
        rotate_angle = ghcomp.Addition(self.theta, ghcomp.Pi())
        crv, _ = ghcomp.Rotate(crv, rotate_angle, self.centroid)
        # pts, _, _ = ghcomp.ControlPoints(crv)
        rc = scriptcontext.doc.Objects.AddCurve(crv)
        return rc
        # return rs.AddCircle(self.centroid, self.config.r)
          