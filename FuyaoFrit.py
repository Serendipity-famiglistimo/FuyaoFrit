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
import Rhino.Geometry as rg
from frits.CircleDot import CircleDot

 
# SampleEtoRoomNumber dialog class

class FuyaoFrit:
    def __init__(self):
        self.dot = CircleDot(0, 0, 0)
        self.inner_curve = None
        self.outer_curve = None
        self.refer_curve = None
        self.radius = [0.425, 0.6, 0.85]
        self.vspace = [1.4, 1.7]
        self.hspace = [2.2]
        self.inner_radius = 0.89
        self.horizontal = 2.2
        self.vertical = 1.7
        self.aligned = False
        self.row_confs = []
        
        self.half_bound = True
        self.rec_band = True
        self.half_sr = 0.25
        self.rec_sr = 0.1

        self.display_curves = []
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
        
        self.pts = []
        self.rs = []
        self.half_pts = []
        self.half_rs = []
        self.half_dirs = []
        self.rec_pts = []
        self.rec_rs = []
        self.rec_dirs = []
        
    # 确定是否将outer curve flip
    def reorder_outer_curve(self):
        tolerance = rc.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
        curve = self.outer_curve
        flip_curve, _ = ghcomp.FlipCurve(curve)
        
        #offset_flip_curve = flip_curve.Offset(ghcomp.XYPlane(), 1.0, tolerance, rg.CurveOffsetCornerStyle.Smooth)
        #offset_curve = curve.Offset(ghcomp.XYPlane, 1.0, tolerance, rg.CurveOffsetCornerStyle.Smooth)
        
        #offset_flip_curve = ghcomp.OffsetCurve(flip_curve, plane = ghcomp.XYPlane(), distance=1.0, corners=1)
        #self.display.AddCurve(offset_flip_curve)
        offset_curve = ghcomp.OffsetCurve(curve, plane = ghcomp.XYPlane(), distance=1.0, corners=1)
        #self.display.AddCurve(offset_curve)
        
        close_curve, _ = ghcomp.Pufferfish.CloseCurve(curve)
        offset_close_curve, _ = ghcomp.Pufferfish.CloseCurve(offset_curve)
        
        offset_curve_area, _ = ghcomp.Area(offset_close_curve)
        curve_area, _ = ghcomp.Area(close_curve)
        #print("calculate area: {0} {1}".format(offset_curve_area, curve_area))
        if curve_area < offset_curve_area:
            print("We flip the outer curve.")
            self.outer_curve = flip_curve
            
    # 确定是否将inner curve flip
    def reorder_inner_curve(self):
        curve = self.inner_curve
        closedflag = ghcomp.Closed(curve)
        outer_start, _ = ghcomp.EndPoints(self.outer_curve)
        
        if closedflag:
            _, t, _ = ghcomp.CurveClosestPoint(outer_start, curve)
            adj_curve = ghcomp.Seam(curve, t)
            adj_flip_curve, _ = ghcomp.FlipCurve(adj_curve)
            
            adj_start, _ = ghcomp.EndPoints(adj_curve)
            _, adj_t, _ = ghcomp.CurveClosestPoint(adj_start, adj_curve)
            _, inner_tgt, _ = ghcomp.EvaluateCurve(adj_curve, adj_t)
            _, outer_t, _ = ghcomp.CurveClosestPoint(outer_start, self.outer_curve)
            _, outer_tgt, _ = ghcomp.EvaluateCurve(self.outer_curve, outer_t)
            angle, _ = ghcomp.Angle(inner_tgt, outer_tgt)
            if angle > ghcomp.Pi()/2:
                self.inner_curve = adj_flip_curve
                print("flip closed inner curve")
                
            else:
                self.inner_curve = adj_curve

        else:
            flip_curve, _ = ghcomp.FlipCurve(curve)
            inner_start, inner_end = ghcomp.EndPoints(curve)
            ssdist = ghcomp.Distance(outer_start, inner_start)
            sedist = ghcomp.Distance(outer_start, inner_end)
            if ssdist > sedist:
                self.inner_curve = flip_curve
                print("flip open inner curve")
            else:
                self.inner_curve = curve
                
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
        bottom_border = ghcomp.OffsetCurve(center_curve, plane = ghcomp.XYPlane, distance=radius, corners=1)
        
        if self.rec_band == False:
            for i in range(len(pts)):
                self.pts.append(pts[i])
                self.rs.append(radius)
        else:
            dir, _ = self.get_dir(pts, self.inner_curve)
            for i in range(len(pts)):
                self.rec_pts.append(pts[i])
                self.rec_rs.append(radius)
                self.rec_dirs.append(dir[i])
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
        print("what is the problem with you")
        print(self.row_confs)
        print(this_offset)
        print(relative_offset)
        
        center_crv = ghcomp.OffsetCurve(crv, plane = ghcomp.XYPlane(), distance=relative_offset, corners=1)
        #print("center_crv")
        #self.display.AddCurve(center_crv)
        
        circle_pts, _, _ = ghcomp.CurveClosestPoint(refer_pts, center_crv)
        offset_curve = center_crv
        top_subcrv_offset = ghcomp.OffsetCurve(top_subcrv, plane = ghcomp.XYPlane(), distance=relative_offset, corners=1)
        #self.display.AddCurve(top_subcrv_offset)
        
        radius = self.row_confs[-1]['radius']
        top_border = ghcomp.OffsetCurve(top_subcrv_offset, plane = ghcomp.XYPlane(), distance=radius, corners=1)
        
        #self.display.AddCurve(top_border)
        
        return top_subcrv, refer_pts, circle_pts, offset_curve, top_border
        
    def shift_half(self, pts, crv):
        _, t, _ = ghcomp.CurveClosestPoint(pts, crv)
        shift_t = ghcomp.ShiftList(t, 1, True)
        ave_t = ghcomp.Division(ghcomp.Addition(t, shift_t), 2)
        len = ghcomp.ListLength(ave_t) - 1
        split_t, _ = ghcomp.SplitList(ave_t, len)
        shifted_pts, _, _ = ghcomp.EvaluateCurve(crv, split_t)
        return shifted_pts
        
    def shift_first_outer_row(self, aligned_pts, shifted_pts):
        row_confs = self.row_confs
        row_num = ghcomp.ListLength(row_confs)
        radius = self.row_confs[-1]['radius']
        outer_pts = []
        if(row_num % 2 == 0):
            outer_pts = shifted_pts
        else:
            outer_pts = aligned_pts
        
        if self.half_bound == False:
            if self.rec_band == False:
                for i in range(len(outer_pts)):
                    self.pts.append(outer_pts[i])
                    self.rs.append(radius)
            else:
                dir, _ = self.get_dir(outer_pts, self.outer_curve)
                for i in range(len(outer_pts)):
                    self.rec_pts.append(outer_pts[i])
                    self.rec_rs.append(radius)
                    self.rec_dirs.append(dir[i])
        else:
            dir, _ = self.get_dir(outer_pts, self.outer_curve)
            for i in range(len(outer_pts)):
                self.half_pts.append(outer_pts[i])
                self.half_rs.append(radius)
                self.half_dirs.append(dir[i])
            
        return outer_pts
        
    def inside_pts(self, inner_refer_pts, outer_refer_pts, top_border, bottom_border):
        #todo: input top_row_num and bottom_row_num
        
        refer_dis = ghcomp.Length(self.refer_curve)
        
        row_confs = self.row_confs
        inner_crv = self.inner_curve
        outer_crv = self.outer_curve
        
        row_num = ghcomp.ListLength(row_confs)
        print(row_num)
        inside_row_num = row_num - 2
        bottom_inside_row_num = int((inside_row_num + 1) / 2)
        top_inside_row_num = inside_row_num - bottom_inside_row_num
        
        inside_refer_pts = []
        inside_radius = []
        bottom_border_pts = []
        top_border_pts = []
        
        inside_dir = []
        
        for i in range(bottom_inside_row_num):
            current_row_conf = ghcomp.ListItem(row_confs, i + 1, True)
            current_offset = current_row_conf['offset']
            current_radius = current_row_conf['radius']
            #_, current_offset, _ = ghcomp.Dhictionary.DictSelect([current_row_conf], 'offset')
            #_, current_radius, _ = ghcomp.Dhictionary.DictSelect([current_row_conf], 'radius')
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
                #print("P5")
                #print(P5)
                inside_refer_pts += P5
                p_dir, _ = self.get_dir(P5, self.inner_curve)
                
                if i == (bottom_inside_row_num - 1):
                    bottom_border_pts += P5
                for j in range(len(P5)):
                    inside_radius.append(current_radius)
        
            else:
                # mapping to outer line
                inside_refer_pts += P
                p_dir, _ = self.get_dir(P, self.inner_curve)
                if i == (bottom_inside_row_num - 1):
                    bottom_border_pts += P
                for j in range(len(P)):
                    inside_radius.append(current_radius)
            inside_dir += p_dir
        
        for i in range(bottom_inside_row_num, inside_row_num):
            next_row_conf = ghcomp.ListItem(row_confs, i+2, True)
            current_row_conf = ghcomp.ListItem(row_confs, i+1, True)
            print(current_row_conf, next_row_conf)
            current_offset= current_row_conf['offset']
            
            current_radius= current_row_conf['radius']
            
            current_vspace= current_row_conf['vspace']
            next_vspace= next_row_conf['vspace']
            
            crv_offset = refer_dis - current_offset
            current_crv = ghcomp.OffsetCurve(outer_crv, plane = ghcomp.XYPlane(), distance = crv_offset)
            P, t, D = ghcomp.CurveClosestPoint(outer_refer_pts, current_crv)
            print(i, current_vspace)
            top_border = ghcomp.OffsetCurve(top_border, plane = ghcomp.XYPlane(), distance = next_vspace)
            
            if i % 2 == 0:
                # mapping to inner line
                P1 = ghcomp.CullIndex(P, ghcomp.ListLength(P) - 1)
                #print(ghcomp.ListLength(P1))
                P2 = ghcomp.CullIndex(P, 0)
                P3 = ghcomp.Addition(P1, P2)
                P4 = ghcomp.Division(P3, 2)
                #print(ghcomp.ListLength(P4))
                P5, _, _ = ghcomp.CurveClosestPoint(P4, current_crv)
                inside_refer_pts += P5
                p_dir, _ = self.get_dir(P5, self.outer_curve)
                if i == bottom_inside_row_num:
                    top_border_pts += P5
                for j in range(len(P5)):
                    inside_radius.append(current_radius)
            else:
                # mapping to outer line
                inside_refer_pts += P
                p_dir, _ = self.get_dir(P, self.outer_curve)
                if i == bottom_inside_row_num:
                    top_border_pts += P
                for j in range(len(P)):
                    inside_radius.append(current_radius)
            inside_dir += p_dir
            
        print("order inside pts")
        print(len(inside_refer_pts))
        if self.rec_band == False:
            for i in range(len(inside_refer_pts)):
                self.pts.append(inside_refer_pts[i])
                self.rs.append(inside_radius[i])
                
        else:
            for i in range(len(inside_refer_pts)):
                self.rec_pts.append(inside_refer_pts[i])
                self.rec_rs.append(inside_radius[i])
                self.rec_dirs.append(inside_dir[i])
        return inside_refer_pts, inside_radius, top_border, bottom_border, bottom_border_pts, top_border_pts
        
    def select_border(self, top_border1, top_border2, bottom_border1, bottom_border2):
        top_border = top_border2
        bottom_border = bottom_border2
        
        if len(top_border)==0:
            top_border = top_border1
        
        if len(bottom_border)==0:
            bottom_border = bottom_border1
        
        return top_border, bottom_border
        
    def pointAlongCurve(self, pts, crv):
        hspace = self.hspace[0]
        _, _, dis = ghcomp.CurveClosestPoint(pts, crv)
        min_dis, _ = ghcomp.DeconstructDomain(ghcomp.Bounds(dis))
        threshold = min_dis + hspace
        pattern = ghcomp.SmallerThan(dis, threshold)
        along_pts = ghcomp.Dispatch(pts, pattern)
        
        return along_pts
        
    def trim_border(self, top_border, bottom_border):
        pts, _, _ = ghcomp.ControlPoints(top_border)
        _, t, _ = ghcomp.CurveClosestPoint(pts, bottom_border)
        domain = ghcomp.Bounds(t)
        bottom_subcrv = ghcomp.SubCurve(bottom_border, domain)
        
        pts, _, _ = ghcomp.ControlPoints(bottom_border)
        _, t, _ = ghcomp.CurveClosestPoint(pts, top_border)
        domain = ghcomp.Bounds(t)
        top_subcrv = ghcomp.SubCurve(top_border, domain)
        
        return top_subcrv, bottom_subcrv
        
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
        
    def block_fill(self, Crv, horizontal, vertical, surround, aligned):
        Pt = []

        threshold = min(horizontal, vertical)
        stepCrv = int(math.ceil(Crv.GetLength()/surround))
        
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
                if aligned == True:
                    pt = rg.Point3d(xStart + i*horizontal, yStart + j*vertical, 0)
                else:
                    if j%2 == 0:
                        pt = rg.Point3d(xStart + i*horizontal, yStart + j*vertical, 0)
                    else:
                        pt = rg.Point3d(xStart + (i+0.5)*horizontal, yStart + j*vertical, 0)
                
                PtCtmt = Crv.Contains(pt)
                if PtCtmt == rg.PointContainment.Inside:
                    Pt.append(pt)
                #else:
                    #print(PtCtmt)
                
                #else:
                    #t = Crv.ClosestPoint(pt)
                    #ptCrv = Crv.PointAt(t[1])
                    #distance = ptCrv.DistanceTo(pt)
                    #if distance < threshold/3:
                        #Pt.append(pt)
        
        radius = self.inner_radius
        print(len(Pt))
        for i in range(len(Pt)):
            self.pts.append(Pt[i])
            self.rs.append(radius)
            
        return Pt, threshold, stepCrv
        
    def get_dir(self, refer_pts, crv):
        _, t, _ = ghcomp.CurveClosestPoint(refer_pts, crv)
        pt, tgt, _ = ghcomp.EvaluateCurve(crv, t)
        
        return tgt, pt
        
    def half_circle(self, pt, tgt, radius, small_radius):
        arc, _ = ghcomp.Arc(pt, radius, ghcomp.Pi())
        #arc, _ = ghcomp.FlipCurve(arc)
        offset = ghcomp.Addition(radius, small_radius)
        offset_vec = ghcomp.UnitX(offset)
        left_c = ghcomp.Subtraction(pt, offset_vec)
        right_c = ghcomp.Addition(pt, offset_vec)
        left_a = ghcomp.ConstructDomain(ghcomp.Pi(1.5), ghcomp.Pi(2))
        left_arc, _ = ghcomp.Arc(left_c, small_radius, left_a)
        right_a = ghcomp.ConstructDomain(ghcomp.Pi(1), ghcomp.Pi(1.5))
        right_arc, _ = ghcomp.Arc(right_c, small_radius, right_a)
        
        arc1 = ghcomp.GraftTree(arc)
        arc2 = ghcomp.GraftTree(left_arc)
        arc3 = ghcomp.GraftTree(right_arc)
        arcs = ghcomp.Merge(ghcomp.Merge(arc2, arc1), arc3)
        crvs = ghcomp.JoinCurves(arcs)
        crvs = ghcomp.FlattenTree(crvs)
        
        crvs, _ = ghcomp.Pufferfish.CloseCurve(crvs, 0, 0.5, 0)
        #half_circle0 = []
        #for i in range(len(crvs)):
            #half_circle0.append(crvs[i])
            
        rotate_angle = ghcomp.Addition(self.tgt_angle(tgt),ghcomp.Pi())
        
        half_circle = []
        for i in range(len(pt)):
            hc, _ = ghcomp.Rotate(crvs[i], rotate_angle[i], pt[i])
            half_circle.append(hc)
        #half_circle, _ = ghcomp.Rotate(crvs, rotate_angle, pt)
        #for i in range(len(half_circle)):
            #half_circle0.append(half_circle[i])
        
        y_offset = ghcomp.Subtraction(pt, ghcomp.UnitY(small_radius))
        border_pt, _ = ghcomp.Rotate(y_offset, rotate_angle, pt)
        
        return half_circle, border_pt
        
    def rectangle(self, pt, tgt, radius):
        rotate_angle = self.tgt_angle(tgt)
        x, y, _ = ghcomp.Deconstruct(pt)
        x_domain = ghcomp.ConstructDomain(ghcomp.Subtraction(x, radius), ghcomp.Addition(x, radius))
        y_domain = ghcomp.ConstructDomain(ghcomp.Subtraction(y, radius), ghcomp.Addition(y, radius))
        rec, _ = ghcomp.Rectangle(ghcomp.XYPlane(), x_domain, y_domain, ghcomp.Division(radius, 2))
        rec, _ = ghcomp.Rotate(rec, rotate_angle, pt)
        
        return rec
        
    def tgt_angle(self, tgt):
        angle, _ = ghcomp.Angle(tgt, ghcomp.UnitX(1))
        _, y, _ = ghcomp.Deconstruct(tgt)
        larger_pattern, _ = ghcomp.LargerThan(y,0)
        factor = ghcomp.Subtraction(ghcomp.Multiplication(larger_pattern,2),1)
        rotate_angle = ghcomp.Multiplication(angle, factor)
        
        return rotate_angle
        
    def circle_packing(self, pt, boundary):
        srf = ghcomp.BoundarySurfaces(boundary)
        mesh = ghcomp.MeshBrep(srf)
        b_radius = self.bounding_radius()
        goal_obj = ghcomp.Kangaroo2Component.ImageCircles(pt, mesh, b_radius, b_radius, boundary, 0.0001)
        _, vertice, _ = ghcomp.Kangaroo2Component.Solver(goal_obj, False, 0, 0.1, False)
        
        return vertice
        
    def bounding_radius(self):
        horizontal = self.horizontal
        vertical = self.vertical
        
        if self.aligned == False:
            hypotenuse = math.sqrt(0.25*horizontal*horizontal + vertical*vertical)
        else:
            hypotenuse = math.sqrt(horizontal*horizontal + vertical*vertical)
        
        min = horizontal/2
        if vertical/2 < min:
            min = vertical/2
        if hypotenuse/2 < min:
            min = hypotenuse/2
        
        return 1.1 * min
        
    def run(self):
        self.init_curves()
        self.calculate_row_conf()
        inner_pts, vec, inner_refer_pts, refer_vec, bottom_border = self.first_row_pts_from_inner()
        top_subcrv, outer_refer_pts, outer_pts, offset_curve, top_border = self.first_row_pts_from_outer(inner_refer_pts, refer_vec)
        
        #self.display.AddCurve(top_border)
        
        shift_outer_pts = self.shift_half(outer_pts, offset_curve)
        outer_pts = self.shift_first_outer_row(outer_pts, shift_outer_pts)
        
        
        inside_refer_pts, inside_radius, top_border, bottom_border, bottom_border_pts, top_border_pts = self.inside_pts(inner_refer_pts, outer_refer_pts, top_border, bottom_border)
        top_pts, bottom_pts = self.select_border(inner_pts, top_border_pts, outer_pts, bottom_border_pts)
        
        top_border, bottom_border = self.trim_border(top_border, bottom_border)
        
        #self.display.AddCurve(top_border)
        #self.display.AddCurve(bottom_border)
        
        top_pts = self.pointAlongCurve(top_pts, top_border)
        bottom_pts = self.pointAlongCurve(bottom_pts, bottom_border)
        top_pts = ghcomp.ReverseList(top_pts)
        border_pts = ghcomp.Merge(top_pts, bottom_pts)
        
        #top_border, _ = ghcomp.FlipCurve(top_border)
        blockborder= self.construct_border(top_border, bottom_border)
        #self.display.AddCurve(blockborder)
        
        #for i in range(len(blockborder)):
        #    print(i)
        #    self.display.AddCurve(blockborder[i])
    
        inner_pts, threshold, stepCrv = self.block_fill(blockborder, self.horizontal, self.vertical, self.hspace[0], self.aligned)
        # draw points
        
        for i in range(len(self.pts)):
            self.display.AddCircle(rc.Geometry.Circle(self.pts[i], self.rs[i]), self.display_color, 1)
        
        if len(self.rec_pts)!=0:
            rec_crv = self.rectangle(self.rec_pts, self.rec_dirs, self.rec_rs)
        for i in range(len(self.rec_pts)):
            self.display.AddCurve(rec_crv[i], self.display_color, 1)
        
        if len(self.half_pts)!=0:
            half_crv, _ = self.half_circle(self.half_pts, self.half_dirs, self.half_rs, self.half_sr)
            #half_crv0, _ = self.half_circle(self.half_pts, ghcomp.UnitX(1), self.half_rs, self.half_sr)
            for i in range(len(half_crv)):
                self.display.AddCurve(half_crv[i], self.display_color, 1)
                #self.display.AddCurve(half_crv0[i], self.display_color, 1)
                #self.display.AddCircle(rc.Geometry.Circle(self.half_pts[i], self.half_rs[i]), self.display_color, 1)
        
        scriptcontext.doc.Views.Redraw()



        # self.custom_display()
        
    def close(self):
        self.display.Clear()
        