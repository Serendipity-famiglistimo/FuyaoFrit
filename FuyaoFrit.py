#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, August 4th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''

import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import System


import ghpythonlib.components as ghcomp
 
# SampleEtoRoomNumber dialog class
class FuyaoFrit:
    def __init__(self):
        self.inner_curve = None
        self.outer_curve = None
        self.refer_curve = None
    
    # 确定是否将outer curve flip
    def reorder_outer_curve(self):
        curve = self.outer_curve
        flip_curve, _ = ghcomp.FlipCurve(curve)
        close_curve, _ = ghcomp.Pufferfish.CloseCurve(curve)
        offset_curve = ghcomp.OffsetCurve(close_curve, distance=1.0, corners=1)
        offset_curve_area, _ = ghcomp.Area(offset_curve)
        print("close curve")
        curve_area, _ = ghcomp.Area(close_curve)
        print("calculate area: {0} {1}".format(offset_curve_area, curve_area))
        if curve_area < offset_curve_area:
            print("We flip the outer curve.")
            self.outer_curve = flip_curve
    
    def reorder_inner_curve(self):
        pass
     
    def init_curves(self):
        self.reorder_outer_curve()
        self.reorder_inner_curve()

    def run(self):
        self.init_curves()