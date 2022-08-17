#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Tuesday, August 16th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import Rhino as rc
class Dot:
    def __init__(self):
        self.centroid = rc.Geometry.Point3d(0, 0, 0)
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0
        self.display = None 
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)
    
    def get_top(self):
        return self.top
    
    def get_bottom(self):
        return self.bottom

    def draw(self):
        print("Dot: this function should not be executed!")
    
    
    