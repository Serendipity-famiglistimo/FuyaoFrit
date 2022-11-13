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
    def __init__(self,upline, midline, downline, boundary, horizontal, vertical, aligned = False):
        self.upline = upline
        self.midline = midline
        self.downline = downline
        self.boundary = boundary
        self.horizontal = horizontal
        self.vertical = vertical
        self.aligned = aligned
        
    def construct_safe_pts_list(self,pts):
        #[x,y,z]to[pt]
        if len(pts)==3:
            try:
                if pts[2]==0:
                    new_pts = []
                    pt = ghcomp.ConstructPoint(pts[0], pts[1], pts[2])
                    new_pts.append(pt)
                    return new_pts
            except:
                return pts
        return pts
    
    def generate_grid_pts(self,base_pts, vertical, downline):
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
                cur_pts = self.construct_safe_pts_list(cur_pts)
                pts += cur_pts
                bound_pts.append(cur_pts[0])
        return dest_pts, pts, bound_pts
    
    def run(self):
        pts = []
        bound_pts = []
        uplength = ghcomp.Length(self.upline)
        num = int(math.floor(uplength/self.horizontal)+1)
        up_pts, _, _ = ghcomp.DivideCurve(self.upline, num, False)
        mid_pts, um_pts, um_bound = self.generate_grid_pts(up_pts, self.vertical, self.midline)
        if self.downline:
            down_pts, md_pts, md_bound = self.generate_grid_pts(mid_pts, self.vertical, self.downline)
        
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
        print(len(um_pts))
        relation, _ = ghcomp.PointInCurve(pts, self.boundary)
        #print(relation)
        pts, _ = ghcomp.Dispatch(pts, relation)
        #print(len(pts))
        pts += um_pts
        #self.display.AddCircle(pts, self.display_color, 1, 1.2)
        print(len(pts))
        #for i in range(len(pts)):
            #self.display.AddCircle(rc.Geometry.Circle(pts[i],0.5),self.display_color,1)
        if self.downline:
            pts += md_pts
        return pts, bound_pts 


class Edge_of_holes:
    def __init__(self,head_pts, pts, split_crv):
        self.head_pts = head_pts
        self.pts = pts
        self.split_crv = split_crv
        self.tolerance = 0.1
        self.horizontal = 2.4
        self.vertical = 1.2
        self.aligned = False
        self.unit_length = 1
    
    def run(self):
        if self.aligned == False:
            self.unit_length = math.sqrt(0.25*self.horizontal*self.horizontal+self.vertical*self.vertical)
        else:
            self.unit_length = math.sqrt(self.horizontal*self.horizontal+self.vertical*self.vertical)
        
        num = int(math.floor(ghcomp.Length(self.split_crv)/self.unit_length)+1)
        aux_pts, _, _ = ghcomp.DivideCurve(self.split_crv, 3*num, False)
        aux_bound_pts, _, _ = ghcomp.ClosestPoint(aux_pts, self.pts)
        aux_bound_pts, _ = ghcomp.DeleteConsecutive(aux_bound_pts, False)
        
        _, anchor, _ = ghcomp.Deconstruct(aux_bound_pts[0])
        bound_pts = []
        for i in range(len(self.head_pts)):
            cur_pt = self.head_pts[i]
            _, cur_y, _ = ghcomp.Deconstruct(cur_pt)
            if cur_y <= anchor:
                bound_pts.append(cur_pt)
        
        self.head_pts = bound_pts
        bound_pts = []
        i=0
        j=0
        pre_pt = self.head_pts[0]
        while i<len(self.head_pts) and j<len(aux_bound_pts):
            cur_head = self.head_pts[i]
            cur_aux = aux_bound_pts[j]
            if ghcomp.Distance(cur_head, cur_aux)<self.tolerance:
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
                    
        if i!=len(self.head_pts):
            for k in range(i, len(self.head_pts)):
                bound_pts.append(self.head_pts[k])
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


