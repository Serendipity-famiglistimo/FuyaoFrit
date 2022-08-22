#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, August 22nd 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
from Zone import Zone
class BlockZone(Zone):
    def __init__(self):
        Zone.__init__(self)
        self.type = 'block'
        self.rows = list()
        self.curves = [None, None, None]
        self.is_flip = [False, False, False]
        self.relations = {}
    
    def add_relation(self):
        pass