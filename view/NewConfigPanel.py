#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, August 17th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import Rhino as rc
import rhinoscriptsyntax as rs
import Eto.Forms as forms
import Eto.Drawing as drawing
from Eto.Drawing import Font
from model.RowFrits import RowArrangeType, RowFrits
import utils

from frits import FritType

class NewConfigPanel(forms.GroupBox):
    def __init__(self, parent, row_config):
        self.parent = parent
        self.model = row_config
        self.Text = '第{}排'.format(row_config.row_id)
        self.setup_view()
        self.display = rc.Display.CustomDisplay(True)
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)

    def setup_view(self):
        self.RemoveAll()
        self.basic_setting_label = forms.Label(Text='基础设置:', Font = Font('Microsoft YaHei', 12.))
        
        self.circle1_dot_radius_label = forms.Label(Text='3排相对参考线距离：')
        self.circle1_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_position3))
        self.circle1_dot_radius.Size = drawing.Size(60, -1)
        self.circle1_dot_radius.TextChanged += self.circle1_dot_radius_changed
        
        self.circle2_dot_radius_label = forms.Label(Text='2排相对参考线距离：')
        self.circle2_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_position2))
        self.circle2_dot_radius.Size = drawing.Size(60, -1)
        self.circle2_dot_radius.TextChanged += self.circle2_dot_radius_changed
        
        self.circle3_dot_radius_label = forms.Label(Text='1排相对参考线距离：')
        self.circle3_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_position1))
        self.circle3_dot_radius.Size = drawing.Size(60, -1)
        self.circle3_dot_radius.TextChanged += self.circle3_dot_radius_changed
        
        self.circle4_dot_radius_label = forms.Label(Text='1排直径：')
        self.circle4_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_r1))
        self.circle4_dot_radius.Size = drawing.Size(60, -1)
        self.circle4_dot_radius.TextChanged += self.circle4_dot_radius_changed
        
        self.circle5_dot_radius_label = forms.Label(Text='2排直径：')
        self.circle5_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_r2))
        self.circle5_dot_radius.Size = drawing.Size(60, -1)
        self.circle5_dot_radius.TextChanged += self.circle5_dot_radius_changed
        
        self.circle6_dot_radius_label = forms.Label(Text='3排直径：')
        self.circle6_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_r3))
        self.circle6_dot_radius.Size = drawing.Size(60, -1)
        self.circle6_dot_radius.TextChanged += self.circle6_dot_radius_changed
        
        
        
        
        self.stepping_label = forms.Label(Text='花点水平间距：')
        self.stepping_input = forms.TextBox(Text='{0}'.format(self.model.stepping))
        self.stepping_input.Size = drawing.Size(60, -1)
        self.stepping_input.TextChanged += self.stepping_input_changed
        
        self.position_label = forms.Label(Text='花点垂直间距：')
        self.position_input = forms.TextBox(Text='{0}'.format(self.model.position))
        self.position_input.Size = drawing.Size(60, -1)
        self.position_input.TextChanged += self.position_input_changed
        
        self.layout = forms.DynamicLayout()
        self.layout.DefaultSpacing = drawing.Size(10, 10)
       
        # default is circle dot
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.basic_setting_label, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.circle1_dot_radius_label,self.circle1_dot_radius,self.circle2_dot_radius_label,self.circle2_dot_radius,None)
        self.layout.AddRow(self.circle3_dot_radius_label,self.circle3_dot_radius,self.circle4_dot_radius_label,self.circle4_dot_radius,None)
        self.layout.AddRow(self.circle5_dot_radius_label,self.circle5_dot_radius,self.circle6_dot_radius_label,self.circle6_dot_radius,None)
        self.layout.AddRow(self.stepping_label,self.stepping_input,self.position_label,self.position_input,None)
        self.layout.EndVertical()
        self.Content = self.layout
        
        
    def circle1_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_position3 = float(self.circle1_dot_radius.Text)
        except:
            pass
    def circle2_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_position2 = float(self.circle2_dot_radius.Text)
        except:
            pass
    def circle3_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_position1 = float(self.circle3_dot_radius.Text)
        except:
            pass
    def circle4_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_r1 = float(self.circle4_dot_radius.Text)
        except:
            pass
    def circle5_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_r2 = float(self.circle5_dot_radius.Text)
        except:
            pass
            
    def circle6_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_r3 = float(self.circle6_dot_radius.Text)
        except:
            pass
    
    def stepping_input_changed(self, sender, e):
        try:
            self.model.stepping = float(self.stepping_input.Text)
        except:
            pass
    
    def position_input_changed(self, sender, e):
        try:
            self.model.position = float(self.position_input.Text)
        except:
            pass
    
    def fill_row_frits(self, sender, e):
        self.clear_dots()
        self.model.fill_dots()
        for d in self.model.dots:
            d.draw(self.display, self.display_color)
    
    def clear_dots(self):
        self.display.Clear()
        #print(self.model.row_id)
        #del self.model.dots[self.model.row_id]
    
    def bake(self):
        layer_name = 'page_{0}_row_{1}'.format(self.parent.page_id, self.model.row_id)
        rs.AddLayer(layer_name,get_color(self.model.row_id), parent='fuyao_frits')
        for d in self.model.dots:
            obj = d.bake()
            rs.ObjectLayer(obj, layer_name)