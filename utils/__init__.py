#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Sunday, August 7th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
from frits import FritType

import ghpythonlib.components as ghcomp
from System.Drawing import Color


def safe_list_access(arr, i):
    arr_len = len(arr)
    if i < 0:
        return 0
    elif i < arr_len:
        return arr[i]
    else:
        return arr[arr_len - 1]

def tgt_angle(tgt):
    angle, _ = ghcomp.Angle(tgt, ghcomp.UnitX(1))
    _, y, _ = ghcomp.Deconstruct(tgt)
    larger_pattern, _ = ghcomp.LargerThan(y,0)
    factor = ghcomp.Subtraction(ghcomp.Multiplication(larger_pattern,2),1)
    rotate_angle = ghcomp.Multiplication(angle, factor)
    
    return rotate_angle

def remove_verbose(list):
    count = len(list)
    loop = []
    i = 0
    flag = False
    while i < count:
        for j in range(count-i-1):
            if list[i] == list[i+j+1]:
                print("**hit**")
                print(i)
                print(i+j+1)
                for k in range(j+1):
                    loop.append(list[i])
                    list.pop(i)
                i -= 1
                count -= j+1
                flag = True
                break
        if flag == True:
            break
        i += 1
   
    return list, loop, flag

def get_vec(line):
    start, end = ghcomp.EndPoints(line)
    deltax = end.X-start.X
    deltay = end.Y-start.Y
    deltaz = end.Z-start.Z
    vec, _ = ghcomp.VectorXYZ(deltax, deltay, deltaz)
    return vec

def generate_n(pre_n, last_n, num):
    start_x, start_y, start_z = ghcomp.DeconstructVector(pre_n)
    end_x, end_y, end_z = ghcomp.DeconstructVector(last_n)
    deltax = end_x - start_x
    deltay = end_y - start_y
    deltaz = end_z - start_z
    n = []
    for i in range(num):
        x = start_x + deltax*(i+1)/num
        y = start_y + deltay*(i+1)/num
        z = start_z + deltaz*(i+1)/num
        cur_n, _ = ghcomp.VectorXYZ(x, y, z)
        n.append(cur_n)
    return n

def get_n_along_crv(pts, crv):
    n=[]
    
    _, t, _ = ghcomp.CurveClosestPoint(pts, crv)
    _, tgt, _ = ghcomp.EvaluateCurve(crv, t)
    
    angle, _ = ghcomp.Angle(tgt, ghcomp.UnitX(1))
    _, y, _ = ghcomp.Deconstruct(tgt)
    larger_pattern, _ = ghcomp.LargerThan(y,0)
    factor = ghcomp.Subtraction(ghcomp.Multiplication(larger_pattern,2),1)
    rotate_angle = ghcomp.Multiplication(angle, factor)
    
    n, _ = ghcomp.Rotate(ghcomp.UnitY(-1), rotate_angle, ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)))
    
    return n
    
def crv_direc(crv):
    start,end = ghcomp.EndPoints(crv)
    startx, starty, _ = ghcomp.Deconstruct(start)
    endx, endy, _ = ghcomp.Deconstruct(end)
    if startx>endx:
        crv, _ = ghcomp.FlipCurve(crv)
    return crv
    
def construct_safe_pts_list(pts):
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

def get_color(id):
    colors = [Color.AntiqueWhite, Color.Aqua, Color.BlueViolet, Color.Chartreuse, Color.Coral, Color.DarkTurquoise,  Color.DeepPink, Color.Gold, Color.LawnGreen, Color.Turquoise]
    return colors[id % len(colors)]

    
