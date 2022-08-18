#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, August 17th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import Eto.Forms as forms
import Eto.Drawing as drawing

class RowControl(forms.GroupBox):
    def __init__(self, row_id):
        self.Text = '第{}排'.format(row_id)
        self.Padding = drawing.Padding(5)

        self.dot_type_label = forms.Label(Text = '花点类型：')
        self.dot_type_combo = forms.ComboBox()
        self.dot_type_combo.DataStore = ["圆点", "圆角矩形", "其他"]
        # self.dot_type_combo.ReadOnly = True
        # for circle dot
        self.circle_dot_radius_label = forms.Label(Text='圆点半径：')
        self.circle_dot_radius = forms.TextBox()
        
        self.round_rect_edge_label = forms.Label(Text='圆角矩形边长：')
        self.round_rect_edge = forms.TextBox()
        self.round_rect_radius_label = forms.Label(Text='圆角矩形半径：')
        self.round_rect_radius = forms.TextBox()

        self.layout = forms.DynamicLayout()
        # default is circle dot
        self.layout.AddRow(self.dot_type_label, self.dot_type_combo, self.circle_dot_radius_label, self.circle_dot_radius)
        self.Content = self.layout

    