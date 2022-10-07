#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Yawen Zheng
# @Date: Tuesday, September 20th 2022
# @Email: yvonnetsang16@gmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''

from utils import get_vec, generate_n, get_n_along_crv, crv_direc, construct_safe_pts_list
import Rhino.Geometry as rg
import Rhino as rc
import ghpythonlib.components as ghcomp

class Separatrix:
    def __init__(self, grid_direc, white_pts, white_k, white_sr, black_k, black_sr, r, white_base_crv, split_crv, black_base_crv):
        self.grid_direc = grid_direc
        self.white_pts = white_pts
        
        self.white_k = white_k
        self.white_sr = white_sr
        self.black_k = black_k
        self.black_sr = black_sr
        self.r = r
        self.lr = white_k-r-0.05
        
        self.white_base_crv = white_base_crv
        self.split_crv = split_crv
        self.black_base_crv = black_base_crv
        
        self.bound_crv = []
        self.rect_crv = []
        self.bug = []
    
    def separate_pts(self, white_pts):
        #data structure: 类似 dictionary
        #list[0]为当前类型的tag
        """ e.g. 
        [['slope', pts],
        ['transit', pts],
        ['cross', pts],
        ['transit', pts]]
        """
        
        pre_type = None
        cur_seq = []
        pts = []
        
        for i in range(len(white_pts)):
            cur_type = None
            cur_pt = white_pts[i]
            
            vec = ghcomp.VectorXYZ(0,0,0)
            if i != len(white_pts)-1:
                vec = ghcomp.Subtraction(white_pts[i+1], cur_pt)
            else:
                vec = ghcomp.Subtraction(cur_pt, white_pts[i-1])
                
            angle, _ = ghcomp.Angle(vec, ghcomp.UnitX(1))
            if ghcomp.Absolute(angle) > ghcomp.Pi(1/12):
                cur_type = 'slope'
            elif ghcomp.Absolute(angle) < ghcomp.Pi(1/48):
                cur_type = 'cross'
            else:
                cur_type = 'transit'
            
            if pre_type == cur_type:
                cur_seq.append(cur_pt)
                if i == len(white_pts)-1:
                    #if len(cur_seq) > 2:
                    pts.append(cur_seq)
            else:
                if pre_type != None:
                    #if len(cur_seq) > 2:
                    pts.append(cur_seq)
                cur_seq = []
                cur_seq.append(cur_type)
                cur_seq.append(cur_pt)
                pre_type = cur_type
        
        return pts

    def generate_rect(self, center_pts, k, r, n, pattern = None):
        sr = r
        lr = self.lr
        #圆角矩形的边方向为逆时针
        bound_crv = []
        rect_crv = []
        rot_center = []
        #TODO: modify line to nurbscurve
        
        k = k/2
        #ang, _ = ghcomp.Angle(ghcomp.UnitY(-1), n)
        
        for i in range(len(center_pts)):
            cur_rect = {}
            cur_pt = center_pts[i]
            x = cur_pt.X
            y = cur_pt.Y
            z = cur_pt.Z
            cur_n = n[i]
            #cur_ang = ang[i]
            #if n[i].X < 0:
            #    cur_ang = -cur_ang
            
            luarc_ct = ghcomp.ConstructPoint(x-k+r, y+k-r, 0)
            lu_angle = ghcomp.ConstructDomain(ghcomp.Pi(1/2), ghcomp.Pi(1))
            luarc, _ = ghcomp.Arc(ghcomp.XYPlane(luarc_ct), r, lu_angle)
            luarc = rg.NurbsCurve.CreateFromArc(luarc)
            luarc, _ = ghcomp.RotateDirection(luarc, cur_pt, ghcomp.UnitY(-1), cur_n)
            #luarc, _ = ghcomp.Rotate(luarc, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(luarc)
            cur_rect['lu'] = luarc
            
                
            up_l = ghcomp.ConstructPoint(x-k+r, y+k, 0)
            
            if pattern == 'white':
                r = lr
            up_r = ghcomp.ConstructPoint(x+k-r, y+k, 0)
            up_crv = ghcomp.Line(up_r, up_l)
            up_crv = rg.NurbsCurve.CreateFromLine(up_crv)
            up_crv, _ = ghcomp.RotateDirection(up_crv, cur_pt, ghcomp.UnitY(-1), cur_n)
            #up_crv, _ = ghcomp.Rotate(up_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(up_crv)
            cur_rect['up'] = up_crv
            
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(up_crv, luarc), True)
            
            ruarc_ct = ghcomp.ConstructPoint(x+k-r, y+k-r, 0)
            ru_angle = ghcomp.ConstructDomain(ghcomp.Pi(0), ghcomp.Pi(1/2))
            ruarc, _ = ghcomp.Arc(ghcomp.XYPlane(ruarc_ct), r, ru_angle)
            ruarc = rg.NurbsCurve.CreateFromArc(ruarc)
            ruarc, _ = ghcomp.RotateDirection(ruarc, cur_pt, ghcomp.UnitY(-1), cur_n)
            #ruarc, _ = ghcomp.Rotate(ruarc, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(ruarc)
            cur_rect['ru'] = ruarc
            
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(ruarc, rec_crv), True)
            
            right_u = ghcomp.ConstructPoint(x+k, y+k-r, 0)
            r = sr
            right_b = ghcomp.ConstructPoint(x+k, y-k+r, 0)
            right_crv = ghcomp.Line(right_b, right_u)
            right_crv = rg.NurbsCurve.CreateFromLine(right_crv)
            right_crv, _ = ghcomp.RotateDirection(right_crv, cur_pt, ghcomp.UnitY(-1), cur_n)
            #right_crv, _ = ghcomp.Rotate(right_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(right_crv)
            cur_rect['right'] = right_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(right_crv, rec_crv), True)
            
            rbarc_ct = ghcomp.ConstructPoint(x+k-r, y-k+r, 0)
            rb_angle = ghcomp.ConstructDomain(ghcomp.Pi(-1/2), ghcomp.Pi(0))
            rbarc, _ = ghcomp.Arc(ghcomp.XYPlane(rbarc_ct), r, rb_angle)
            rbarc = rg.NurbsCurve.CreateFromArc(rbarc)
            rbarc, _ = ghcomp.RotateDirection(rbarc, cur_pt, ghcomp.UnitY(-1), cur_n)
            #rbarc, _ = ghcomp.Rotate(rbarc, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(rbarc)
            cur_rect['rb'] = rbarc
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(rbarc, rec_crv), True)
            
            bottom_r = ghcomp.ConstructPoint(x+k-r, y-k, 0)
            if pattern == 'black':
                r = lr
            bottom_l = ghcomp.ConstructPoint(x-k+r, y-k, 0)
            bottom_crv = ghcomp.Line(bottom_l, bottom_r)
            bottom_crv = rg.NurbsCurve.CreateFromLine(bottom_crv)
            bottom_crv, _ = ghcomp.RotateDirection(bottom_crv, cur_pt, ghcomp.UnitY(-1), cur_n)
            #bottom_crv, _ = ghcomp.Rotate(bottom_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(bottom_crv)
            cur_rect['bottom'] = bottom_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(bottom_crv, rec_crv), True)
            
            lbarc_ct = ghcomp.ConstructPoint(x-k+r, y-k+r, 0)
            lb_angle = ghcomp.ConstructDomain(ghcomp.Pi(-1), ghcomp.Pi(-1/2))
            lbarc, _ = ghcomp.Arc(ghcomp.XYPlane(lbarc_ct), r, lb_angle)
            lbarc = rg.NurbsCurve.CreateFromArc(lbarc)
            lbarc, _ = ghcomp.RotateDirection(lbarc, cur_pt, ghcomp.UnitY(-1), cur_n)
            #lbarc, _ = ghcomp.Rotate(lbarc, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(lbarc)
            cur_rect['lb'] = lbarc
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(lbarc, rec_crv), True)
            
            left_b = ghcomp.ConstructPoint(x-k, y-k+r, 0)
            r = sr
            left_u = ghcomp.ConstructPoint(x-k, y+k-r, 0)
            left_crv = ghcomp.Line(left_u, left_b)
            left_crv = rg.NurbsCurve.CreateFromLine(left_crv)
            left_crv, _ = ghcomp.RotateDirection(left_crv, cur_pt, ghcomp.UnitY(-1), cur_n)
            #left_crv, _ = ghcomp.Rotate(left_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(left_crv)
            cur_rect['left'] = left_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(left_crv, rec_crv), True)
            
            seampt, _ = ghcomp.EndPoints(bottom_crv)
            _, seamt, _ = ghcomp.CurveClosestPoint(seampt, rec_crv)
            rec_crv = ghcomp.Seam(rec_crv, seamt)
            cur_rect['rect'] = rec_crv
            
            rect_crv.append(cur_rect)
        
        return bound_crv, rect_crv
    
    def _generate_slope_bound(self, white_rect, black_rect):
        bound_crv = []
        #TODO 需要区分左右边界，通过斜率进行选择
        for i in range(len(white_rect)):
            cur_white = white_rect[i]
            white_left = cur_white['left']
            if i==0:
                tail = []
                white_lb = cur_white['lb']
                lb_pt, _= ghcomp.EndPoints(white_lb)
                lb_plane, _ = ghcomp.RotateDirection(ghcomp.YZPlane(lb_pt), lb_pt, ghcomp.UnitY(-1), get_vec(white_left))
                white_lb, _ = ghcomp.Mirror(white_lb, lb_plane)
                tail.append(white_lb)
                tail.append(white_left)
                tail.append(cur_white['lu'])
                tail_crv = ghcomp.JoinCurves(tail, True)
                tail_crv = crv_direc(tail_crv)
                split_crv = self.split_crv
                _, t1, _ = ghcomp.CurveXCurve(tail_crv, split_crv)
                if t1:
                    _, cur_domain = ghcomp.CurveDomain(tail_crv)
                    _, t2 = ghcomp.DeconstructDomain(cur_domain)
                    bound_crv.append(ghcomp.SubCurve(tail_crv, ghcomp.ConstructDomain(t1, t2)))
                else:
                    bound_crv += tail
                
            white_up = cur_white['up']
            bound_crv.append(white_up)
            
            bound_crv.append(cur_white['ru'])
            
            white_right = cur_white['right']
            bound_crv.append(white_right)
            white_bottom = cur_white['bottom']
            
            if i!=0:
                pre_black = black_rect[i-1]
                pre_black_bottom = pre_black['bottom']
                pre_black_right = pre_black['right']
                white_left_flip, _ = ghcomp.FlipCurve(white_left)
                right_left = ghcomp.TweenCurve(pre_black_right, white_left_flip, 0.5)
                bound_crv.append(right_left)
                
                _, pre_link_black = ghcomp.EndPoints(pre_black_bottom)
                pre_link_mid, _ = ghcomp.EndPoints(right_left)
                linkv = ghcomp.Merge(pre_link_black, pre_link_mid)
                linkt = ghcomp.Merge(get_vec(pre_black_bottom), get_vec(right_left))
                pre_link1, _, _ = ghcomp.TangentCurve(linkv, linkt, 0.5, 3)
                bound_crv.append(pre_link1)
                
                _, pre_link_mid= ghcomp.EndPoints(right_left)
                _, pre_link_white = ghcomp.EndPoints(white_up)
                linkv = ghcomp.Merge(pre_link_mid, pre_link_white)
                linkt = ghcomp.Merge(get_vec(right_left), ghcomp.Multiplication(-1, get_vec(white_up)))
                pre_link2, _, _ = ghcomp.TangentCurve(linkv, linkt, 0.5, 3)
                bound_crv.append(pre_link2)
                
            if i!=len(white_rect)-1:
                cur_black = black_rect[i]
                black_up = cur_black['up']
                black_left = cur_black['left']
                white_bottom_flip, _ = ghcomp.FlipCurve(white_bottom)
                up_bottom = ghcomp.TweenCurve(black_up, white_bottom_flip, 0.5)
                bound_crv.append(up_bottom)
                
                bound_crv.append(black_left)
                bound_crv.append(cur_black['lb'])
                bound_crv.append(cur_black['bottom'])
               
                suc_link_white, _ = ghcomp.EndPoints(white_right)
                suc_link_mid, _ = ghcomp.EndPoints(up_bottom)
                linkv = ghcomp.Merge(suc_link_white, suc_link_mid)
                linkt = ghcomp.Merge(ghcomp.Multiplication(-1, get_vec(white_right)), get_vec(up_bottom))
                suc_link1, _, _ = ghcomp.TangentCurve(linkv, linkt, 0.5, 3)
                bound_crv.append(suc_link1)
                
                _, suc_link_mid= ghcomp.EndPoints(up_bottom)
                suc_link_black, _ = ghcomp.EndPoints(black_left)
                linkv = ghcomp.Merge(suc_link_mid, suc_link_black)
                linkt = ghcomp.Merge(get_vec(up_bottom), get_vec(black_left))
                suc_link2, _, _ = ghcomp.TangentCurve(linkv, linkt, 0.5, 3)
                bound_crv.append(suc_link2)
            
            else:
                tail = []
                tail.append(cur_white['rb'])
                white_bottom = cur_white['bottom']
                _, bottom_pt = ghcomp.EndPoints(white_bottom)
                white_k = self.white_k
                bottom_line = ghcomp.LineSDL(bottom_pt, ghcomp.Multiplication(-1, get_vec(white_bottom)), white_k)
                bottom_line = rg.NurbsCurve.CreateFromLine(bottom_line)
                tail.append(bottom_line)
                
                tail_crv = ghcomp.JoinCurves(tail, False)
                tail_crv = crv_direc(tail_crv)
                
                split_crv = self.split_crv
                _, t1, _ = ghcomp.CurveXCurve(tail_crv, split_crv)
                if t1:
                    _, cur_domain = ghcomp.CurveDomain(tail_crv)
                    _, t2 = ghcomp.DeconstructDomain(cur_domain)
                    bottom_crv = ghcomp.SubCurve(tail_crv, ghcomp.ConstructDomain(t1, t2))
                    bound_crv.append(bottom_crv)
                else:
                    bound_crv += tail
        bound_crv = ghcomp.JoinCurves(bound_crv, False)
        bound_crv = crv_direc(bound_crv)
        return bound_crv
    
    def generate_slope_bound(self, white_pts, grid_direc):
        black_pts = []
        black_n = []
        black_x = []
        black_y = []
        
        for i in range(len(white_pts)-1):
            cur_pt = white_pts[i]
            next_pt = white_pts[i+1]
            mid_pt = ghcomp.Division(ghcomp.Addition(cur_pt, next_pt),2)
            deltax = next_pt.X - cur_pt.X
            deltay = next_pt.Y- cur_pt.Y
            deltaz = next_pt.Z - cur_pt.Z
            tgt, _ = ghcomp.VectorXYZ(deltax, deltay, deltaz)
            normal, _ = ghcomp.Rotate(tgt, ghcomp.Pi(-1/2), ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)))
            delta = ghcomp.Line(cur_pt, next_pt)
            length = ghcomp.Length(delta)
            
            #direc = ghcomp.LineSDL(mid_pt, normal, length)
            
            grid_line = ghcomp.LineSDL(cur_pt, ghcomp.Multiplication(grid_direc, -1), length)
            _, end_pt = ghcomp.EndPoints(grid_line)
            diag_vec, y_length = ghcomp.Vector2Pt(end_pt, next_pt, False)
            black_n.append(diag_vec)
            
            diag_line = ghcomp.LineSDL(end_pt, tgt, length)
            _, diag_pt = ghcomp.EndPoints(diag_line)
            _, x_length = ghcomp.Vector2Pt(cur_pt, diag_pt, False)
            
            black_x.append(ghcomp.ConstructDomain(ghcomp.Division(x_length,2), ghcomp.Division(x_length,-2)))
            black_y.append(ghcomp.ConstructDomain(ghcomp.Division(y_length,2), ghcomp.Division(y_length,-2)))
            
            grid_diag = ghcomp.LineSDL(mid_pt, grid_direc, 0.55*length)
            _, black_pt = ghcomp.EndPoints(grid_diag)
            black_pts.append(black_pt)
            
        white_n = []
        for i in range(len(black_n) +1):
            if i==len(black_n):
                white_n.append(black_n[i-1])
                break
            cur_n = black_n[i]
            if i==0:
                white_n.append(cur_n)
            else:
                pre_n = black_n[i-1]
                white_n.append(ghcomp.Division(ghcomp.Addition(cur_n, pre_n), 2))
        
        white_k = self.white_k
        r = self.r
        black_k = self.black_k
        
        white_crv, white_rect = self.generate_rect(white_pts, white_k, r, white_n, 'white')
        black_crv, black_rect = self.generate_rect(black_pts, black_k, r, black_n, 'black')
        bound_crv = []
        bound_crv = self._generate_slope_bound(white_rect, black_rect)
        
        return bound_crv, white_n[-1], black_n[-1]
    
    def generate_horizontal_bound(self, white_base_crv, black_base_crv, white_pts):
        white_k = self.white_k
        white_sr = self.white_sr
        black_k = self.black_k
        black_sr = self.black_sr
        
        white_n = get_n_along_crv(white_pts, white_base_crv)
        black_pts, _, _ = ghcomp.CurveClosestPoint(white_pts, black_base_crv)
        black_n = get_n_along_crv(black_pts, black_base_crv)
        
        _, white_rect = self.generate_rect(white_pts, white_k, white_sr, white_n)
        _, black_rect = self.generate_rect(black_pts, black_k, black_sr, black_n)
        
        bound_crv = []
        for i in range(len(white_rect)):
            cur_white = white_rect[i]
            white_lb = cur_white['lb']
            bound_crv.append(white_lb)
            bound_crv.append(cur_white['left'])
            bound_crv.append(cur_white['lu'])
            bound_crv.append(cur_white['up'])
            bound_crv.append(cur_white['ru'])
            bound_crv.append(cur_white['right'])
            white_rb = cur_white['rb']
            bound_crv.append(white_rb)
            
            white_bottom = cur_white['bottom']
            
            if i!=0:
                pre_white = white_rect[i-1]
                pre_white_rb = pre_white['rb']
                pre_link1, _ = ghcomp.EndPoints(pre_white_rb)
                _, pre_link2 = ghcomp.EndPoints(white_lb)
                
                pre_white_bottom = pre_white['bottom']
                linkv = ghcomp.Merge(pre_link1, pre_link2)
                linkt = ghcomp.Merge(get_vec(pre_white_bottom), get_vec(white_bottom))
                pre_link, _, _ = ghcomp.TangentCurve(linkv, linkt, 0.5, 3)
                bound_crv.append(pre_link)
        bound_crv = ghcomp.JoinCurves(bound_crv, False)
        bound_crv = crv_direc(bound_crv)
        black_crv = []
        for i in range(len(black_rect)):
            black_crv.append(black_rect[i]['rect'])
            
        return bound_crv, black_crv, white_n[-1]

    def generate_black_pts(self, white_pts, white_base_crv, black_base_crv, grid_direc):
        #crv, _, _ = ghcomp.NurbsCurve(white_pts, 3, False)
        pts, _, _ = ghcomp.CurveClosestPoint(white_pts, white_base_crv)
        base_pts = []
        
        for i in range(len(pts)-1):
            cur_pt = ghcomp.Division(ghcomp.Addition(pts[i], pts[i+1]),2)
            base_pts.append(cur_pt)
        
        ray = ghcomp.LineSDL(base_pts, grid_direc, 10)
        
        black_pts, _, _ = ghcomp.CurveXCurve(ray, black_base_crv)
        return black_pts
    
    def _generate_transit_bound(self, white_rect, split_crv):
        bound_crv = []
        
        for i in range(len(white_rect)-1):
            if i==0 and i!=len(white_rect)-2:
                pass
                """
                cur_rect = white_rect[i]
                bottom_crv = cur_rect['bottom']
                rbarc = cur_rect['rb']
                #right_crv = cur_rect['right']
                
                cur_rect = ghcomp.JoinCurves(ghcomp.Merge(bottom_crv, rbarc), True)
                #cur_rect = ghcomp.JoinCurves(ghcomp.Merge(cur_rect, right_crv), True)
                _, cur_domain = ghcomp.CurveDomain(cur_rect)
                _, te = ghcomp.DeconstructDomain(cur_domain)
                
                suc_rect = white_rect[i+1]['rect']
                
                _, ts, tr = ghcomp.CurveXCurve(split_crv, cur_rect)
                rect_domain = ghcomp.ConstructDomain(tr, te)
                #ghcomp.SubCurve()
                rect_crv = ghcomp.SubCurve(cur_rect, rect_domain)
                bound_crv.append(rect_crv)
                
                _, suc_ts, _ = ghcomp.CurveXCurve(split_crv, suc_rect)
                split_domain = ghcomp.ConstructDomain(ts, suc_ts[0])
                #ghcomp.SubCurve()
                sub_split = ghcomp.SubCurve(split_crv, split_domain)
                bound_crv.append(sub_split)
                """
                
            else:
                cur_rect = white_rect[i]['rect']
                suc_rect = white_rect[i+1]['rect']
                
                _, ts, tr = ghcomp.CurveXCurve(split_crv, cur_rect)
                try:
                    rect_domain = ghcomp.ConstructDomain(tr[0], tr[-1])
                    #ghcomp.SubCurve()
                    rect_crv = ghcomp.SubCurve(cur_rect, rect_domain)
                    bound_crv.append(rect_crv)
                except:
                    pass
                
                if i != len(white_rect)-2:
                    _, suc_ts, _ = ghcomp.CurveXCurve(split_crv, suc_rect)
                    split_domain = ghcomp.ConstructDomain(ts[-1], suc_ts[0])
                    #ghcomp.SubCurve()
                    sub_split = ghcomp.SubCurve(split_crv, split_domain)
                    bound_crv.append(sub_split)
        if len(bound_crv)!=0:
            bound_crv = ghcomp.JoinCurves(bound_crv, False)
        else:
            return None
        bound_crv = crv_direc(bound_crv)
        return bound_crv
        
    def generate_transit_bound(self, white_base_crv, split_crv, white_pts, black_pts, white_pre_n, begin = False):
        white_k = self.white_k
        white_sr = self.white_sr
        black_k = self.black_k
        r = self.r
        
        num = len(white_pts)
        crv_n = get_n_along_crv(white_pts, white_base_crv)
        white_n = []
        if begin == True:
            white_n = crv_n
        else:
            white_n = generate_n(white_pre_n, crv_n[-1], num)
        
        white_crv = []
        _, white_rect = self.generate_rect(white_pts, white_k*1.1, (r+white_sr)/2, white_n)
        for i in range(len(white_rect)):
            white_crv.append(white_rect[i]['rect'])
        black_crv = []
        _, black_rect = self.generate_rect(black_pts, black_k, r, white_n[0:-1])
        for i in range(len(black_rect)):
            black_crv.append(black_rect[i]['rect'])
        
        bound_crv = self._generate_transit_bound(white_rect, split_crv)
        
        return white_crv, black_crv, bound_crv
        
    def join_bound(self, bound_crv, split_crv):
        joined_crv = []
        for i in range(len(bound_crv)-1):
            cur_bound = bound_crv[i]
            next_bound = bound_crv[i+1]
            
            _, cur_end = ghcomp.EndPoints(cur_bound)
            next_start, _ = ghcomp.EndPoints(next_bound)
            
            _, t1, _ = ghcomp.CurveClosestPoint(cur_end, split_crv)
            _, tgt1, _ = ghcomp.EvaluateCurve(split_crv, t1)
            _, t2, _ = ghcomp.CurveClosestPoint(next_start, split_crv)
            _, tgt2, _ = ghcomp.EvaluateCurve(split_crv, t2)
            
            v = ghcomp.Merge(cur_end, next_start)
            direc = ghcomp.Merge(tgt1, tgt2)
            crv, _, _ = ghcomp.TangentCurve(v, direc, 0.5, 3)
            joined_crv.append(cur_bound)
            joined_crv.append(crv)
        joined_crv.append(bound_crv[-1])
        #joined_crv = ghcomp.JoinCurves(joined_crv, True)
        return joined_crv
            
    def generate_bound(self):
        #接口处永远是最后一个rect与split_crv相交
        
        pts = self.separate_pts(self.white_pts)
        white_last_n  = None
        bound_crv = []
        rect_crv = []
        
        for i in range(len(pts)):
            cur_seq = pts[i]
            type = cur_seq[0]
            white_pts = cur_seq[1:len(cur_seq)]
            white_pts = construct_safe_pts_list(white_pts)
            print(type)
            print(len(white_pts))
            
            if type == 'slope':
                slope_bound_crv, white_last_n, _ = self.generate_slope_bound(white_pts, self.grid_direc)
                bound_crv.append(slope_bound_crv)
            
            if type == "cross":
                cross_bound_crv, black_rect, white_last_n = self.generate_horizontal_bound(self.white_base_crv, self.black_base_crv, white_pts)
                bound_crv.append(cross_bound_crv)
                rect_crv += black_rect
            
            if type == 'transit':
                if i == 0:
                    next_seq = pts[i+1]
                    next_white_pt = next_seq[1]
                    white_pts.append(next_white_pt)
                    black_pts = self.generate_black_pts(white_pts, self.white_base_crv, self.black_base_crv, self.grid_direc)
                    black_pts = construct_safe_pts_list(black_pts)
                    _, black_rect, transit_bound_crv = self.generate_transit_bound(self.white_base_crv, self.split_crv, white_pts, black_pts, white_last_n, True)
                    if transit_bound_crv!=None:
                        bound_crv.append(transit_bound_crv)
                    rect_crv += black_rect
                else:
                    pre_seq = pts[i-1]
                    pre_white_pt = pre_seq[-1]
                    white_pts.insert(0, pre_white_pt)
                    
                    if i!=len(pts)-1:
                        next_seq = pts[i+1]
                        next_white_pt = next_seq[1]
                        white_pts.append(next_white_pt)
                    
                    black_pts = self.generate_black_pts(white_pts, self.white_base_crv, self.black_base_crv, self.grid_direc)
                    black_pts = construct_safe_pts_list(black_pts)
                    _, black_rect, transit_bound_crv = self.generate_transit_bound(self.white_base_crv, self.split_crv, white_pts, black_pts, white_last_n, False)
                    if bound_crv!=None:
                        bound_crv.append(transit_bound_crv)
                    rect_crv += black_rect
        bound_crv = self.join_bound(bound_crv, self.split_crv)
        self.bound_crv = bound_crv
        self.rect_crv = rect_crv
    

if __name__=='__main__':
    separatrix = Separatrix(grid_direc, white_pts, white_k, white_sr, black_k, black_sr, r, white_base_crv, split_crv, black_base_crv)
    separatrix.generate_bound()

    bound_crv = separatrix.bound_crv
    rect_crv = separatrix.rect_crv
    try:
        a = separatrix.bug
    except:
        pass