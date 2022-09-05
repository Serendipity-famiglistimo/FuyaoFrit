#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, August 22nd 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
from Zone import Zone
import math
from frits import FritType
from frits.CircleDot import CircleDot, CircleDotConfig
from frits.RoundRectDot import RoundRectConfig, RoundRectDot
import Rhino.Geometry as rg
import ghpythonlib.components as ghcomp

class BlockZone(Zone):
    def __init__(self):
        Zone.__init__(self)
        self.type = 'block'
        # 每一排都包括row id
        # row从下往上编号为0， 1， 2， 3， 4...
        # row 从上往下编号为-1, -2, -3...
        self.rows = list()
        self.holes = list()
        self.curves = [None, None, None]
        self.is_flip = [False, False, False]
        self.block_dots = []
        self.dots = []
    
    def get_top_row(self):
        for row in self.rows:
            if row.row_id < 0:
                return row
    
    def fill_dots(self):
        # 填充最顶部的一行
       
        row_num = len(self.rows)
        top_curve = None
        bottom_curve = self.curves[0]
        first_bottom_row_dots = None
        first_bottom_row = None
        for i in range(row_num):
            if self.rows[i].row_id < 0:
                self.rows[i].fill_dots()
                self.block_dots.append(self.rows[i].dots)
                if self.rows[i].row_id == -1:
                    first_bottom_row_dots = self.rows[i].dots
                    first_bottom_row = self.rows[i]
        bottom_curve = self.curves[0]
        top_curve = self.rows[-1].get_bottom_curve()
        current_row_id = self.rows[-1].row_id
        current_vspace = self.rows[-1].position - first_bottom_row.position
        self.border_curve = self.construct_border(top_curve, bottom_curve)
        bbox = self.border_curve.GetBoundingBox(True)
        
        leftup = bbox.Min
        bottomright = bbox.Max

        stepping = self.holes[0].stepping
        vspace = self.holes[0].vspace
        arrange_type = self.holes[0].arrange_type
        
        yStart = leftup.Y
        yEnd = bottomright.Y
        yLength = yEnd - yStart 
        yCount = abs(int(math.ceil(yLength / vspace)))
        for i in range(yCount):
            current_row_id -= 1
            dots = list()
            if current_row_id % 2 == 0:
                dots = first_bottom_row.shift_y_mid_dots(-current_vspace - vspace * (i+1))
            else:
                dots = first_bottom_row.shift_y_dots(-current_vspace - (i + 1) * vspace)
            # use hole config for these dots
            # modify after
            new_row = []
            for dot in dots:
                # is in curve
                is_in_curve = self.border_curve.Contains(dot.centroid)
                if is_in_curve == rg.PointContainment.Inside:
                    new_dot = None
                    if self.holes[0].dot_type == FritType.CIRCLE_DOT:
                        new_dot = CircleDot(dot.centroid.X, dot.centroid.Y, self.holes[0].circle_config)
                    elif self.dot_type == FritType.ROUND_RECT:
                        new_dot = RoundRectDot(dot.centroid.X, dot.centroid.Y, self.holes[0].round_rect_config, dot.theta)
                    new_row.append(new_dot)
            self.block_dots.append(new_row)

        for row in self.block_dots:
            self.dots += row
    
    def trim_curve(self, crv, t1, t2):
        _, crv_domain = ghcomp.CurveDomain(crv)
        tstart, tend = ghcomp.DeconstructDomain(crv_domain)
        mid = (tstart + tend) / 2
        if t1 > mid:
            t1 = tstart
        if t2 < mid:
            t2 = tend
        domain = ghcomp.ConstructDomain(t1, t2)
        subcrv = ghcomp.SubCurve(crv, domain)
        
        return subcrv
        
    def construct_border(self, top_border, bottom_border):
        _, tA, tB = ghcomp.CurveXCurve(top_border, bottom_border)
        top_subcrv = top_border
        bottom_subcrv = bottom_border
        
        if tA:
            try:
                top_subcrv = self.trim_curve(top_border, tA[0], tA[-1])
            except:
                top_subcrv = self.trim_curve(top_border, tA, tA)
        if tB:
            try:
                bottom_subcrv = self.trim_curve(bottom_border, tB[0], tB[-1])
            except:
                bottom_subcrv = self.trim_curve(bottom_border, tB, tB)
        
        #self.display.AddCurve(top_subcrv)
        #self.display.AddCurve(bottom_subcrv)
        
        blocksrf = ghcomp.RuledSurface(top_subcrv, bottom_subcrv)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        #self.display.AddCurve(blockborder)
        
        return blockborder
    
  