class Black_white_transit:
    def __init__(self, white_pts, upline, midline, downline, edge_crv):
        self.white_pts = white_pts
        self.upline = upline
        self.midline = midline
        self.downline = downline
        self.edge_crv = edge_crv
        self.tolerance = 0.5
        self.horizontal = 2.4
        self.vertical = 1.2
        self.aligned = False

        self.display_color = rc.Display.ColorHSL(0, 1, 0)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()

        if self.aligned == False:
            self.horizontal = self.horizontal/2
        
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
            cur_line = ghcomp.LineSDL(cur_pt, ghcomp.Multiplication(-1, cur_direc), self.horizontal)
            #cur_black_pt, _, _ = ghcomp.CurveClosestPoint(black_pt_ori, cur_line)
            _, cur_black_pt = ghcomp.EndPoints(cur_line)
            black_pts.append(cur_black_pt)
        return black_pts, black_direc
    
    def generate_seq(self, white_pts, black_pts,white_direc,black_direc):
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
        #print(factor)
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
            print(band_pts21[i], band_pts22[i], cur_pt)
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
        r3 = 1.13/2
        
        unit_length = math.sqrt(self.horizontal*self.horizontal + self.vertical*self.vertical)
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
    
    def generate_black_band(self, bound_pts, bound_direcs, edge_crv):
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
    
    def run(self):
        white_direc = self.generate_white_direc(self.white_pts)
        black_pts, black_direc = self.generate_black_pts(self.white_pts, white_direc, self.upline)
        seq_pts, seq_direc = self.generate_seq(self.white_pts, black_pts,white_direc,black_direc)
        #print(seq_pts)
        bound_crv, link_crv, black_seq_pts, black_n = self.generate_bound(seq_pts, seq_direc)
        bound_pts, bound_direcs = self.separate_pts(black_seq_pts, black_n)
        black_band = self.generate_black_band(bound_pts, bound_direcs, self.edge_crv)
        
        for i in range(len(link_crv)):
            print(link_crv[i])
            self.display.AddCurve(link_crv[i], self.display_color, 1)
        for i in range(len(black_band)):
            self.display.AddCurve(black_band[i],self.display_color,1)
        return seq_pts,link_crv,black_band


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
            
        self.reffer_crv = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.reffer_crv, _ = ghcomp.FlipCurve(self.reffer_crv)
            
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
        self.display_color = rc.Display.ColorHSL(0, 1, 0)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
        crv1 = ghcomp.OffsetCurve(self.outer_crv, distance=2.4, corners=1)
        blocksrf = ghcomp.RuledSurface(crv1, self.reffer_crv)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        #self.display.AddCurve(blockborder, self.display_color, 1)
        boundary_crv = ghcomp.OffsetCurve(blockborder,  plane = rs.WorldXYPlane(),distance=-0.1, corners=1)
        self.display.AddCurve(boundary_crv, self.display_color, 1)
        upline_crv = ghcomp.OffsetCurve(self.top_crv, plane = rs.WorldXYPlane(), distance=0.5, corners=1)
        pts, bound_pts = Dazhong_fill_holes(upline = upline_crv, midline = self.bottom_crv, downline = self.bottom1_crv, boundary = boundary_crv, horizontal = 2.4, vertical = 1.2, aligned = False).run()
        bound_pts_white = Edge_of_holes(head_pts = bound_pts, pts = pts, split_crv = self.reffer_crv).run()
        transit_band,link,black_band = Black_white_transit(white_pts = bound_pts_white, upline = self.top_crv, midline = self.bottom_crv, downline = self.bottom1_crv, edge_crv = self.inner_crv).run()
        pat = ghcomp.Merge(True, False)
        _,white_list = ghcomp.Dispatch(transit_band,pat)#OK
        _, Index_of_white, _ = ghcomp.ClosestPoint(white_list, pts)#OK
        #for i in range(len(Index_of_white)):
        #    print(Index_of_white[i])
        inner_of_holes = ghcomp.CullIndex(pts,Index_of_white,True)#OK
        _,white_border,_ = ghcomp.ClosestPoint(transit_band, inner_of_holes)#OK
        white_item = ghcomp.ListItem(inner_of_holes,white_border, True)#OK 222 values
        white_border_frit,_ = ghcomp.DeleteConsecutive(white_item, False)#OK 111 values
        for i in range(len(white_border_frit)):
            self.display.AddCircle(rc.Geometry.Circle(white_border_frit[i],0.585),self.display_color,1)
        #print(len(white_border_frit))
        #for i in range(len(white_border_frit)):
        #    print(white_border_frit[i])
        _, Index_boder_white, _ = ghcomp.ClosestPoint(white_border_frit, inner_of_holes)#OK 111 values
        white_hole_frit = ghcomp.CullIndex(inner_of_holes,Index_boder_white,True)#OK 3999 values
        #print(len(white_hole_frit))
        for i in range(len(white_hole_frit)):
            self.display.AddCircle(rc.Geometry.Circle(white_hole_frit[i],0.5),self.display_color,1)
    
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
        self.fill_angle()
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
        
        
        self.display_color = rc.Display.ColorHSL(0, 1, 0)
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
       



    