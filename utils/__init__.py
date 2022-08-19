#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Sunday, August 7th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import ghpythonlib.components as ghcomp

def safe_list_access(arr, i):
    arr_len = len(arr)
    if i < 0:
        return 0
    elif i < arr_len:
        return arr[i]
    else:
        return arr[arr_len - 1]

def tgt_angle(tgt):
    angle, _ = ghcomp.Angle(tgt, ghcomp.UnitX())
    _, y, _ = ghcomp.Deconstruct(tgt)
    larger_pattern, _ = ghcomp.LargerThan(y,0)
    factor = ghcomp.Subtraction(ghcomp.Multiplication(larger_pattern,2),1)
    rotate_angle = ghcomp.Multiplication(angle, factor)
    
    return rotate_angle