#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, August 24th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
from frits import FritType
from frits.CircleDot import CircleDot, CircleDotConfig
from frits.RoundRectDot import RoundRectConfig, RoundRectDot
import ghpythonlib.components as ghcomp
import utils
import math
import Rhino.Geometry as rg
import Rhino as rc
import Grasshopper as gh
import scriptcontext
import rhinoscriptsyntax as rs
import clr
import copy
from model.ChooseZone import con
clr.AddReference("System.Xml")
import System.Xml

class HoleArrangeType:
    HEADING=0
    CROSS=1
    @staticmethod
    def get_hole_arrange_type():
        return ['顶头', '交错']

class HoleFrits:
    def __init__(self, hole_id, region):
        self.hole_id = hole_id
        self.dot_type = FritType.CIRCLE_DOT
        self.dot_config = CircleDotConfig()
        self.stepping = 0
        self.vspace = 0
        self.first_line_position = 0

        self.circle_config = CircleDotConfig()
        self.round_rect_config = RoundRectConfig()
        
        self.arrange_type = HoleArrangeType.CROSS
        self.dots = []
        self.region = region
        self.top_curve = None
        self.bottom_curve = None
        self.border_curve = None
    
    def bake(self):
        pass
    
    def fill_dots_88LFW(self):
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        
        first_line_curve = ghcomp.OffsetCurve(self.top_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        crv_length = ghcomp.Length(first_line_curve)   
        pts_num = int(crv_length / self.stepping)
        line_pts, _, t = ghcomp.DivideCurve(first_line_curve, pts_num, False)
        new_t = []
        for i in range(len(t) - 1):
            new_t.append((t[i] + t[i + 1]) / 2)
        
        cross_pts, vec, _ = ghcomp.EvaluateCurve(first_line_curve, new_t)
        
        _, _, blockborder = self.construct_border(self.top_curve, self.bottom_curve)
        # 估计排数
        bbox = blockborder.GetBoundingBox(True)
        
        leftup = bbox.Min
        bottomright = bbox.Max
      
        yStart = leftup.Y
        yEnd = bottomright.Y
        
       
        yLength = yEnd - yStart 
        
        # 随便估算一下
        yCount = int(math.ceil(yLength / self.vspace) / 2 + 2)
        bottom_pts = []
        all_dots = []
        dots_list = []
        for i in range(yCount):
            l2 = ghcomp.Addition(rg.Vector3d(0, -self.vspace * 2 * i, 0), cross_pts)
            l3 = ghcomp.Addition(rg.Vector3d(0, -self.vspace * (2* i + 1), 0), line_pts)
            new_l2 = []
            new_l3 = []
            for pt in l2:
                PtCtmt = blockborder.Contains(pt)
                if PtCtmt == rg.PointContainment.Inside:
                    new_l2.append(pt)
            
            for pt in l3:
                PtCtmt = blockborder.Contains(pt)
                if PtCtmt == rg.PointContainment.Inside:
                    new_l3.append(pt)
            if len(new_l2):
                dots_list.append(new_l2)
            if len(new_l3):
                dots_list.append(new_l3)
        big_dots = []
        start_pt, end_pt = ghcomp.EndPoints(self.top_curve)
        #首先判断斜率得方向
        sx, sy, sz = ghcomp.Deconstruct(start_pt)
        ex, ey, ez = ghcomp.Deconstruct(end_pt)
        left_or_right = 1 # 左边
        if (ey - sy) * (ex - sx) > 0:
            left_or_right = -1 # 右边
        if left_or_right == 1:
            for i in range(len(dots_list)):
                for j in range(len(dots_list[i])):
                    if i == len(dots_list) - 1:
                        bottom_pts.append(dots_list[i][j])
                    else:
                        dot = dots_list[i][j]
                        dot1 = dots_list[i+1][0]
                        dx, _, _ = ghcomp.Deconstruct(dot)
                        dx1, _, _ = ghcomp.Deconstruct(dot1)
                        if dx < dx1:
                            bottom_pts.append(dot)
                        else:
                            break
        else:
            for i in range(len(dots_list)):
            
                for j in range(len(dots_list[i])):
                    if i == len(dots_list) - 1:
                        bottom_pts.append(dots_list[i][j])
                    else:
                        dot = dots_list[i][len(dots_list[i]) - 1- j]
                        dot1 = dots_list[i+1][len(dots_list[i + 1]) - 1]
                        dx, _, _ = ghcomp.Deconstruct(dot)
                        dx1, _, _ = ghcomp.Deconstruct(dot1)
                        if dx > dx1:
                            bottom_pts.append(dot)
                        else:
                            break
        for i in range(0, len(dots_list) - 1):
            big_dots += dots_list[i]
        big_dots += dots_list[-1]
        # draw big dots
        for i in range(len(big_dots)):
            theta = 0 # utils.tgt_angle(vec[i])
            c = CircleDotConfig()
            c.r = 1
            dot = CircleDot(big_dots[i].X, big_dots[i].Y, c, theta)
            self.dots.append(dot)

        
        small_curve = self.region.curves[1]
        if self.region.is_flip[1] == True:
            small_curve, _ = ghcomp.FlipCurve(small_curve)
         # 从顶部发射射线与下部相交
        default_length = 500
        dirc = rg.Vector3d(-left_or_right * self.stepping / 2, -self.vspace, 0)
        diag_lines = ghcomp.LineSDL(bottom_pts, dirc, default_length)

        # 射线与底线相交
        offset_dis = -0.5
        bcurve = ghcomp.OffsetCurve(small_curve, plane = rs.WorldXYPlane(), distance=offset_dis, corners=1)
        line = []
        fill_pts = []
        for i in range(len(diag_lines)):
            small_pts, _, _ = ghcomp.CurveXCurve(diag_lines[i], bcurve)
            if small_pts:
                line.append(ghcomp.Line(bottom_pts[i], small_pts))
            
        
        # line = ghcomp.Line(top_pts, bottom_pts)
        unit_length = math.sqrt(0.25 * self.stepping * self.stepping + self.vspace * self.vspace)
        for l in line:
            crv_length = ghcomp.Length(l)   
            pts_num = int(crv_length / unit_length)
            # offset curve
            line_pts, _, t = ghcomp.DivideCurve(l, pts_num, False)
            line_pts.reverse()
            if line_pts:
                # line_pts = line_pts[1:]
                if line_pts:
                    for i in range(len(line_pts) - 1): 
                        c = CircleDotConfig()
                        c.r = 0.5 + 0.1 * i
                        dot = CircleDot(line_pts[i].X, line_pts[i].Y, c, 0)
                        self.dots.append(dot)
        

    # 76720LFW00027
    def fill_dots_76720LFW00027(self):
        # top_curve
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        
        box = ghcomp.BoundingBox(self.top_curve, rs.WorldXYPlane())
        box_centroid, _, _, _, _ = ghcomp.BoxProperties(box)
        cx, cy, cz = ghcomp.Deconstruct(box_centroid[0])
        # 向下平移半径长度
        # 这里先假设是圆形
        curve = ghcomp.OffsetCurve(self.top_curve, plane = rs.WorldXYPlane(), distance=0.36, corners=1)
        # 先画一条水平线
        start_pt, end_pt = ghcomp.EndPoints(curve)
        #首先判断斜率得方向
        sx, sy, sz = ghcomp.Deconstruct(start_pt)
        ex, ey, ez = ghcomp.Deconstruct(end_pt)
        left_or_right = 1 # 左边
        if (ey - sy) * (ex - sx) > 0:
            left_or_right = -1 # 右边
        sx0 = sx - left_or_right * (sy - cy) / self.vspace / 2  * self.stepping
        ex0 = ex - left_or_right * (ey - cy) / self.vspace / 2 * self.stepping
        pts_num = int(abs(ex0 - sx0) / self.stepping)
        xs = []
        default_xd = 500
        top_pts = []
        for i in range(pts_num + 1):
            mx = sx0 + i * (ex0 - sx0) / pts_num
            lx = mx - default_xd
            ly = cy - left_or_right * default_xd * self.vspace * 2 / self.stepping
            rx = mx + default_xd
            ry = cy + left_or_right * default_xd * self.vspace * 2 /self.stepping
            line = ghcomp.Line(rg.Point3d(lx, ly, 0), rg.Point3d(rx, ry, 0))
            jpt, _, _ = ghcomp.CurveXCurve(line, curve)
            top_pts.append(jpt)
        # offset curve
        
        # 从顶部发射射线与下部相交
        default_length = 500
        dirc = rg.Vector3d(-left_or_right * self.stepping / 2, -self.vspace, 0)
        diag_lines = ghcomp.LineSDL(top_pts, dirc, default_length)

        # 射线与底线相交
        offset_dis = -0.5
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        bcurve = ghcomp.OffsetCurve(self.bottom_curve, plane = rs.WorldXYPlane(), distance=offset_dis, corners=1)
        line = []
        fill_pts = []
        for i in range(len(diag_lines)):
            bottom_pts, _, _ = ghcomp.CurveXCurve(diag_lines[i], bcurve)
            if bottom_pts:
                line.append(ghcomp.Line(top_pts[i], bottom_pts))
            
        
        # line = ghcomp.Line(top_pts, bottom_pts)
        unit_length = math.sqrt(0.25 * self.stepping * self.stepping + self.vspace * self.vspace)

        
        for l in line:
            crv_length = ghcomp.Length(l)   
            pts_num = int(crv_length / unit_length)
            # offset curve
            line_pts, _, t = ghcomp.DivideCurve(l, pts_num, False)
            if line_pts:
                fill_pts += line_pts[1:]
            

        for i in range(len(top_pts)):
            theta = ghcomp.Pi() * 0.25 # utils.tgt_angle(vec[i])
            c = RoundRectConfig()
            c.k = 0.6
            c.r = 0.15
            dot = RoundRectDot(top_pts[i].X, top_pts[i].Y, c, theta)
            self.dots.append(dot)

        for i in range(len(fill_pts)):
            theta = ghcomp.Pi() * 0.25 # utils.tgt_angle(vec[i])
            dot = RoundRectDot(fill_pts[i].X, fill_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)

    def fill_from_bottom(self):
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        
        start_pt, end_pt = ghcomp.EndPoints(self.top_curve)
        #首先判断斜率得方向
        sx, sy, sz = ghcomp.Deconstruct(start_pt)
        ex, ey, ez = ghcomp.Deconstruct(end_pt)
        left_or_right = 1 # 左边
        if (ey - sy) * (ex - sx) > 0:
            left_or_right = -1 # 右边
        first_line_curve = self.region.curves[1]
        if self.region.is_flip[1] == True:
            first_line_curve, _ = ghcomp.FlipCurve(self.region.curves[1])
        first_line_curve = ghcomp.OffsetCurve(first_line_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        crv_length = ghcomp.Length(first_line_curve)   
        pts_num = int(crv_length / self.stepping)
        line_pts, v1, t = ghcomp.DivideCurve(first_line_curve, pts_num, False)
         # cross
        new_t = []
        for i in range(len(t) - 1):
            new_t.append((t[i] + t[i + 1]) / 2)
        
        cross_pts, v1, _ = ghcomp.EvaluateCurve(first_line_curve, new_t)
        # 旋转90度做垂线，分别往两个方向分别取100个点
        v2 = rg.Vector3d(left_or_right * self.stepping / 2, self.vspace, 0)
        all_dots = list(cross_pts)
        for i in range(1, 300):
            l2 = ghcomp.Addition(ghcomp.Multiplication(v2, i), cross_pts) 
            all_dots += l2
        # 边界
        # bcurve = ghcomp.OffsetCurve(self.bottom_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        tcurve = self.top_curve
        bcurve = self.bottom_curve
        _, _, blockborder = self.construct_border(tcurve, bcurve)
        # blockborder = ghcomp.OffsetCurve(blockborder, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        filter_pts = []
        for pt in all_dots:
            PtCtmt = blockborder.Contains(pt)
            if PtCtmt == rg.PointContainment.Inside:
                filter_pts.append(pt)
        
        for i in range(len(filter_pts)):
            theta = 0
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(filter_pts[i].X, filter_pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(filter_pts[i].X, filter_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)

    # 针对00215 设计填充算法

    def fill_angle(self):
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        first_line_curve = self.region.curves[1]
        if self.region.is_flip[1] == True:
            first_line_curve, _ = ghcomp.FlipCurve(self.region.curves[1])
        first_line_curve = ghcomp.OffsetCurve(first_line_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        second_curve = ghcomp.OffsetCurve(self.bottom_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        # second_curve = ghcomp.RebuildCurve(second_curve, 3, 300, True) 
         # 先画一条水平线
        start_pt, end_pt = ghcomp.EndPoints(self.top_curve)
        #首先判断斜率得方向
        sx, sy, sz = ghcomp.Deconstruct(start_pt)
        ex, ey, ez = ghcomp.Deconstruct(end_pt)
        left_or_right = 1 # 左边
        if (ey - sy) * (ex - sx) > 0:
            left_or_right = -1 # 右边
        crv_length = ghcomp.Length(first_line_curve)   
        pts_num = int(crv_length / self.stepping)
        line_pts, v1, t = ghcomp.DivideCurve(first_line_curve, pts_num, False)
        # cross
        new_t = []
        for i in range(len(t) - 1):
            new_t.append((t[i] + t[i + 1]) / 2)
        
        cross_pts, v1, _ = ghcomp.EvaluateCurve(first_line_curve, new_t)
        # 旋转90度做垂线，分别往两个方向分别取100个点
        new_v = list()
        for i in range(len(v1)):
            new_v.append(v1[1])
        # fuck Fuck fuck!!! 离谱！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！必须写小数
        v2, _ = ghcomp.Rotate(new_v, ghcomp.Pi()*(-0.3333) * left_or_right, rg.Point3d(0, 0, 0))
        # ghcomp.Rotate(
        print(v2[0])
        
        top_pts = []
        
        for i in range(len(cross_pts)):     
            line = ghcomp.LineSDL(cross_pts[i], -v2[i], 500)
            # cl = rg.NurbsCurve.CreateFromLine(line)
            # events = rg.Intersect.Intersection.CurveCurve(second_curve, cl, 0.001, 0.0)
            # jpt = rs.CurveCurveIntersection(line,second_curve)
            jpt, _, _ = ghcomp.CurveXCurve(line, second_curve)
            if jpt:
                top_pts.append(jpt)
            line = ghcomp.LineSDL(cross_pts[i], v2[i], 500)
            jpt, _, _ = ghcomp.CurveXCurve(line, second_curve)
            if jpt:
                top_pts.append(jpt)
        # offset curve
        
        # 从顶部发射射线与下部相交
        default_length = 500
        
        diag_lines = ghcomp.LineSDL(top_pts, -v2[0] * left_or_right, default_length)

        # 射线与底线相交
        # offset_dis = self.first_line_position # self.region.rows[-1].position - self.vspace - 0.1
        
        bcurve = ghcomp.OffsetCurve(self.top_curve, plane = rs.WorldXYPlane(), distance=0, corners=1)
        line = []
        fill_pts = []
        for i in range(len(diag_lines)):
            bottom_pts, _, _ = ghcomp.CurveXCurve(diag_lines[i], bcurve)
            if bottom_pts:
                line.append(ghcomp.Line(top_pts[i], bottom_pts))
            else:
                fill_pts.append(top_pts[i])
        
        # line = ghcomp.Line(top_pts, bottom_pts)
        unit_length = math.sqrt(0.25 * self.stepping * self.stepping + self.vspace * self.vspace)

        
        for l in line:
            crv_length = ghcomp.Length(l)   
            pts_num = int(crv_length / unit_length)
            # offset curve
            line_pts, _, t = ghcomp.DivideCurve(l, pts_num, False)
            if line_pts:
                fill_pts += line_pts
            else:
                sp, ep = ghcomp.EndPoints(l)
                fill_pts.append(sp)

        # 边界
        blocksrf = ghcomp.RuledSurface(self.top_curve, self.bottom_curve)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        blockborder = ghcomp.OffsetCurve(blockborder, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        filter_pts = []
        for pt in fill_pts:
            PtCtmt = blockborder.Contains(pt)
            if PtCtmt == rg.PointContainment.Inside:
                filter_pts.append(pt)
        
        for i in range(len(filter_pts)):
            theta = utils.tgt_angle(v1[0])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(filter_pts[i].X, filter_pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(filter_pts[i].X, filter_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)


    # 针对00841LFW00001 设计填充算法
    def fill_simple(self):
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        
        first_line_curve = ghcomp.OffsetCurve(self.top_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        crv_length = ghcomp.Length(first_line_curve)   
        pts_num = int(crv_length / self.stepping)
        line_pts, _, t = ghcomp.DivideCurve(first_line_curve, pts_num, False)
        new_t = []
        for i in range(len(t) - 1):
            new_t.append((t[i] + t[i + 1]) / 2)
        
        cross_pts, vec, _ = ghcomp.EvaluateCurve(first_line_curve, new_t)
        
        blocksrf = ghcomp.RuledSurface(self.top_curve, self.bottom_curve)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        # 估计排数
        bbox = blockborder.GetBoundingBox(True)
        
        leftup = bbox.Min
        bottomright = bbox.Max
      
        yStart = leftup.Y
        yEnd = bottomright.Y
        
       
        yLength = yEnd - yStart 
        
        # 随便估算一下
        yCount = int(math.ceil(yLength / self.vspace) / 2 + 2)
        all_dots = []
        for i in range(yCount):
            l2 = ghcomp.Addition(rg.Vector3d(0, -self.vspace * 2 * i, 0), line_pts)
            l3 = ghcomp.Addition(rg.Vector3d(0, -self.vspace * (2* i + 1), 0), cross_pts)
            all_dots += l2
            all_dots += l3
        if self.dot_type == FritType.CIRCLE_DOT:
            blockborder = ghcomp.OffsetCurve(blockborder, plane = rs.WorldXYPlane(), distance=-self.circle_config.r, corners=1)
        elif self.dot_type == FritType.ROUND_RECT:
             blockborder = ghcomp.OffsetCurve(blockborder, plane = rs.WorldXYPlane(), distance=-self.round_rect_config.k / 2, corners=1)
        filter_pts = []
        for pt in all_dots:
            PtCtmt = blockborder.Contains(pt)
            if PtCtmt == rg.PointContainment.Inside:
                filter_pts.append(pt)
        
        for i in range(len(filter_pts)):
            theta = 0
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(filter_pts[i].X, filter_pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(filter_pts[i].X, filter_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)

    # 针对00399LFW00012 设计填充算法
    # curve[0] 是黑白分界线
    # curve[1] 是分界线上的直线延长线，通过确保len(curve[1])= len(curve[0])保证了上下点对齐
    # curve[2] 是上分界线
    def fill_one_line(self):
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        first_line_curve = self.region.curves[1]
        if self.region.is_flip[1] == True:
            first_line_curve, _ = ghcomp.FlipCurve(self.region.curves[1])
        first_line_curve = ghcomp.OffsetCurve(first_line_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        crv_length = ghcomp.Length(first_line_curve)   
        pts_num = int(crv_length / self.stepping)
        line_pts, v1, t = ghcomp.DivideCurve(first_line_curve, pts_num, False)
        
        # 旋转90度做垂线，分别往两个方向分别取100个点
        v2, _ = ghcomp.Rotate(v1, ghcomp.Pi(0.5), rg.Point3d(0, 0, 0))
        all_dots = list(line_pts)
        for i in range(1, 100):
            l2 = ghcomp.Addition(ghcomp.Multiplication(v2, i* self.vspace), line_pts) 
            all_dots += l2 
            l3 = ghcomp.Addition(ghcomp.Multiplication(v2, -i* self.vspace), line_pts)
            all_dots += l3
        
        # 边界
        blocksrf = ghcomp.RuledSurface(self.top_curve, self.bottom_curve)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        blockborder = ghcomp.OffsetCurve(blockborder, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        filter_pts = []
        for pt in all_dots:
            PtCtmt = blockborder.Contains(pt)
            if PtCtmt == rg.PointContainment.Inside:
                filter_pts.append(pt)
        
        for i in range(len(filter_pts)):
            theta = utils.tgt_angle(v1[0])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(filter_pts[i].X, filter_pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(filter_pts[i].X, filter_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)


    # 针对00792LFW000023 设计填充算法
    def fill_dots_diag_and_sticky(self):
        # top_curve
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        box = ghcomp.BoundingBox(self.top_curve, rs.WorldXYPlane())
        box_centroid, _, _, _, _ = ghcomp.BoxProperties(box)
        cx, cy, cz = ghcomp.Deconstruct(box_centroid[0])
        # 向下平移半径长度
        # 这里先假设是圆形
        curve = ghcomp.OffsetCurve(self.top_curve, plane = rs.WorldXYPlane(), distance=self.circle_config.r, corners=1)
        # 先画一条水平线
        start_pt, end_pt = ghcomp.EndPoints(curve)
        #首先判断斜率得方向
        sx, sy, sz = ghcomp.Deconstruct(start_pt)
        ex, ey, ez = ghcomp.Deconstruct(end_pt)
        left_or_right = 1 # 左边
        if (ey - sy) * (ex - sx) > 0:
            left_or_right = -1 # 右边
        sx0 = sx - left_or_right * (sy - cy) / self.vspace / 2  * self.stepping
        ex0 = ex - left_or_right * (ey - cy) / self.vspace / 2 * self.stepping
        pts_num = int(abs(ex0 - sx0) / self.stepping)
        xs = []
        default_xd = 500
        top_pts = []
        for i in range(pts_num + 1):
            mx = sx0 + i * (ex0 - sx0) / pts_num
            lx = mx - default_xd
            ly = cy - left_or_right * default_xd * self.vspace * 2 / self.stepping
            rx = mx + default_xd
            ry = cy + left_or_right * default_xd * self.vspace * 2 /self.stepping
            line = ghcomp.Line(rg.Point3d(lx, ly, 0), rg.Point3d(rx, ry, 0))
            jpt, _, _ = ghcomp.CurveXCurve(line, curve)
            top_pts.append(jpt)
        # offset curve
        
        # 从顶部发射射线与下部相交
        default_length = 500
        dirc = rg.Vector3d(-left_or_right * self.stepping / 2, -self.vspace, 0)
        diag_lines = ghcomp.LineSDL(top_pts, dirc, default_length)

        # 射线与底线相交
        offset_dis = self.region.rows[-1].position - self.vspace - 0.2
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        bcurve = ghcomp.OffsetCurve(self.bottom_curve, plane = rs.WorldXYPlane(), distance=offset_dis, corners=1)
        line = []
        fill_pts = []
        for i in range(len(diag_lines)):
            bottom_pts, _, _ = ghcomp.CurveXCurve(diag_lines[i], bcurve)
            if bottom_pts:
                line.append(ghcomp.Line(top_pts[i], bottom_pts))
            else:
                fill_pts.append(top_pts[i])
        
        # line = ghcomp.Line(top_pts, bottom_pts)
        unit_length = math.sqrt(0.25 * self.stepping * self.stepping + self.vspace * self.vspace)

        
        for l in line:
            crv_length = ghcomp.Length(l)   
            pts_num = int(crv_length / unit_length)
            # offset curve
            line_pts, _, t = ghcomp.DivideCurve(l, pts_num, False)
            if line_pts:
                fill_pts += line_pts
            else:
                sp, ep = ghcomp.EndPoints(l)
                fill_pts.append(sp)
                
        for i in range(len(fill_pts)):
            theta = 0 # utils.tgt_angle(vec[i])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(fill_pts[i].X, fill_pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(fill_pts[i].X, fill_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)

    def fill_dots(self):
        print(con.type+'算法')
        if con.type == '大众图纸':
            pass
        elif con.type == '88LF':
            self.fill_dots_88LFW()
        elif con.type == '76720LFW00027':
            self.fill_dots_76720LFW00027()
        elif con.type == '00215':
            self.fill_angle()
        elif con.type == '00841LFW00001':
            self.fill_simple()
        elif con.type == '00399LFW00012':
            self.fill_one_line()
        elif con.type == '00792LFW000023':
            self.fill_dots_diag_and_sticky()
        
        # self.fill_from_bottom()
        # self.fill_simple()
        # self.fill_dots_88LFW()
        # self.fill_dots_76720LFW00027()
        # self.fill_one_line()
        # self.fill_dots_diag_and_sticky()

    def general_fill_dots(self):
        #outer_anchor = []
        print(self.hole_id)
        row_num = len(self.region.rows)
        top_curve = None
        bottom_curve = None
        top_anchor = []
        bottom_anchor = []
        for i in range(row_num):
            if self.region.rows[i].row_id < 0:
                bottom_curve = self.region.rows[i - 1].get_top_curve()
                bottom_dots = self.region.rows[i - 1].dots
                for j in range(len(bottom_dots)):
                    bottom_anchor.append(bottom_dots[j].centroid)
                #outer_anchor += bottom_anchor
                #print(len(bottom_anchor))
                break
        
        top_curve = self.region.rows[-1].get_bottom_curve()
        top_dots = self.region.rows[-1].dots
        for j in range(len(top_dots)):
            top_anchor.append(top_dots[j].centroid)
            
        #top_anchor = ghcomp.ReverseList(top_anchor)
        #outer_anchor += top_anchor
        
        #print("*****get anchor*****")
        #print(len(top_anchor))
        #print(len(outer_anchor))
        #stepping = self.region.rows[-1].stepping
        
        _, _, self.border_curve = self.construct_border(top_curve, bottom_curve)
        
        self.block_fill(self.border_curve, top_anchor, bottom_anchor, self.stepping, self.vspace, self.arrange_type)

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
        
        return top_subcrv, bottom_subcrv, blockborder

    def block_fill(self, Crv, top_outer_anchor, bottom_outer_anchor, horizontal, vertical, aligned):
        # self.display.AddCurve(blockborder)
        Pt = []

        threshold = min(horizontal, vertical)
        
        
        bbox = Crv.GetBoundingBox(True)
        
        leftup = bbox.Min
        bottomright = bbox.Max
        
        xStart = leftup.X
        xEnd = bottomright.X
        yStart = leftup.Y
        yEnd = bottomright.Y
        
        xLength = xEnd - xStart
        yLength = yEnd - yStart 
        
        xCount = int(math.ceil(xLength / horizontal))
        yCount = int(math.ceil(yLength / vertical))
        print(xCount, yCount)
        
        for i in range(xCount + 1):
            for j in range(yCount + 1):
                if aligned == HoleArrangeType.HEADING:
                    pt = rg.Point3d(xStart + i*horizontal, yStart + j*vertical, 0)
                else:
                    if j%2 == 0:
                        pt = rg.Point3d(xStart + i*horizontal, yStart + j*vertical, 0)
                    else:
                        pt = rg.Point3d(xStart + (i+0.5)*horizontal, yStart + j*vertical, 0)
                
                PtCtmt = Crv.Contains(pt)
                if PtCtmt == rg.PointContainment.Inside:
                    Pt.append(pt)
        
        #iterate force conduct algo
        pts = self.force_conduct(Pt, Crv, top_outer_anchor, bottom_outer_anchor, horizontal, vertical, aligned)
        #pts = Pt

        for i in range(len(pts)):
            theta = 0 # utils.tgt_angle(vec[i])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(pts[i].X, pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(pts[i].X, pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)
    
    def force_conduct(self, inner_pts, outer_border, top_outer_anchor, bottom_outer_anchor, horizontal, vertical, aligned):
        #To do: send aligned parameters in !!!
        
        aligned = False
        
        outer_anchor = ghcomp.Merge(top_outer_anchor, bottom_outer_anchor)
        hspace = (horizontal+vertical)/2
        
        #outer_anchor_num = int(ghcomp.Length(outer_border)/hspace)
        #outer_anchor, _, _ = ghcomp.DivideCurve(outer_border, outer_anchor_num, False)
        
        offset = horizontal
        if aligned == True:
            offset = math.sqrt(horizontal*horizontal + vertical*vertical)
        
        else:
            offset = math.sqrt(0.25*horizontal*horizontal + vertical*vertical)
            vertical = 2 * vertical
        
        
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
        self.display.AddCurve(outer_border, self.display_color, 1)
        #scriptcontext.doc.Views.Redraw()
        
        inner_aux_border = ghcomp.OffsetCurve(outer_border, 5*offset, plane=ghcomp.XYPlane(), corners = 1)
        verbose_aux_border = ghcomp.OffsetCurve(outer_border, 6*offset, plane=ghcomp.XYPlane(), corners = 1)
        
        aux_num = int(3 * ghcomp.Length(inner_aux_border) / hspace)
        aux_pts, _, _ = ghcomp.DivideCurve(inner_aux_border, aux_num, False)
        verbose_pts, _, _ = ghcomp.ClosestPoint(aux_pts, inner_pts)
        verbose_pts, _ = ghcomp.DeleteConsecutive(verbose_pts, True)
        print("****check original verbose****")
        print(len(verbose_pts))
        
        flag = True
        inner_anchor = []
        while flag == True:
            temp = copy.deepcopy(verbose_pts)
            inner_anchor1, inner_anchor2, flag = utils.remove_verbose(temp)
            #print("****check verbose****")
            #print(len(verbose_pts))
            #print(len(inner_anchor1))
            #print(len(inner_anchor2))
            inner_anchor = inner_anchor1
            verbose_pts = inner_anchor1
            if len(inner_anchor2) > len(inner_anchor1):
                inner_anchor = inner_anchor2
                verbose_pts = inner_anchor2
        
        """
        odd_even = ghcomp.Merge(True, False)
        odd_pts, even_pts = ghcomp.Dispatch(inner_anchor, odd_even)
        odd_pts, _ = ghcomp.DeleteConsecutive(odd_pts, False)
        even_pts, _ = ghcomp.DeleteConsecutive(even_pts, False)
        inner_anchor = ghcomp.Merge(odd_pts, even_pts)
        """
        
        inner_border = ghcomp.PolyLine(inner_anchor, True)
        self.display.AddCurve(inner_border, self.display_color, 1)
        scriptcontext.doc.Views.Redraw()
        
        relationship, _ = ghcomp.PointInCurve(inner_pts, inner_border)
        outside_pattern, _ = ghcomp.Equality(relationship, 0)
        iter_pts, _ = ghcomp.Dispatch(inner_pts, outside_pattern)
        inside_pattern, _ = ghcomp.Equality(relationship, 2)
        fix_pts, _ = ghcomp.Dispatch(inner_pts, inside_pattern)
        
        verbose_iter_pts = copy.deepcopy(iter_pts)
        relationship, _ = ghcomp.PointInCurve(iter_pts, verbose_aux_border)
        aux_pattern, _ = ghcomp.Equality(relationship, 2)
        bug_pts, iter_pts = ghcomp.Dispatch(iter_pts, aux_pattern)
        if bug_pts:
            if len(iter_pts) == len(verbose_iter_pts) - 1:
                fix_pts.append(ghcomp.ConstructPoint(bug_pts[0],bug_pts[1],bug_pts[2]))
            else:
                fix_pts += bug_pts
        
        anchor_pts = ghcomp.Merge(outer_anchor, inner_anchor)
        all_pts = ghcomp.Merge(anchor_pts, iter_pts)
        
        top_crv = ghcomp.PolyLine(top_outer_anchor, False)
        bottom_crv = ghcomp.PolyLine(bottom_outer_anchor, False)
        
        _, _, outer_anchor_border = self.construct_border(top_crv, bottom_crv)
        
        outer_mesh, inner_mesh, ring_mesh = self.construct_ring_mesh(outer_anchor_border, inner_border, all_pts)
        _, mesh_edges, _ = ghcomp.MeshEdges(ring_mesh)
        
        edge_midpt = ghcomp.CurveMiddle(mesh_edges)
        edge_pattern, _ = ghcomp.PointInCurve(edge_midpt, outer_anchor_border)
        raw_line, _ = ghcomp.Dispatch(mesh_edges, edge_pattern)
        start_pt, end_pt = ghcomp.EndPoints(raw_line)
        oncrv1, _ = ghcomp.PointInCurve(start_pt, outer_anchor_border)
        oncrv2, _ = ghcomp.PointInCurve(end_pt, outer_anchor_border)
        oncrv_pattern, _ = ghcomp.Equality(oncrv1, oncrv2)
        inner_line, border_line = ghcomp.Dispatch(mesh_edges, oncrv_pattern)
        
        #for i in range(len(inner_line)):
        #    crv = rg.NurbsCurve.CreateFromLine(inner_line[i])
        #    self.display.AddCurve(crv, self.display_color, 1)
        #iter_pts += anchor_pts
        
        threshold = horizontal
        if vertical < threshold:
            threshold = vertical
        if offset < threshold:
            threshold = offset
        #threshold = (offset + threshold)/2
        
        link = horizontal
        if vertical < link:
            link = vertical
        if offset > link:
            link = offset
        
        print("length parameter threshold offset link:")
        print(threshold)
        print(offset)
        print(link)
        
        
        goal_anchor = ghcomp.Kangaroo2Component.Anchor(point = anchor_pts, strength = 10000)
        goal_zfix = ghcomp.Kangaroo2Component.AnchorXYZ(point = all_pts, x = False, y = False, z = True, strength = 1000)
        goal_cpcin = ghcomp.Kangaroo2Component.CurvePointCollide(points = iter_pts, curve = outer_border, plane = ghcomp.XYPlane(), interior = True, strength = 1)
        goal_cpcout = ghcomp.Kangaroo2Component.CurvePointCollide(points = iter_pts, curve = inner_border, plane = ghcomp.XYPlane(), interior = False, strength = 1)
        goal_cpcin = [goal_cpcin]
        goal_cpcout = [goal_cpcout]
        goal_inner_length = ghcomp.Kangaroo2Component.LengthLine(line = inner_line, strength = 0.15)
        goal_inner_threshold = ghcomp.Kangaroo2Component.ClampLength(line = inner_line, lowerlimit = threshold, upperlimit = link, strength = 1)
        goal_border_length = ghcomp.Kangaroo2Component.LengthLine(line = border_line, length = offset, strength = 0.2)
        #goal_border_length = ghcomp.Kangaroo2Component.ClampLength(line = border_line, lowerlimit = threshold, upperlimit = offset, strength = 2)
        
        #goal_1 = ghcomp.Entwine(goal_anchor, goal_zfix)
        #goal_2 = ghcomp.Entwine(goal_cpcin, goal_cpcout)
        #goal_3 = ghcomp.Entwine(goal_inner_length, goal_inner_threshold, goal_border_length)
        #goal_obj = ghcomp.Entwine(goal_1, goal_2, goal_3)
        
        # Make an empty datatree
        goal_obj = gh.DataTree[object]()
        
        # Add data to it (note that you assign your own path to the level you like)
        goal_obj.AddRange(goal_anchor, gh.Kernel.Data.GH_Path(0,0))
        goal_obj.AddRange(goal_zfix, gh.Kernel.Data.GH_Path(0,1))
        goal_obj.AddRange(goal_cpcin, gh.Kernel.Data.GH_Path(0,2))
        goal_obj.AddRange(goal_cpcout, gh.Kernel.Data.GH_Path(0,3))
        goal_obj.AddRange(goal_inner_length, gh.Kernel.Data.GH_Path(0,4))
        goal_obj.AddRange(goal_inner_threshold, gh.Kernel.Data.GH_Path(0,5))
        goal_obj.AddRange(goal_border_length, gh.Kernel.Data.GH_Path(0,6))
        
        subiter = 1000
        _, pts, _ = ghcomp.Kangaroo2Component.StepSolver(goal_obj, 0.01, True, 0.99, subiter, True)
        
        filter, _ = ghcomp.PointInCurve(pts, outer_border)
        filter, _ = ghcomp.Equality(filter, 2)
        pts, _ = ghcomp.Dispatch(pts, filter)
        
        pts += fix_pts
        
        
        return pts
    
    def construct_ring_mesh(self, outer_border, inner_border, pts):
        outer_srf = ghcomp.BoundarySurfaces(outer_border)
        outer_mesh = rg.Mesh.CreateFromBrep(outer_srf)
        print("*****get outer mesh*******")
        print(len(outer_mesh))
        outer_mesh = outer_mesh[0]
        
        inner_srf = ghcomp.BoundarySurfaces(inner_border)
        inner_mesh = rg.Mesh.CreateFromBrep(inner_srf)
        print("*****get inner mesh*******")
        print(len(inner_mesh))
        inner_mesh = inner_mesh[0]
        
        raw_mesh = ghcomp.DelaunayMesh(pts, ghcomp.XYPlane())
        raw_center, _ = ghcomp.FaceNormals(raw_mesh)
        _, _, _, z_axis = ghcomp.DeconstructPlane(ghcomp.XYPlane())
        _, outer_hit = ghcomp.MeshXRay(outer_mesh, raw_center, z_axis)
        _, inner_hit = ghcomp.MeshXRay(inner_mesh, raw_center, z_axis)
        inner_unhit = ghcomp.GateNot(inner_hit)
        cull_pattern = ghcomp.GateAnd(outer_hit, inner_unhit)
        
        cull_pattern = ghcomp.GateNot(cull_pattern)
        ring_mesh = ghcomp.CullFaces(raw_mesh, cull_pattern)
        
        return outer_mesh, inner_mesh, ring_mesh

    def generate_grid_array(self, top_border, bottom_border, horizontal, vertical, block_aligned, band_aligned):
        top_border, bottom_border, border = self.construct_border(top_border, bottom_border)
        box, _ = ghcomp.BoundingBox(border, ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)))
        center_pt, d_vec, _, _, _ = ghcomp.BoxProperties(box)
        diag_length = ghcomp.VectorLength(d_vec)
        
        centerx, centery, centerz = ghcomp.Deconstruct(center_pt)
        x,y,z = ghcomp.DeconstructVector(d_vec)
        
        left_up = ghcomp.ConstructPoint(centerx - x/2, centery + y/2, z)
        left_down = ghcomp.ConstructPoint(centerx - x/2, centery - y/2, z)
        right_up = ghcomp.ConstructPoint(centerx + x/2, centery + y/2, z)
        right_down = ghcomp.ConstructPoint(centerx + x/2, centery - y/2, z)
        
        diag_direc = ghcomp.Subtraction(right_up, left_down)
        diag_line = ghcomp.LineSDL(right_down, diag_direc, diag_length)
        _, diag_pt = ghcomp.EndPoints(diag_line)
        extend_line = ghcomp.Line(left_up, diag_pt)
        
        grid_num = int(math.ceil(ghcomp.Length(extend_line)), horizontal)
        white_start, _, _ = ghcomp.DivideCurve(extend_line, grid_num, False)
        
        grid_vec, _ = ghcomp.VectorXYZ(-1, -1, 0)
        if block_aligned == False:
            grid_vec, _ = ghcomp.VectorXYZ(-horizontal/2, -vertical, 0)
        else:
            grid_vec, _ = ghcomp.VectorXYZ(-horizontal, -vertical, 0)
            
        white_grid_array = ghcomp.LineSDL(white_start, grid_vec, diag_length)
        
        black_start = []
        if band_aligned == False:
            for i in range(len(white_start)-1):
                black_start.append(ghcomp.Division(ghcomp.Addition(white_start[i]+white_start[i+1]),2))
        black_grid_array = ghcomp.LineSDL(black_start, grid_vec, diag_length)
        
        grid_start, _, _ = ghcomp.CurveXCurve(white_grid_array, top_border)
        grid_end, _, _ = ghcomp.CurveXCurve(white_grid_array, bottom_border)
        white_grid_line = ghcomp.Line(grid_start, grid_end)
        white_grid_line = white_grid_line.flatten()
        
        return white_grid_line, white_grid_array, black_grid_array
        
    def array_white_fill(self, grid_crv, horizontal, vertical, aligned, fit_ends):
        #给定上下边界填充斜向阵列
        pts = []
        unit_length = 1
        
        top_pts = []
        bottom_pts = []
        limbo_pts = []
        
        if aligned == False:
            unit_length = math.sqrt(0.25 * horizontal*horizontal + vertical*vertical)
        else:
            unit_length = math.sqrt(horizontal*horizontal + vertical*vertical)
        
        for i in range(len(fit_ends)):
            cur_crv = fit_ends[i]
            start_pt, end_pt = ghcomp.EndPoints(cur_crv)
            x = start_pt.X
            y = start_pt.Y
            z = start_pt.Z
            x_domain = end_pt.X - x
            y_domain = end_pt.Y - y
            z_domain = end_pt.Z - z
            num = int(math.floor(ghcomp.Length(cur_crv)/unit_length)+1)
            cur_pts = []
            for k in range(num+1):
                cur_fac = k/num
                cur_x = x + cur_fac*x_domain
                cur_y = y + cur_fac*y_domain
                cur_z = z + cur_fac*z_domain
                cur_pt = ghcomp.ConstructPoint(cur_x, cur_y, cur_z)
                cur_pts.append(cur_pt)
            for k in range(1, num-1):
                pts.append(cur_pts[k])
            if num>1:
                top_pts.append(cur_pts[0])
            bottom_pts.append(cur_pts[-1])
            limbo_pts.append(cur_pts[-2])
        
        return pts, top_pts, bottom_pts, limbo_pts

    @staticmethod
    def load_block_xml(file_path, region):
        xmldoc = System.Xml.XmlDocument()
        xmldoc.Load(file_path)
        items = xmldoc.SelectNodes("setting/block/hole")
        rows = []
        for item in items:
            nid = int(item.GetAttributeNode('id').Value)
            row = HoleFrits(nid, region)
            dot_type = item.GetAttributeNode('type').Value
            row.dot_type = {'circle': FritType.CIRCLE_DOT, 'roundrect': FritType.ROUND_RECT}[dot_type]
            arrange_type = item.GetAttributeNode('arrange').Value
            row.arrange_type = {'heading': HoleArrangeType.HEADING, 'cross': HoleArrangeType.CROSS }[arrange_type]
            val = dict()

            for node in item.ChildNodes:
                val[node.Name] = float(node.InnerText)
            row.stepping = val['stepping']
            row.vspace = val['vspace']
            if 'fposition' in val.keys():
                row.first_line_position = val['fposition']
            if row.dot_type == FritType.CIRCLE_DOT:
                row.circle_config.r = val['r']
            elif row.dot_type == FritType.ROUND_RECT:
                row.round_rect_config.k = val['k']
                row.round_rect_config.r = val['r']
            rows.append(row)
        return rows
       

    