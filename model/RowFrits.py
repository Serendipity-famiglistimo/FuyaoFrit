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
    def __init__(self, row_id, region):
        self.row_id = row_id
        self.dot_type = FritType.CIRCLE_DOT
        self.dot_config = CircleDotConfig()
        self.stepping = 0
        self.position = 0

        self.circle_config = CircleDotConfig()
        self.round_rect_config = RoundRectConfig()

        self.is_transit = False
        self.transit_radius = 0
        self.transit_position = 0
        
        self.arrange_type = RowArrangeType.HEADING
        self.dots = []
        self.region = region
     
    def fill_dots(self):
        del self.dots[:]
        print(self.row_id)
        if self.region.type == 'band' and self.region.curves[0]:
            if self.is_transit:
                self.fill_transit_band()
                print('fill transit band')
            else:
                self.fill_general_band()
                print('fill general band')
        elif self.region.type == 'block' and self.region.curves[0] and self.region.curves[1]:
            if self.row_id >= 0:
                if self.is_transit:
                    
                    self.fill_transit_band()
                    print('fill transit band')
                else:
                    self.fill_general_band()
                    print('fill general band')
            else:
                self.fill_bottom_band()

    def fill_general_band(self):
        refer_curve = self.region.curves[0] 
        if self.region.is_flip[0] == True:
            refer_curve, _ = ghcomp.FlipCurve(refer_curve)
        curve = ghcomp.OffsetCurve(refer_curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
        
        # crv = ghcomp.OffsetCurve(curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
        crv = refer_curve
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
        pts, t, _ = ghcomp.CurveClosestPoint(pts, curve)
        self.dots = list()
        for i in range(len(pts)):
            theta = utils.tgt_angle(vec[i])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(pts[i].X, pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(pts[i].X, pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)

    def fill_transit_band(self):
        refer_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            refer_curve, _ = ghcomp.FlipCurve(refer_curve)
        
        inner_curve = self.region.curves[1]
        if self.region.is_flip[1] == True:
            inner_curve, _ = ghcomp.FlipCurve(inner_curve)

        curve = ghcomp.OffsetCurve(refer_curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
        
        # crv = ghcomp.OffsetCurve(curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
        crv = refer_curve
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
        inner_pts, _, dis = ghcomp.CurveClosestPoint(pts, inner_curve)
        max_dis = max(dis)
        min_dis = min(dis)
        new_pts, t, _ = ghcomp.CurveClosestPoint(pts, curve)
        self.dots = list()
        for i in range(len(pts)):
            theta = utils.tgt_angle(vec[i])
            dot = None
            tp = dis[i]
            rp = max_dis
            if self.transit_position != 0:
                tp = (dis[i] - min_dis) / (max_dis - min_dis) * (self.position - self.transit_position) + self.transit_position
                # tr = 0
                # if self.dot_type == FritType.CIRCLE_DOT:
                #     tr = (dis[i] - min_dis) / (max_dis - min_dis) * (self.circle_config.r - self.transit_radius) + self.transit_radius
                # elif self.dot_type == FritType.ROUND_RECT:
                #     tr = (dis[i] - min_dis) / (max_dis - min_dis) * (self.round_rect_config.k - self.transit_radius) + self.transit_radius
                tp = tp
                rp = self.position
            else:
                tp = 1.0
                rp = 1.0
            x = (1 - tp / rp) * pts[i].X + (tp / rp) * new_pts[i].X
            y = (1 - tp / rp) * pts[i].Y + (tp / rp) * new_pts[i].Y
            if self.dot_type == FritType.CIRCLE_DOT:
                new_config = CircleDotConfig()
                new_config.r = (dis[i] - min_dis) / (max_dis - min_dis) * (self.circle_config.r - self.transit_radius) + self.transit_radius
                dot = CircleDot(x, y, new_config)
            elif self.dot_type == FritType.ROUND_RECT:
                k = (dis[i] - min_dis) / (max_dis - min_dis) * (self.round_rect_config.k - self.transit_radius) + self.transit_radius
                r = k / self.round_rect_config.k * self.round_rect_config.r # dis[i] / max_dis * self.round_rect_config.r
                new_config = RoundRectConfig()
                new_config.k = k
                new_config.r = r
                dot = RoundRectDot(x, y, new_config, theta)
            self.dots.append(dot)
    
    def fill_bottom_band(self):
        refer_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            refer_curve, _ = ghcomp.FlipCurve(refer_curve)
        curve = ghcomp.OffsetCurve(refer_curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
        
        # crv = ghcomp.OffsetCurve(curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
        crv = refer_curve
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
        pts, t, _ = ghcomp.CurveClosestPoint(pts, curve)
        self.dots = list()
        for i in range(len(pts)):
            theta = utils.tgt_angle(vec[i])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(pts[i].X, pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(pts[i].X, pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)

    def get_bottom_curve(self):
        refer_curve = None
        if self.row_id >= 0:
            refer_curve = self.region.curves[0]
            if self.region.is_flip[0] == True:
                refer_curve, _ = ghcomp.FlipCurve(refer_curve)
            
        else:
            refer_curve = self.region.curves[2]
            if self.region.is_flip[2] == True:
                refer_curve, _ = ghcomp.FlipCurve(refer_curve)
        dis = 0
        if self.dot_type == FritType.CIRCLE_DOT:
            dis = self.circle_config.bottom()
        elif self.dot_type == FritType.ROUND_RECT:
            dis = self.round_rect_config.bottom()
        curve = ghcomp.OffsetCurve(refer_curve, plane = ghcomp.XYPlane(), distance=self.position + dis, corners=1)
        return curve
        
    def get_top_curve(self):
        refer_curve = None
        if self.row_id >= 0:
            refer_curve = self.region.curves[0]
            if self.region.is_flip[0] == True:
                refer_curve, _ = ghcomp.FlipCurve(refer_curve)
            
        else:
            refer_curve = self.region.curves[2]
            if self.region.is_flip[2] == True:
                refer_curve, _ = ghcomp.FlipCurve(refer_curve)
        dis = 0
        if self.dot_type == FritType.CIRCLE_DOT:
            dis = self.circle_config.top()
        elif self.dot_type == FritType.ROUND_RECT:
            dis = self.round_rect_config.top()
        curve = ghcomp.OffsetCurve(refer_curve, plane = ghcomp.XYPlane(), distance=self.position - dis, corners=1)
        return curve

    @staticmethod
    def load_band_xml(file_path, region):
        xmldoc = System.Xml.XmlDocument()
        xmldoc.Load(file_path)
        items = xmldoc.SelectNodes("setting/band/row")
        rows = []
        for item in items:
            nid = int(item.GetAttributeNode('id').Value)
            row = RowFrits(nid, region)
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
            if 'transit' in val.keys():
                row.is_transit = True
                row.transit_radius = val['transit']
                if 'transitposition' in val.keys():
                    row.transit_position = val['transitposition']
            rows.append(row)
        return rows

    @staticmethod
    def load_block_xml(file_path, region):
        xmldoc = System.Xml.XmlDocument()
        xmldoc.Load(file_path)
        items = xmldoc.SelectNodes("setting/block/row")
        rows = []
        for item in items:
            nid = int(item.GetAttributeNode('id').Value)
            row = RowFrits(nid, region)
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
            if 'transit' in val.keys():
                row.is_transit = True
                row.transit_radius = val['transit']
                if 'transitposition' in val.keys():
                    row.transit_position = val['transitposition']
            rows.append(row)
        return rows