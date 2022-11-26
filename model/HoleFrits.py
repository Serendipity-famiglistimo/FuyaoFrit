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

clr.AddReference("System.Xml")
import System.Xml

class HoleArrangeType:
    HEADING=0
    CROSS=1
    @staticmethod
    def get_hole_arrange_type():
        return ['顶头', '交错']


class Dazhong_fill_holes:
    def __init__(self, upline, midline, downline, boundary, split_crv, edge_crv, horizontal, vertical, aligned = False):
        self.upline = upline
        self.midline = midline
        self.downline = downline
        self.boundary = boundary
        self.split_crv = split_crv
        self.edge_crv = edge_crv
        self.frit_black = []
        self.frit_white = []
        self.frit_bound = []
        
        self.horizontal = horizontal
        self.vertical = vertical
        self.aligned = aligned
        self.tolerance = 0.5
        
        self.display_color = rc.Display.ColorHSL(0, 1, 0)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
    
    def _generate_grid_pts(self, base_pts, vertical, downline):
        pts = []
        bound_pts = []
        dest_pts = []
        
        dest_pts0, _, dis = ghcomp.CurveClosestPoint(base_pts, downline)
        max = 0
        for i in range(len(dis)):
            if dis[i]>max:
                max = dis[i]
        
        base_vec = ghcomp.UnitY(-1)
        
        for i in range(len(dis)):
            base_line = ghcomp.LineSDL(base_pts[i], base_vec, 1.25*max)
            dest_pt, _, _ = ghcomp.CurveXCurve(base_line, downline)
            if dest_pt:
                dest_pts.append(dest_pt)
            else:
                dest_pts.append(dest_pts0[i])
        
        v_dis = ghcomp.Distance(base_pts, dest_pts)
        vlength = ghcomp.Average(v_dis)
        v_num = int(math.floor(vlength/vertical))
        if v_num%2 != 0:
            v_num = v_num - 1
        
        relation, _ = ghcomp.PointInCurve(base_pts, self.boundary)
        base_array_pts, _ = ghcomp.Dispatch(base_pts, relation)
        if base_array_pts:
            bound_pts.append(base_array_pts[0])
    
        for i in range(1, v_num):
            cur_pts = []
            for j in range(len(base_pts)):
                cur_base = base_pts[j]
                cur_dest = dest_pts[j]
                cur_vec, _ = ghcomp.Vector2Pt(cur_base, cur_dest, True)
                cur_dis = i*v_dis[j]/v_num
                line = ghcomp.LineSDL(cur_base, cur_vec, cur_dis)
                _, cur_pt = ghcomp.EndPoints(line)
                cur_pts.append(cur_pt)
            if self.aligned == False:
                if i%2 == 1:
                    shift_pts = []
                    for k in range(len(cur_pts)-1):
                        shift_pts.append(ghcomp.Division(ghcomp.Addition(cur_pts[k], cur_pts[k+1]),2))
                    cur_pts = shift_pts
            relation, _ = ghcomp.PointInCurve(cur_pts, self.boundary)
            cur_pts, _ = ghcomp.Dispatch(cur_pts, relation)
            if cur_pts:
                cur_pts = utils.construct_safe_pts_list(cur_pts)
                pts += cur_pts
                bound_pts.append(cur_pts[0])
        return dest_pts, pts, bound_pts
    
    def generate_grid_pts(self):
        pts = []
        bound_pts = []
        uplength = ghcomp.Length(self.upline)
        num = int(math.floor(uplength/self.horizontal)+1)
        up_pts, _, _ = ghcomp.DivideCurve(self.upline, num, False)
        mid_pts, um_pts, um_bound = self._generate_grid_pts(up_pts, self.vertical, self.midline)
        if self.downline:
            down_pts, md_pts, md_bound = self._generate_grid_pts(mid_pts, self.vertical, self.downline)
        
        bound_pts += um_bound
        if self.downline:
            bound_pts += md_bound
        bound_pts, _ = ghcomp.DeleteConsecutive(bound_pts, False)
        #relation, _ = ghcomp.PointInCurve(bound_pts, self.boundary)
        #bound_pts, _ = ghcomp.Dispatch(bound_pts, relation)
        pts += up_pts
        pts += mid_pts
        if self.downline:
            pts += down_pts
        
        relation, _ = ghcomp.PointInCurve(pts, self.boundary)
        
        pts, _ = ghcomp.Dispatch(pts, relation)
        
        pts += um_pts
        #self.display.AddCircle(pts, self.display_color, 1, 1.2)
        
        #for i in range(len(pts)):
            #self.display.AddCircle(rc.Geometry.Circle(pts[i],0.5),self.display_color,1)
        if self.downline:
            pts += md_pts
        return pts, bound_pts
        
    def generate_bound_pts(self, head_pts, pts):
        tolerance = 0.1
        
        unit_length = 1
        if self.aligned == False:
            unit_length = math.sqrt(0.25*self.horizontal*self.horizontal+self.vertical*self.vertical)
        else:
            unit_length = math.sqrt(self.horizontal*self.horizontal+self.vertical*self.vertical)
            
        num = int(math.floor(ghcomp.Length(self.split_crv)/unit_length)+1)
        aux_pts, _, _ = ghcomp.DivideCurve(self.split_crv, 3*num, False)
        aux_bound_pts, _, _ = ghcomp.ClosestPoint(aux_pts, pts)
        aux_bound_pts, _ = ghcomp.DeleteConsecutive(aux_bound_pts, False)
        
        _, anchor, _ = ghcomp.Deconstruct(aux_bound_pts[0])
        bound_pts = []
        for i in range(len(head_pts)):
            cur_pt = head_pts[i]
            _, cur_y, _ = ghcomp.Deconstruct(cur_pt)
            if cur_y <= anchor:
                bound_pts.append(cur_pt)
        
        head_pts = bound_pts
        bound_pts = []
        i=0
        j=0
        pre_pt = head_pts[0]
        while i<len(head_pts) and j<len(aux_bound_pts):
            cur_head = head_pts[i]
            cur_aux = aux_bound_pts[j]
            if ghcomp.Distance(cur_head, cur_aux)<tolerance:
                bound_pts.append(cur_head)
                pre_pt = cur_head
                i += 1
                j += 1
            else:
                dis_head = ghcomp.Distance(cur_head, pre_pt)
                dis_aux = ghcomp.Distance(cur_aux, pre_pt)
                if dis_head < dis_aux:
                    bound_pts.append(cur_head)
                    i += 1
                    pre_pt = cur_head
                else:
                    bound_pts.append(cur_aux)
                    j += 1
                    pre_pt = cur_aux
                    
        if i!=len(head_pts):
            for k in range(i, len(head_pts)):
                bound_pts.append(head_pts[k])
        if j!=len(aux_pts):
            for k in range(j, len(aux_bound_pts)):
                bound_pts.append(aux_bound_pts[k])
            
        i=1
        count = len(bound_pts)
        while i<count-1:
            pre_pt = bound_pts[i-1]
            cur_pt = bound_pts[i]
            suc_pt = bound_pts[i+1]
            _, pre_y, _ = ghcomp.Deconstruct(pre_pt)
            _, cur_y, _ = ghcomp.Deconstruct(cur_pt)
            _, suc_y, _ = ghcomp.Deconstruct(suc_pt)
            if cur_y>pre_y and cur_y>suc_y:
                bound_pts.pop(i)
                count -= 1
                continue
            i += 1
        return bound_pts
    
    def ifright(self, pt1, pt2):
        right = False
        x1, y1, z1 = ghcomp.Deconstruct(pt1)
        x2, y2, z2 = ghcomp.Deconstruct(pt2)
        #if ghcomp.Absolute(x2-x1-horizontal) < tolerance:
        if ghcomp.Absolute(y1-y2) < self.tolerance:
            right = True
        return right
    
    def ifdown(self, pt1, pt2):
        down = False
        x1, y1, z1 = ghcomp.Deconstruct(pt1)
        x2, y2, z2 = ghcomp.Deconstruct(pt2)
        #if ghcomp.Absolute(y1-y2-vertical) < tolerance:
        if ghcomp.Absolute(x1-x2) < self.tolerance:
            down = True
        return down
    
    def generate_white_direc(self, white_pts):
        white_direc = []
        for i in range(len(white_pts)):
            cur_pt = white_pts[i]
            _, t1, d1 = ghcomp.CurveClosestPoint(cur_pt, self.upline)
            std_pt, t2, d2 = ghcomp.CurveClosestPoint(cur_pt, self.midline)
            _, t3, d3 = ghcomp.CurveClosestPoint(cur_pt, self.downline)
            _, cur_y, _ = ghcomp.Deconstruct(cur_pt)
            _, std_y, _ = ghcomp.Deconstruct(std_pt)
            cur_direc = ghcomp.VectorXYZ(-1, 0, 0)
            if cur_y > std_y:
                _, tgt1, _ = ghcomp.EvaluateCurve(self.upline, t1)
                _, tgt2, _ = ghcomp.EvaluateCurve(self.midline, t2)
                cur_direc = ghcomp.Addition(ghcomp.Multiplication(tgt1, d2/(d1+d2)),ghcomp.Multiplication(tgt2, d1/(d1+d2)))
            elif cur_y < std_y:
                _, tgt2, _ = ghcomp.EvaluateCurve(self.midline, t2)
                _, tgt3, _ = ghcomp.EvaluateCurve(self.downline, t3)
                cur_direc = ghcomp.Addition(ghcomp.Multiplication(tgt2, d3/(d2+d3)),ghcomp.Multiplication(tgt3, d2/(d2+d3)))
            else:
                cur_direc = tgt2
            white_direc.append(cur_direc)
        return white_direc
    
    def generate_black_pts(self, white_pts, white_direc, upline):
        
        horizontal = self.horizontal
        if self.aligned == False:
            horizontal = horizontal/2
            
        black_pts = []
        black_direc = []
        for i in range(len(white_pts)):
            cur_pt = white_pts[i]
            cur_direc = white_direc[i]
            black_direc.append(cur_direc)
            """
            pt_ori, t, _ = ghcomp.CurveClosestPoint(cur_pt, upline)
            _, direc_ori, _ = ghcomp.EvaluateCurve(upline, t)
            
            aux_line = ghcomp.LineSDL(pt_ori, ghcomp.Multiplication(-1, direc_ori), self.horizontal)
            _, black_pt_ori = ghcomp.EndPoints(aux_line)
            """
            cur_line = ghcomp.LineSDL(cur_pt, ghcomp.Multiplication(-1, cur_direc), horizontal)
            #cur_black_pt, _, _ = ghcomp.CurveClosestPoint(black_pt_ori, cur_line)
            _, cur_black_pt = ghcomp.EndPoints(cur_line)
            black_pts.append(cur_black_pt)
        return black_pts, black_direc
    
    def generate_seq(self, white_pts, black_pts, white_direc, black_direc):
        seq_pts = []
        seq_direc = []
        pre_pt = white_pts[0]
        
        for i in range(len(white_pts)):
            cur_white = white_pts[i]
            cur_black = black_pts[i]
            if i==0:
                seq_pts.append(cur_black)
                seq_direc.append(black_direc[i])
                seq_pts.append(cur_white)
                seq_direc.append(white_direc[i])
                pre_pt = cur_white
            else:
                if self.ifdown(pre_pt, cur_black):
                    seq_pts.append(cur_black)
                    seq_direc.append(black_direc[i])
                    seq_pts.append(cur_white)
                    seq_direc.append(white_direc[i])
                    pre_pt = cur_white
                elif self.ifright(pre_pt, cur_black):
                    seq_pts.append(cur_black)
                    seq_direc.append(black_direc[i])
                    seq_pts.append(cur_white)
                    seq_direc.append(white_direc[i])
                    pre_pt = cur_white
                else:
                    seq_pts.pop(-1)
                    seq_direc.pop(-1)
                    seq_pts.append(cur_white)
                    seq_direc.append(white_direc[i])
                    pre_pt = cur_white
                    
        return seq_pts, seq_direc
    
    def generate_rect(self, center_pts, ks, r, n, pattern = None):
        sr = r
        lr = sr
        #默认圆角矩形的边方向为逆时针（黑），白色则为顺时针
        bound_crv = []
        rect_crv = []
        #TODO: modify line to nurbscurve
        
        #k = k/2
        #ang, _ = ghcomp.Angle(ghcomp.UnitY(-1), n)
        
        for i in range(len(center_pts)):
            k = ks[i]/2
            cur_rect = {}
            cur_pt = center_pts[i]
            x = cur_pt.X
            y = cur_pt.Y
            z = cur_pt.Z
            cur_n = n[i]
            #cur_ang = ang[i]
            #if n[i].X < 0:
            #    cur_ang = -cur_ang
            
            std_vec = ghcomp.UnitX(1)
            
            luarc_ct = ghcomp.ConstructPoint(x-k+r, y+k-r, 0)
            lu_angle = ghcomp.ConstructDomain(ghcomp.Pi(0.5), ghcomp.Pi(1))
            luarc, _ = ghcomp.Arc(ghcomp.XYPlane(luarc_ct), r, lu_angle)
            luarc = rg.NurbsCurve.CreateFromArc(luarc)
            luarc, _ = ghcomp.RotateDirection(luarc, cur_pt, std_vec, cur_n)
            #luarc, _ = ghcomp.Rotate(luarc, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                luarc, _ = ghcomp.FlipCurve(luarc)
            bound_crv.append(luarc)
            cur_rect['lu'] = luarc
            
            up_l = ghcomp.ConstructPoint(x-k+r, y+k, 0)
            up_r = ghcomp.ConstructPoint(x+k-r, y+k, 0)
            up_crv = ghcomp.Line(up_r, up_l)
            up_crv = rg.NurbsCurve.CreateFromLine(up_crv)
            up_crv, _ = ghcomp.RotateDirection(up_crv, cur_pt, std_vec, cur_n)
            #up_crv, _ = ghcomp.Rotate(up_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                up_crv, _ = ghcomp.FlipCurve(up_crv)
            bound_crv.append(up_crv)
            cur_rect['up'] = up_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(up_crv, luarc), True)
            
            ruarc_ct = ghcomp.ConstructPoint(x+k-r, y+k-r, 0)
            ru_angle = ghcomp.ConstructDomain(ghcomp.Pi(0), ghcomp.Pi(0.5))
            ruarc, _ = ghcomp.Arc(ghcomp.XYPlane(ruarc_ct), r, ru_angle)
            ruarc = rg.NurbsCurve.CreateFromArc(ruarc)
            ruarc, _ = ghcomp.RotateDirection(ruarc, cur_pt, std_vec, cur_n)
            #ruarc, _ = ghcomp.Rotate(ruarc, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                ruarc, _ = ghcomp.FlipCurve(ruarc)
            bound_crv.append(ruarc)
            cur_rect['ru'] = ruarc
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(ruarc, rec_crv), True)
            
            right_u = ghcomp.ConstructPoint(x+k, y+k-r, 0)
            r = sr
            right_b = ghcomp.ConstructPoint(x+k, y-k+r, 0)
            right_crv = ghcomp.Line(right_b, right_u)
            right_crv = rg.NurbsCurve.CreateFromLine(right_crv)
            right_crv, _ = ghcomp.RotateDirection(right_crv, cur_pt, std_vec, cur_n)
            #right_crv, _ = ghcomp.Rotate(right_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                right_crv, _ = ghcomp.FlipCurve(right_crv)
            bound_crv.append(right_crv)
            cur_rect['right'] = right_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(right_crv, rec_crv), True)
            
            rbarc_ct = ghcomp.ConstructPoint(x+k-r, y-k+r, 0)
            rb_angle = ghcomp.ConstructDomain(ghcomp.Pi(-0.5), ghcomp.Pi(0))
            rbarc, _ = ghcomp.Arc(ghcomp.XYPlane(rbarc_ct), r, rb_angle)
            rbarc = rg.NurbsCurve.CreateFromArc(rbarc)
            rbarc, _ = ghcomp.RotateDirection(rbarc, cur_pt, std_vec, cur_n)
            #rbarc, _ = ghcomp.Rotate(rbarc, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                rbarc, _ = ghcomp.FlipCurve(rbarc)
            bound_crv.append(rbarc)
            cur_rect['rb'] = rbarc
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(rbarc, rec_crv), True)
            
            bottom_r = ghcomp.ConstructPoint(x+k-r, y-k, 0)
            bottom_l = ghcomp.ConstructPoint(x-k+r, y-k, 0)
            bottom_crv = ghcomp.Line(bottom_l, bottom_r)
            bottom_crv = rg.NurbsCurve.CreateFromLine(bottom_crv)
            bottom_crv, _ = ghcomp.RotateDirection(bottom_crv, cur_pt, std_vec, cur_n)
            #bottom_crv, _ = ghcomp.Rotate(bottom_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                bottom_crv, _ = ghcomp.FlipCurve(bottom_crv)
            bound_crv.append(bottom_crv)
            cur_rect['bottom'] = bottom_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(bottom_crv, rec_crv), True)
            
            lbarc_ct = ghcomp.ConstructPoint(x-k+r, y-k+r, 0)
            lb_angle = ghcomp.ConstructDomain(ghcomp.Pi(-1), ghcomp.Pi(-0.5))
            lbarc, _ = ghcomp.Arc(ghcomp.XYPlane(lbarc_ct), r, lb_angle)
            lbarc = rg.NurbsCurve.CreateFromArc(lbarc)
            lbarc, _ = ghcomp.RotateDirection(lbarc, cur_pt, std_vec, cur_n)
            #lbarc, _ = ghcomp.Rotate(lbarc, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                lbarc, _ = ghcomp.FlipCurve(lbarc)
            bound_crv.append(lbarc)
            cur_rect['lb'] = lbarc
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(lbarc, rec_crv), True)
            
            left_b = ghcomp.ConstructPoint(x-k, y-k+r, 0)
            left_u = ghcomp.ConstructPoint(x-k, y+k-r, 0)
            left_crv = ghcomp.Line(left_u, left_b)
            left_crv = rg.NurbsCurve.CreateFromLine(left_crv)
            left_crv, _ = ghcomp.RotateDirection(left_crv, cur_pt, std_vec, cur_n)
            #left_crv, _ = ghcomp.Rotate(left_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                left_crv, _ = ghcomp.FlipCurve(left_crv)
            bound_crv.append(left_crv)
            cur_rect['left'] = left_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(left_crv, rec_crv), True)
            
            seamptl, seamptr = ghcomp.EndPoints(bottom_crv)
            #seampt = ghcomp.Division(ghcomp.Addition(seamptl, seamptr), 2)
            _, seamt, _ = ghcomp.CurveClosestPoint(seamptl, rec_crv)
            rec_crvl = ghcomp.Seam(rec_crv, seamt)
            cur_rect['rect'] = rec_crvl
            _, seamt, _ = ghcomp.CurveClosestPoint(seamptr, rec_crv)
            rec_crvr = ghcomp.Seam(rec_crv, seamt)
            cur_rect['rect2'] = rec_crvr
            
            rect_crv.append(cur_rect)
        
        return bound_crv, rect_crv
    
    def generate_h_link(self, rect1, rect2):
        crv1 = rect1['right']
        crv2 = rect2['left']
        link = ghcomp.TweenCurve(crv1, crv2, 0.5)
        return link
        
    def generate_v_link(self, rect1, rect2):
        crv1 = rect1['bottom']
        crv2 = rect2['up']
        link = ghcomp.TweenCurve(crv1, crv2, 0.5)
        return link
    
    def separate_pts(self, seq_pts, seq_direc):
        #data structure: 类似 dictionary
        #list[0]为当前类型的tag
        """ e.g. 
        [['slope', pts],
        ['cross', pts],
        ['slope', pts]]
        """
        
        slope_pts = []
        cross_pts = []
        slope_direcs = []
        cross_direcs = []
        
        pts = []
        direcs = []
        
        pre_type = None
        temp_head = None
        
        for i in range(len(seq_pts)):
            cur_pt = seq_pts[i]
            
            if i!=0:
                pre_pt = seq_pts[i-1]
                if self.ifright(pre_pt, cur_pt):
                    cross_pts.append(cur_pt)
                    cross_direcs.append(seq_direc[i])
                    if len(cross_pts) > 3:
                        if len(slope_pts) != 0:
                            temp_head = (cross_pts[0], cross_direcs[0])
                            #slope_pts.append(cross_pts[0])
                            #slope_direcs.append(cross_direcs[0])
                            cross_pts.insert(0, slope_pts[-1])
                            cross_direcs.insert(0, slope_direcs[-1])
                            slope_pts.append(temp_head[0])
                            slope_direcs.append(temp_head[1])
                            temp_head = None
                            pre_seq = ['slope', slope_pts]
                            pts.append(pre_seq)
                            direcs.append(slope_direcs)
                            slope_pts = []
                            slope_direcs = []
                            pre_type = 'slope'
                    
                else:
                    if len(cross_pts) > 10:
                        if pre_type == 'cross' and temp_head!=None:
                            cross_pts.insert(0, temp_head[0])
                            cross_direcs.insert(0, temp_head[1])
                            temp_head = None
                        pre_seq = ['cross', cross_pts]
                        pts.append(pre_seq)
                        direcs.append(cross_direcs)
                        pre_type = 'cross'
                        #slope_pts.pop()
                        #slope_direcs.pop()
                        temp_head = (cur_pt, seq_direc[i])
                    else:
                        slope_pts += cross_pts
                        slope_direcs += cross_direcs
                        slope_pts.append(cur_pt)
                        slope_direcs.append(seq_direc[i])
                    cross_pts = []
                    cross_direcs = []
            
            if i==len(seq_pts)-1:
                if len(slope_pts) != 0:
                    cur_seq = ['slope', slope_pts]
                    pts.append(cur_seq)
                    direcs.append(slope_direcs)
                    slope_pts = []
                    slope_direcs = []
                if len(cross_pts) != 0:
                    if pre_type == 'cross' and temp_head!=None:
                        cross_pts.insert(0, temp_head[0])
                        cross_direcs.insert(0, temp_head[1])
                        temp_head = None
                    cur_seq = ['cross', cross_pts]
                    pts.append(cur_seq)
                    direcs.append(cross_direcs)
                    cross_pts = []
                    cross_direcs = []
                
        return pts, direcs
    
    def generate_bound(self, seq_pts, seq_direc):
        white_rect = []
        black_rect = []
        bound_crv = []
        
        black_emu = ['lu', 'left', 'lb', 'bottom', 'rb', 'right', 'ru', 'up']
        white_emu = ['lu', 'up', 'ru', 'right', 'rb', 'bottom', 'lb', 'left']
        
        odd_even = ghcomp.Merge(0,1)
        white_pts, black_pts = ghcomp.Dispatch(seq_pts, odd_even)
        white_n, black_n = ghcomp.Dispatch(seq_direc, odd_even)
        
        white_ks = []
        black_ks = []
        
        white_seq_pts, _ = self.separate_pts(white_pts, white_n)
        for i in range(len(white_seq_pts)):
            cur_seq = white_seq_pts[i]
            if cur_seq[0] == 'slope':
                for j in range(len(cur_seq[1])):
                    white_ks.append(1.15)
            else:
                for j in range(len(cur_seq[1])):
                    white_ks.append(1.15)
        
        for i in range(len(black_pts)):
            black_ks.append(1.13)
        
        white_bound, white_rect = self.generate_rect(white_pts, white_ks, 0.2, white_n, pattern = "white")
        black_bound, black_rect = self.generate_rect(black_pts, black_ks, 0.2, black_n, pattern = "black")
        
        pre_pt = white_pts[0]
        link_crv = []
        for i in range(len(white_pts)):
            cur_black = black_pts[i]
            cur_white = white_pts[i]
            cur_white_rect = white_rect[i]
            cur_black_rect = black_rect[i]
            
            if i!=0:
                pre_white_rect = white_rect[i-1]
                if self.ifright(pre_pt, cur_black):
                    link_crv.append(self.generate_h_link(pre_white_rect, cur_black_rect))
                    pre_white_rect['end'] = 'ru'
                    cur_black_rect['start'] = 'lb'
                elif self.ifdown(pre_pt, cur_black):
                    link_crv.append(self.generate_v_link(pre_white_rect, cur_black_rect))
                    pre_white_rect['end'] = 'rb'
                    cur_black_rect['start'] = 'lu'
            else:
                cur_black_rect['start']='left'
                
            if self.ifright(cur_black, cur_white):
                link_crv.append(self.generate_h_link(cur_black_rect, cur_white_rect))
                cur_black_rect['end'] = 'rb'
                cur_white_rect['start'] = 'lu'
            elif self.ifdown(cur_black, cur_white):
                link_crv.append(self.generate_v_link(cur_black_rect, cur_white_rect))
                cur_black_rect['end'] = 'lb'
                cur_white_rect['start'] = 'ru'
            
            if i == len(white_pts)-1:
                cur_white_rect['end'] = 'right'
            
            pre_pt = cur_white
        
        for i in range(len(white_pts)):
            cur_black_rect = black_rect[i]
            cur_white_rect = white_rect[i]
            
            flag = False
            for k in black_emu:
                if k==cur_black_rect['start']:
                    flag = True
                if flag == True:
                    link_crv.append(cur_black_rect[k])
                if k==cur_black_rect['end']:
                    flag = False
                    break
            
            for k in white_emu:
                if k==cur_white_rect['start']:
                    flag = True
                if flag == True:
                    link_crv.append(cur_white_rect[k])
                if k==cur_white_rect['end']:
                    break
        
        bound_crv += white_bound
        bound_crv += black_bound
        
        link_crv = rg.Curve.JoinCurves(link_crv, 0.5, True)
        
        return bound_crv, link_crv, black_pts, black_n
    
    def generate_cross_band(self, cross_pts, edge_crv):
        #todo：用tweencrv进行offset
        cross_band = []
        shift_pts = []
        for i in range(len(cross_pts)-1):
            shift_pts.append(ghcomp.Division(ghcomp.Addition(cross_pts[i] + cross_pts[i+1]), 2))
        k0 = 1.15
        h1 = 0.595 + k0/2
        h2 = 1.725 + k0/2
        h3 = 3.165 + k0/2
        k1 = 1.13
        sr1 = 0.2
        r2 = 1.11/2
        r3 = 1.03/2
        
        std_crv = ghcomp.PolyLine(cross_pts, False)
        
        real_pts, _, dis = ghcomp.CurveClosestPoint(cross_pts, edge_crv)
        real_dis = ghcomp.Average(dis)
        factor = real_dis/(h3+r3)
        
        real_factor = ghcomp.Division(dis, h3+r3)
        
        des_crv = ghcomp.PolyLine(real_pts, False)
        
        #crv1 = ghcomp.TweenCurve(std_crv, des_crv, h1/(h3+r3))
        crv1 = ghcomp.OffsetCurve(std_crv, h1, ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), 1)
        band_pts1, t1, _ = ghcomp.CurveClosestPoint(shift_pts, crv1)
        _, tgt1, _ = ghcomp.EvaluateCurve(crv1, t1)
        ks1 = []
        for i in range(len(band_pts1)):
            ks1.append(k1)
        _, band_rect1 = self.generate_rect(band_pts1, ks1, sr1, tgt1, pattern = "black")
        for i in range(len(band_rect1)):
            cross_band.append(band_rect1[i]['rect'])
        
        crv21 = ghcomp.OffsetCurve(std_crv, h2, ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), 1)
        band_pts21, _, _ = ghcomp.CurveClosestPoint(cross_pts, crv21)
        crv22 = ghcomp.TweenCurve(std_crv, des_crv, h2/(h3+r3))
        band_pts22, _, _ = ghcomp.CurveClosestPoint(cross_pts, crv22)
        num = len(band_pts21)
        band_pts2 = []
        for i in range(num):
            cur_pt = ghcomp.Addition(ghcomp.Multiplication(band_pts21[i], 1.0*(num-i)/num), ghcomp.Multiplication(band_pts22[i], 1.0*i/num))
            
            band_pts2.append(cur_pt)
        
        crv3 = ghcomp.TweenCurve(std_crv, des_crv, h3/(h3+r3))
        band_pts3, _, _ = ghcomp.CurveClosestPoint(shift_pts, crv3)

        circle_band = []
        circle_band += ghcomp.Circle(band_pts2, ghcomp.Multiplication(real_factor, r2))
        circle_band += ghcomp.Circle(band_pts3, ghcomp.Multiplication(real_factor, r3))
        for i in range(len(circle_band)): 
            circle_band[i] = rg.NurbsCurve.CreateFromCircle(circle_band[i])
        
        cross_band += circle_band    
        return cross_band
    
    def generate_slope_band(self, slope_pts, h_direcs, edge_crv):
        slope_band = []
        
        r0 = 0.55/2 #装饰性圆点
        r1 = 0.825/2
        r2 = 1.11/2
        r3 = 1.15/2
        
        horizontal = self.horizontal
        if self.aligned == False:
            horizontal = horizontal/2
        
        unit_length = math.sqrt(horizontal*horizontal + self.vertical*self.vertical)
        threshold = 0.3
        
        for i in range(len(h_direcs)):
            cur_pt = slope_pts[i]
            #逆时针旋转45°
            line, _ = ghcomp.Rotate(ghcomp.LineSDL(cur_pt, h_direcs[i], 10), ghcomp.Pi(1.25), ghcomp.XYPlane(cur_pt))
            end_pt, _, _ = ghcomp.CurveXCurve(line, edge_crv)
            if end_pt:
                cur_direc, _ = ghcomp.Vector2Pt(cur_pt, end_pt, False)
                dist = ghcomp.Distance(cur_pt, end_pt)
                count = int(math.floor(dist/unit_length))
                cpst = dist - count * unit_length
                for j in range(count):
                    _, band_pt = ghcomp.EndPoints(ghcomp.LineSDL(cur_pt, cur_direc, unit_length*(j+1)))
                    if j==count-1:
                        if cpst > threshold * unit_length:
                            slope_band.append(ghcomp.Circle(band_pt, r1))
                        else:
                            _, cpst_pt = ghcomp.EndPoints(ghcomp.LineSDL(cur_pt, cur_direc, dist-r1))
                            slope_band.append(ghcomp.Circle(cpst_pt, r0))
                            
                    elif j==count-2:
                        slope_band.append(ghcomp.Circle(band_pt, r2))
                    else:
                        slope_band.append(ghcomp.Circle(band_pt, r3))
                        
                if cpst > (1-threshold) * unit_length:
                    _, cpst_pt = ghcomp.EndPoints(ghcomp.LineSDL(cur_pt, cur_direc, dist-r0))
                    slope_band.append(ghcomp.Circle(cpst_pt, r0))
        
        for i in range(len(slope_band)):
            slope_band[i] = rg.NurbsCurve.CreateFromCircle(slope_band[i])
        
        return slope_band
    
    def generate_black_band(self, bound_pts, bound_direcs):
        edge_crv = self.edge_crv
        
        black_band = []
        bug1 = []
        bug2 = []
        for i in range(len(bound_pts)):
            cur_seq = bound_pts[i]
            cur_type = cur_seq[0]
            if cur_type == "slope":
                cur_seq_pts = cur_seq[1]
                bug1 += cur_seq_pts
                cur_direcs = bound_direcs[i]
                black_band += self.generate_slope_band(cur_seq_pts, cur_direcs, edge_crv)
            elif cur_type == "cross":
                cur_seq_pts = cur_seq[1]
                bug2 += cur_seq_pts
                black_band += self.generate_cross_band(cur_seq_pts, edge_crv)
                
        #两部分点：斜向阵列和贴边装饰点
        #横向点直接遵照规则做offset和shift
        return black_band
        
    def bake(self):
        layer_name = 'fuyao_black'
        rs.AddLayer(layer_name, self.display_color, parent='fuyao_frits')
        for i in range(len(self.frit_black)):
            obj = scriptcontext.doc.Objects.AddCurve(self.frit_black[i])
            rs.ObjectLayer(obj, layer_name)
        
        layer_name = 'fuyao_white'
        rs.AddLayer(layer_name, self.display_color, parent='fuyao_frits')
        for i in range(len(self.frit_white)):
            obj = scriptcontext.doc.Objects.AddCurve(self.frit_white[i])
            rs.ObjectLayer(obj, layer_name)
        
        layer_name = 'fuyao_bound'
        rs.AddLayer(layer_name, self.display_color, parent='fuyao_frits')
        for i in range(len(self.frit_bound)):
            obj = scriptcontext.doc.Objects.AddCurve(self.frit_bound[i])
            rs.ObjectLayer(obj, layer_name)
    
    def run(self):
        pts, bound_pts = self.generate_grid_pts()
            
        white_pts = self.generate_bound_pts(head_pts = bound_pts, pts = pts)
        
        white_direc = self.generate_white_direc(white_pts)
        black_pts, black_direc = self.generate_black_pts(white_pts, white_direc, self.upline)
        seq_pts, seq_direc = self.generate_seq(white_pts, black_pts, white_direc, black_direc)
        
        bound_crv, link_crv, black_seq_pts, black_n = self.generate_bound(seq_pts, seq_direc)
        bound_pts, bound_direcs = self.separate_pts(black_seq_pts, black_n)
        black_band = self.generate_black_band(bound_pts, bound_direcs)
        
        for i in range(len(link_crv)):
            self.frit_bound.append(link_crv[i])
            #self.display.AddCurve(link_crv[i], self.display_color, 1)
        
        for i in range(len(black_band)):
            self.frit_black.append(black_band[i])
            #self.display.AddCurve(black_band[i],self.display_color,1)
        
        pat = ghcomp.Merge(True, False)
        _, white_list = ghcomp.Dispatch(seq_pts, pat)#OK
        _, Index_of_white, _ = ghcomp.ClosestPoint(white_list, pts)#OK
        
        #for i in range(len(Index_of_white)):
        #    print(Index_of_white[i])
        inner_of_holes = ghcomp.CullIndex(pts,Index_of_white,True)#OK.
        _, white_border, _ = ghcomp.ClosestPoint(seq_pts, inner_of_holes)#OK
        white_item = ghcomp.ListItem(inner_of_holes, white_border, True)#OK 222 values
        white_border_frit, _ = ghcomp.DeleteConsecutive(white_item, False)#OK 111 values
        
        for i in range(len(white_border_frit)):
            self.frit_white.append(rg.NurbsCurve.CreateFromCircle(rc.Geometry.Circle(white_border_frit[i],0.585)))
            #self.display.AddCircle(rc.Geometry.Circle(white_border_frit[i],0.585),self.display_color,1)
        
        #print(len(white_border_frit))
        #for i in range(len(white_border_frit)):
        #    print(white_border_frit[i])
        _, Index_boder_white, _ = ghcomp.ClosestPoint(white_border_frit, inner_of_holes)#OK 111 values
        white_hole_frit = ghcomp.CullIndex(inner_of_holes,Index_boder_white,True)#OK 3999 values
        #print(len(white_hole_frit))
        for i in range(len(white_hole_frit)):
            self.frit_white.append(rg.NurbsCurve.CreateFromCircle(rc.Geometry.Circle(white_hole_frit[i],0.5)))
            #self.display.AddCircle(rc.Geometry.Circle(white_hole_frit[i],0.5),self.display_color,1)
        
        self.bake()


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
    
    def dazhong_fill_dots(self):
        self.outer_crv = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.outer_crv, _ = ghcomp.FlipCurve(self.outer_crv)
            
        self.inner_crv = self.region.curves[1]
        if self.region.is_flip[1] == True:
            self.inner_crv, _ = ghcomp.FlipCurve(self.inner_crv)
            
        self.refer_crv = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.refer_crv, _ = ghcomp.FlipCurve(self.refer_crv)
            
        self.top_crv = self.region.curves[3]
        if self.region.is_flip[3] == True:
            self.top_crv, _ = ghcomp.FlipCurve(self.top_crv)
            
        self.bottom_crv = self.region.curves[4]
        if self.region.is_flip[4] == True:
            self.bottom_crv, _ = ghcomp.FlipCurve(self.bottom_crv)
            
        self.bottom1_crv = self.region.curves[5]
        if self.region.is_flip[5] == True:
            self.bottom1_crv, _ = ghcomp.FlipCurve(self.bottom1_crv)
            
        #offset outer_crv
        #self.display_color = rc.Display.ColorHSL(0, 1, 0)
        #self.display = rc.Display.CustomDisplay(True)
        #self.display.Clear()
        
        crv1 = ghcomp.OffsetCurve(self.outer_crv, distance= 2.4, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), corners=1)
        blocksrf = ghcomp.RuledSurface(crv1, self.refer_crv)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        #self.display.AddCurve(blockborder, self.display_color, 1)
        boundary_crv = ghcomp.OffsetCurve(blockborder,  plane = rs.WorldXYPlane(),distance=-0.1, corners=1)
        #self.display.AddCurve(boundary_crv, self.display_color, 1)
        upline_crv = ghcomp.OffsetCurve(self.top_crv, plane = rs.WorldXYPlane(), distance=0.5, corners=1)
        
        dazhong_frit_generator = Dazhong_fill_holes(\
                                    upline = upline_crv, midline = self.bottom_crv, downline = self.bottom1_crv, \
                                    boundary = boundary_crv, split_crv = self.refer_crv, edge_crv = self.inner_crv, \
                                    horizontal = 2.4, vertical = 1.2, aligned = False)
        dazhong_frit_generator.run()
        
        
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
       