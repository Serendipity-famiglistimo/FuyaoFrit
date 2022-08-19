#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, August 18th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
from frits import FritType
from frits.CircleDot import CircleDot, CircleDotConfig
from frits.RoundRectDot import RoundRectConfig, RoundRectDot
import ghpythonlib.components as ghcomp
import utils

class RowRelationType:
    ALIGN=0
    CROSS=1
    @staticmethod
    def get_relations_strings():
        return ['对齐', '交错']

class RowFrits:
    def __init__(self, row_id, band_model):
        self.row_id = row_id
        self.dot_type = FritType.CIRCLE_DOT
        self.dot_config = CircleDotConfig()
        self.stepping = 0
        self.position = 0

        self.circle_config = CircleDotConfig()
        self.round_rect_config = RoundRectConfig()
        self.is_heading = True
        self.relations = [{'row_id': self.row_id - 1, 'type': RowRelationType.CROSS}]
        self.band_model = band_model
        if self.relations[0]['row_id'] >= 0:
            self.is_heading = not self.band_model.rows[self.relations[0]['row_id']].is_heading
        
        self.dots = []
        
    
    def get_first_relation(self):
        return self.relations[0]
    
    def fill_dots(self):
        if self.band_model and len(self.band_model.curves) > 0:
            
            # curve offset
            curve = self.band_model.curves[0]
            crv = ghcomp.OffsetCurve(curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
            crv_length = ghcomp.Length(crv)
    
            pts_num = int(crv_length / self.stepping)
            # offset curve
            pts = None
            t = None
            pts, _, t = ghcomp.DivideCurve(crv, pts_num, False)
            if not self.is_heading:
                new_t = []
                for i in range(len(t) - 1):
                    new_t.append((t[i] + t[i + 1]) / 2)
                t = new_t
            pts, vec, _ = ghcomp.EvaluateCurve(crv, t)
            
            self.dots = list()
            for i in range(len(pts)):
                theta = utils.tgt_angle(vec[i])
                dot = None
                if self.dot_type == FritType.CIRCLE_DOT:
                    dot = CircleDot(pts[i].X, pts[i].Y, self.circle_config.r)
                elif self.dot_type == FritType.ROUND_RECT:
                    dot = RoundRectDot(pts[i].X, pts[i].Y, self.round_rect_config.k, self.round_rect_config.r, theta)
                self.dots.append(dot)
                
                

        

