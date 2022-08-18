#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, August 17th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import imp
import Eto.Forms as forms
import Eto.Drawing as drawing
from model.RowFrits import RowFrits
from frits import FritType

class RowConfigPanel(forms.GroupBox):
    def __init__(self, row_config):
        self.row_config = row_config
        self.Text = '第{}排'.format(row_config.row_id)
        self.setup_view()
    
    def setup_view(self):
        self.RemoveAll()
        self.dot_type_label = forms.Label(Text = '花点类型：')
        self.dot_type_combo = forms.ComboBox()
        # self.dot_type_combo.Padding = drawing.Padding(20, 0, 0, 0)
        self.dot_type_combo.DataStore = ["圆点", "圆角矩形", "其他"]
        self.dot_type_combo.SelectedIndex = self.row_config.dot_type
        self.dot_type_combo.SelectedIndexChanged += self.change_dot_type 
        # self.dot_type_combo.ReadOnly = True
        # for circle dot
        self.circle_dot_radius_label = forms.Label(Text='圆点半径：')
        self.circle_dot_radius = forms.TextBox(Text='{0}'.format(self.row_config.circle_config.r))
        self.circle_dot_radius.Size = drawing.Size(60, -1)
        
        self.round_rect_edge_label = forms.Label(Text='圆角矩形边长：')
        self.round_rect_edge = forms.TextBox(Text='{0}'.format(self.row_config.round_rect_config.k))
        self.round_rect_edge.Size = drawing.Size(60, -1)
        self.round_rect_radius_label = forms.Label(Text='圆角矩形半径：')
        self.round_rect_radius = forms.TextBox(Text='{0}'.format(self.row_config.round_rect_config.r))
        self.round_rect_radius.Size = drawing.Size(60, -1)

        self.stepping_label = forms.Label(Text='水平间距：')
        self.stepping_input = forms.TextBox(Text='{0}'.format(self.row_config.stepping))
        self.stepping_input.Size = drawing.Size(60, -1)
        self.position_label = forms.Label(Text='相对参考线距离：')
        self.position_input = forms.TextBox(Text='{0}'.format(self.row_config.position))
        self.position_input.Size = drawing.Size(60, -1)

        self.config_panel = forms.Panel()
        self.update_btn = forms.Button(Text='填充花点')
        self.update_btn.Size = drawing.Size(100, -1)
        self.layout = forms.DynamicLayout()

        panel_layout = forms.StackLayout()
        panel_layout.Orientation = forms.Orientation.Horizontal
        panel_layout.Spacing = 10
        # default is circle dot
        #self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        if self.row_config.dot_type == FritType.CIRCLE_DOT:
            panel_layout.Items.Add(self.dot_type_label)
            panel_layout.Items.Add(self.dot_type_combo)
            panel_layout.Items.Add(self.circle_dot_radius_label)
            panel_layout.Items.Add(self.circle_dot_radius)
            panel_layout.Items.Add(self.stepping_label)
            panel_layout.Items.Add(self.stepping_input)
            panel_layout.Items.Add(self.position_label)
            panel_layout.Items.Add(self.position_input)
            
        elif self.row_config.dot_type == FritType.ROUND_RECT:
            panel_layout.Items.Add(self.dot_type_label)
            panel_layout.Items.Add(self.dot_type_combo)
            panel_layout.Items.Add(self.round_rect_edge_label)
            panel_layout.Items.Add(self.round_rect_edge)
            panel_layout.Items.Add(self.round_rect_radius_label)
            panel_layout.Items.Add(self.round_rect_radius)
            panel_layout.Items.Add(self.stepping_label)
            panel_layout.Items.Add(self.stepping_input)
            panel_layout.Items.Add(self.position_label)
            panel_layout.Items.Add(self.position_input)
        self.config_panel.Content = panel_layout
        self.layout.DefaultSpacing = drawing.Size(10, 10)
        self.layout.AddSeparateRow(self.config_panel)
        self.layout.AddSeparateRow(self.update_btn, None)
        self.Content = self.layout
    
    def change_dot_type(self, sender, e):
        if self.dot_type_combo.SelectedIndex == 0:
            self.row_config.dot_type = FritType.CIRCLE_DOT
        elif self.dot_type_combo.SelectedIndex == 1:
            self.row_config.dot_type = FritType.ROUND_RECT
        
        self.setup_view()

    