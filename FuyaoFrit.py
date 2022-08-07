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
Class FuyaoFrit:
    def __init__(self):
        self.inner_curve = None
        self.outer_curve = None
        self.refer_curve = None
    
    def handle_curves(self):
        curve1 = self.outer_curve
        curve2 = ghcomp.FlipCurve(curve1)
        oc = ghcomp.Pufferfish.CloseCurve(curve1)
        
        
    