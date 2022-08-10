#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, August 4th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext
import System
from utils import safe_list_access
import random as rnd
import math
import ghpythonlib.components as ghcomp

 
# SampleEtoRoomNumber dialog class

class FuyaoFrit:
    def __init__(self):
        self.inner_curve = None
        self.outer_curve = None
        self.refer_curve = None
        self.radius = [0.425, 0.6, 0.85]
        self.vspace = [1.4, 1.7]
        self.hspace = [2.2]
        self.row_confs = []
        self.display_curves = []
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
    
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
        # todo by Zheng Yawen
        pass
     
    def init_curves(self):
        self.reorder_outer_curve()
        self.reorder_inner_curve()
    
    
    
    def calculate_row_conf(self):
        crv_length = ghcomp.Length(self.refer_curve)
        print(crv_length)
        radius = self.radius
        vspace = self.vspace
        hspace = self.hspace
         
        i = 0
        total_offset = 0.0
        row_confs = []
        n = len(radius)
        while True:
            cr = safe_list_access(radius, i)
            cv = safe_list_access(vspace, i - 1)
            print(cv)
            offset = cv
            if cv == 0:
                offset = cr
            total_offset += offset
            item = {'offset':total_offset , 'radius': cr, 'vspace': cv, 'hspace': hspace[0]}
            row_confs.append(item)
        
            if ((total_offset >= crv_length) or (i == n - 1)):
                break
            else:
                i += 1
        print(row_confs)
        self.row_confs = row_confs
    
    # 排布第一排的点
    def first_row_pts_from_inner(self):
        crv = self.inner_curve
        hspace = self.row_confs[0]['hspace']
        radius = self.row_confs[0]['radius']
        offset = self.row_confs[0]['offset']
        # points
        crv_length = ghcomp.Length(crv)
        print(crv)
        print(crv_length)
        print(hspace)
        pts_num = int(crv_length / hspace)
        # offset curve 
        center_curve = ghcomp.OffsetCurve(crv, distance=offset, corners=1)
        pts, vec, _ = ghcomp.DivideCurve(center_curve, pts_num, False)
        refer_pts, t, _ = ghcomp.CurveClosestPoint(pts, crv)
        _, refer_vec, _ = ghcomp.EvaluateCurve(crv, t)
        bottom_border = ghcomp.OffsetCurve(center_curve, distance=radius, corners=1)
        return pts, vec, refer_pts, refer_vec, bottom_border
    
    def first_row_pts_from_outer(self, refer_pts, refer_vec):
        refer_dis = ghcomp.Length(self.refer_curve)
        crv = self.outer_curve
        pts, t, D = ghcomp.CurveClosestPoint(refer_pts, crv)
        _, T, _ = ghcomp.EvaluateCurve(crv, t)
        # 角度过滤
        v = ghcomp.Multiplication(refer_vec, T)
        x1 = ghcomp.Absolute(v)
        x2 = ghcomp.ArcCosine(x1)
        x3 = ghcomp.Division(x2, ghcomp.Pi())
        # print(x3)
        x4 = ghcomp.Multiplication(x3, 180)
        angle_threshold = 10
        angle_filter, _ = ghcomp.SmallerThan(x4, 10)
      
        dis_threshold = refer_dis * 1.1
        dis_filter, _ = ghcomp.SmallerThan(D, dis_threshold)
        filter = ghcomp.GateAnd(angle_filter, dis_filter)
        shift_filter = ghcomp.ShiftList(filter, 1, True)
        xor_filter = ghcomp.GateXor(filter, shift_filter)
        # print(xor_filter)
        true_index, _ = ghcomp.MemberIndex(xor_filter, True)
        index_start = true_index[0]
        index_end = true_index[1]
        
        shift_pts = ghcomp.ShiftList(pts, 1, True)
        start_pts = ghcomp.ListItem(shift_pts, index_start)
        _, start_t, _ = ghcomp.CurveClosestPoint(start_pts, crv)
        end_t = ghcomp.ListItem(t, index_end)
        hole_domain = ghcomp.Bounds([start_t, end_t])
        hole_curve = ghcomp.SubCurve(crv, hole_domain)
        top_subcrv = hole_curve
        hole_curve_len = ghcomp.Length(top_subcrv)
        # check it!
        hspace = self.row_confs[-1]['hspace']
        hole_num = int(hole_curve_len / hspace)
        hole_pts, _, _ = ghcomp.DivideCurve(hole_curve, hole_num, False)
        hole_pts_len = ghcomp.ListLength(hole_pts)
        
        filter_domain = ghcomp.ConstructDomain(index_start, index_end)
        filter_steps = index_end - index_start
        filter_range = ghcomp.Range(filter_domain, filter_steps)
        filter_range = ghcomp.CullIndex(filter_range, 0, True)
        replaced_filter = ghcomp.ReplaceItems(filter, False, filter_range)
        A, B = ghcomp.Dispatch(pts, replaced_filter)
        
        # insert new points
        index_list = []
        i = 0
        while(i<hole_pts_len):
            index_list.append(index_start+1)
            i += 1
        refer_pts = ghcomp.InsertItems(A, hole_pts, index_list)
        # 将refer_pts 投影到边的off
        this_offset = self.row_confs[-1]['offset']
        relative_offset = refer_dis - this_offset
        print(self.row_confs)
        print(this_offset)
        print(relative_offset)
        center_crv = ghcomp.OffsetCurve(crv, distance=relative_offset, corners=1)
        circle_pts, _, _ = ghcomp.CurveClosestPoint(refer_pts, center_crv)
        offset_curve = center_crv
        top_subcrv_offset = ghcomp.OffsetCurve(top_subcrv, distance=relative_offset, corners=1)
        radius = self.row_confs[-1]['radius']
        top_border = ghcomp.OffsetCurve(top_subcrv_offset, distance=radius, corners=1)
        return top_subcrv, refer_pts, circle_pts, offset_curve, top_border
        
    def band_area_filling(self):
        row_confs = self.row_confs
        row_num = ghcomp.ListLength(row_confs)
        print(row_num)
        inside_row_num = row_num - 2
        bottom_inside_row_num = int((inside_row_num + 1) / 2)
        #print(bottom_inside_row_num)
        top_inside_row_num = inside_row_num - bottom_inside_row_num

        inside_refer_pts = []
        inside_radius = []
        bottom_border_pts = []
        top_border_pts = []

        for i in range(bottom_inside_row_num):
            current_row_conf = ghcomp.ListItem(row_confs, i + 1, True)
            _, current_offset, _ = ghcomp.Dhictionary.DictSelect([current_row_conf], 'offset')
            _, current_radius, _ = ghcomp.Dhictionary.DictSelect([current_row_conf], 'radius')
            #print(current_radius)
            current_crv = ghcomp.OffsetCurve(inner_crv, current_offset)
            bottom_border = ghcomp.OffsetCurve(current_crv, current_radius)
            P, t, D = ghcomp.CurveClosestPoint(inner_refer_pts, current_crv)
            if i % 2 == 0:
                # mapping to inner line
                #print(ghcomp.ListLength(P))
                P1 = ghcomp.CullIndex(P, ghcomp.ListLength(P) - 1)
                #print(ghcomp.ListLength(P1))
                P2 = ghcomp.CullIndex(P, 0)
                P3 = ghcomp.Addition(P1, P2)
                P4 = ghcomp.Division(P3, 2)
                #print(ghcomp.ListLength(P4))
                P5, _, _ = ghcomp.CurveClosestPoint(P4, current_crv)
                inside_refer_pts += P5
                if i == (bottom_inside_row_num - 1):
                    bottom_border_pts += P5
                for j in range(len(P5)):
                    inside_radius.append(current_radius)

            else:
                # mapping to outer line
                inside_refer_pts += P
                if i == (bottom_inside_row_num - 1):
                    bottom_border_pts += P
                for j in range(len(P)):
                    inside_radius.append(current_radius)
                

        for i in range(bottom_inside_row_num, inside_row_num):
            next_row_conf = ghcomp.ListItem(row_confs, i+2, True)
            current_row_conf = ghcomp.ListItem(row_confs, i+1, True)
            _, current_offset, _ = ghcomp.Dhictionary.DictSelect([current_row_conf], 'offset')
            _, current_radius, _ = ghcomp.Dhictionary.DictSelect([current_row_conf], 'radius')
            #print(current_radius)
            _, current_vspace, _ = ghcomp.Dhictionary.DictSelect([current_row_conf], 'vspace')
            _, next_vspace, _ = ghcomp.Dhictionary.DictSelect([next_row_conf], 'vspace')
            crv_offset = refer_dis - current_offset
            current_crv = ghcomp.OffsetCurve(outer_crv, -crv_offset)
            P, t, D = ghcomp.CurveClosestPoint(outer_refer_pts, current_crv)
            print(i, current_vspace)
            top_border = ghcomp.OffsetCurve(top_border, -next_vspace)
            
            if i % 2 == 0:
                # mapping to inner line
                #print('here')
                #print(ghcomp.ListLength(P))
                P1 = ghcomp.CullIndex(P, ghcomp.ListLength(P) - 1)
                #print(ghcomp.ListLength(P1))
                P2 = ghcomp.CullIndex(P, 0)
                P3 = ghcomp.Addition(P1, P2)
                P4 = ghcomp.Division(P3, 2)
                #print(ghcomp.ListLength(P4))
                P5, _, _ = ghcomp.CurveClosestPoint(P4, current_crv)
                inside_refer_pts += P5
                if i == bottom_inside_row_num:
                    top_border_pts += P5
                for j in range(len(P5)):
                    inside_radius.append(current_radius)
            else:
                # mapping to outer line
                inside_refer_pts += P
                if i == bottom_inside_row_num:
                    top_border_pts += P
                for j in range(len(P)):
                    inside_radius.append(current_radius)

        top_border_updated = top_border
        bottom_border_updated = bottom_border
        print("finish")
                
    def run(self):
        self.init_curves()
        self.calculate_row_conf()
        pts, vec, refer_pts, refer_vec, bottom_border = self.first_row_pts_from_inner()
        top_subcrv, refer_pts, circle_pts, offset_curve, top_border = self.first_row_pts_from_outer(refer_pts, refer_vec)
        
        # c = ghcomp.ColourRGB(0, 0, 0, 255)
        # ghcomp.CustomPreview(circle_pts, c)
        # display.AddCurve(crv,color,i+1)
        # draw points
        color = rc.Display.ColorHSL(rnd.random(),1.0,0.5)
        for p in circle_pts:
            self.display.AddCircle(rc.Geometry.Circle(p, self.row_confs[0]['radius']), color, 1) 
        
        scriptcontext.doc.Views.Redraw()


        # self.custom_display()
    def close(self):
        self.display.Clear()
        