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
import clr
clr.AddReference("System.Xml")
import System.Xml

class RowArrangeType:
    HEADING=0
    CROSS=1
    @staticmethod
    def get_row_arrange_type():
        return ['顶头', '交错']

class RowFrits:
    def __init__(self, row_id):
        self.row_id = row_id
        self.dot_type = FritType.CIRCLE_DOT
        self.dot_config = CircleDotConfig()
        self.stepping = 0
        self.position = 0

        self.circle_config = CircleDotConfig()
        self.round_rect_config = RoundRectConfig()
        
        self.arrange_type = RowArrangeType.HEADING
        self.dots = []
        self.curve = None
        self.refer_curve = None
    
    def set_curve(self, refer_curve):
        self.refer_curve = refer_curve
        self.curve = ghcomp.OffsetCurve(refer_curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
    
    def fill_dots(self):
        if self.curve:
            # crv = ghcomp.OffsetCurve(curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
            crv = self.refer_curve
            crv_length = ghcomp.Length(crv)   
            pts_num = int(crv_length / self.stepping)
            # offset curve
            pts = None
            t = None
            pts, _, t = ghcomp.DivideCurve(crv, pts_num, False)
            if self.arrange_type == RowArrangeType.CROSS:
                new_t = []
                for i in range(len(t) - 1):
                    new_t.append((t[i] + t[i + 1]) / 2)
                t = new_t
            pts, vec, _ = ghcomp.EvaluateCurve(crv, t)
            pts, t, _ = ghcomp.CurveClosestPoint(pts, self.curve)
            self.dots = list()
            for i in range(len(pts)):
                theta = utils.tgt_angle(vec[i])
                dot = None
                if self.dot_type == FritType.CIRCLE_DOT:
                    dot = CircleDot(pts[i].X, pts[i].Y, self.circle_config.r)
                elif self.dot_type == FritType.ROUND_RECT:
                    dot = RoundRectDot(pts[i].X, pts[i].Y, self.round_rect_config, theta)
                self.dots.append(dot)

    @staticmethod
    def load_band_xml(file_path):
        xmldoc = System.Xml.XmlDocument()
        xmldoc.Load(file_path)
        items = xmldoc.SelectNodes("setting/band/row")
        rows = []
        for item in items:
            nid = item.GetAttributeNode('id').Value
            row = RowFrits(nid)
            dot_type = item.GetAttributeNode('type').Value
            row.dot_type = {'circle': FritType.CIRCLE_DOT, 'roundrect': FritType.ROUND_RECT}[dot_type]
            arrange_type = item.GetAttributeNode('arrange').Value
            row.arrange_type = {'heading': RowArrangeType.HEADING, 'cross': RowArrangeType.CROSS }[arrange_type]
            val = dict()

            for node in item.ChildNodes:
                val[node.Name] = float(node.InnerText)
            row.stepping = val['stepping']
            row.position = val['position']
            if row.dot_type == FritType.CIRCLE_DOT:
                row.circle_config.r = val['r']
            elif row.dot_type == FritType.ROUND_RECT:
                row.round_rect_config.k = val['k']
                row.round_rect_config.r = val['r']
            rows.append(row)
        return rows
