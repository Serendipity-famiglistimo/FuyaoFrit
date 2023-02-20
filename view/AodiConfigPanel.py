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

class AODIConfigPanel(forms.GroupBox):
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
        
        self.outer_block_k_label = forms.Label(Text='块状最外侧花点K值：')
        self.outer_block_k = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.outer_block_k))
        self.outer_block_k.Size = drawing.Size(60, -1)
        self.outer_block_k.TextChanged += self.outer_block_k_changed
        
        self.outer_block_r_label = forms.Label(Text='块状最外侧花点R值：')
        self.outer_block_r = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.outer_block_r))
        self.outer_block_r.Size = drawing.Size(60, -1)
        self.outer_block_r.TextChanged += self.outer_block_r_changed
        
        
        self.inner_block_k_label = forms.Label(Text='块状中间花点K值：')
        self.inner_block_k = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.inner_block_k))
        self.inner_block_k.Size = drawing.Size(60, -1)
        self.inner_block_k.TextChanged += self.inner_block_k_changed
        
        self.inner_block_r_label = forms.Label(Text='块状中间花点R值：')
        self.inner_block_r = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.inner_block_r))
        self.inner_block_r.Size = drawing.Size(60, -1)
        self.inner_block_r.TextChanged += self.inner_block_r_changed
        
        
        self.border_k_label = forms.Label(Text='黑白边缘花点K值：')
        self.border_k = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.border_k))
        self.border_k.Size = drawing.Size(60, -1)
        self.border_k.TextChanged += self.border_k_changed
        
        self.border_r_label = forms.Label(Text='黑白边缘花点R值：')
        self.border_r = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.border_r))
        self.border_r.Size = drawing.Size(60, -1)
        self.border_r.TextChanged += self.border_r_changed
        
        
        self.black_band_k1_label = forms.Label(Text='黑色带状花点K1值：')
        self.black_band_k1 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.black_band_k1))
        self.black_band_k1.Size = drawing.Size(60, -1)
        self.black_band_k1.TextChanged += self.black_band_k1_changed
        self.black_band_k2_label = forms.Label(Text='黑色带状花点K2值：')
        self.black_band_k2 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.black_band_k2))
        self.black_band_k2.Size = drawing.Size(60, -1)
        self.black_band_k2.TextChanged += self.black_band_k2_changed
        
        self.black_band_h2_label = forms.Label(Text='黑色带状花点H2值：')
        self.black_band_h2 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.black_band_h2))
        self.black_band_h2.Size = drawing.Size(60, -1)
        self.black_band_h2.TextChanged += self.black_band_h2_changed
        self.black_band_h1_label = forms.Label(Text='黑色带状花点H1值：')
        self.black_band_h1 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.black_band_h1))
        self.black_band_h1.Size = drawing.Size(60, -1)
        self.black_band_h1.TextChanged += self.black_band_h1_changed
        
        
        self.down_block_area_k1_label = forms.Label(Text='小块状花点K1值：')
        self.down_block_area_k1 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_block_area_k1))
        self.down_block_area_k1.Size = drawing.Size(60, -1)
        self.down_block_area_k1.TextChanged += self.down_block_area_k1_changed
        
        self.down_block_area_k2_label = forms.Label(Text='小块状花点K2值：')
        self.down_block_area_k2 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_block_area_k2))
        self.down_block_area_k2.Size = drawing.Size(60, -1)
        self.down_block_area_k2.TextChanged += self.down_block_area_k2_changed
        
        self.down_block_area_k3_label = forms.Label(Text='小块状花点K3值：')
        self.down_block_area_k3 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_block_area_k3))
        self.down_block_area_k3.Size = drawing.Size(60, -1)
        self.down_block_area_k3.TextChanged += self.down_block_area_k3_changed
        
        self.down_block_area_k4_label = forms.Label(Text='小块状花点K4值：')
        self.down_block_area_k4 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_block_area_k4))
        self.down_block_area_k4.Size = drawing.Size(60, -1)
        self.down_block_area_k4.TextChanged += self.down_block_area_k4_changed
        
        self.down_block_area_k5_label = forms.Label(Text='小块状花点K5值：')
        self.down_block_area_k5 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_block_area_k5))
        self.down_block_area_k5.Size = drawing.Size(60, -1)
        self.down_block_area_k5.TextChanged += self.down_block_area_k5_changed
        
        
        self.down_block_area_h1_label = forms.Label(Text='小块状花点H1值：')
        self.down_block_area_h1 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_block_area_h1))
        self.down_block_area_h1.Size = drawing.Size(60, -1)
        self.down_block_area_h1.TextChanged += self.down_block_area_h1_changed
        
        self.down_block_area_h2_label = forms.Label(Text='小块状花点H2值：')
        self.down_block_area_h2 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_block_area_h2))
        self.down_block_area_h2.Size = drawing.Size(60, -1)
        self.down_block_area_h2.TextChanged += self.down_block_area_h2_changed
        
        self.down_block_area_h3_label = forms.Label(Text='小块状花点H3值：')
        self.down_block_area_h3 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_block_area_h3))
        self.down_block_area_h3.Size = drawing.Size(60, -1)
        self.down_block_area_h3.TextChanged += self.down_block_area_h3_changed
        
        self.down_block_area_h4_label = forms.Label(Text='小块状花点H4值：')
        self.down_block_area_h4 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_block_area_h4))
        self.down_block_area_h4.Size = drawing.Size(60, -1)
        self.down_block_area_h4.TextChanged += self.down_block_area_h4_changed
        
        self.down_block_area_h5_label = forms.Label(Text='小块状花点H5值：')
        self.down_block_area_h5 = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_block_area_h5))
        self.down_block_area_h5.Size = drawing.Size(60, -1)
        self.down_block_area_h5.TextChanged += self.down_block_area_h5_changed
        
        self.stepping_label = forms.Label(Text='大块状花点水平间距：')
        self.stepping_input = forms.TextBox(Text='{0}'.format(self.model.stepping))
        self.stepping_input.Size = drawing.Size(60, -1)
        self.stepping_input.TextChanged += self.stepping_input_changed
        
        self.position_label = forms.Label(Text='大块状花点垂直间距：')
        self.position_input = forms.TextBox(Text='{0}'.format(self.model.position))
        self.position_input.Size = drawing.Size(60, -1)
        self.position_input.TextChanged += self.position_input_changed
        
        self.down_horizontal_label = forms.Label(Text='小块状花点水平间距：')
        self.down_horizontal_input = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_horizontal))
        self.down_horizontal_input.Size = drawing.Size(60, -1)
        self.down_horizontal_input.TextChanged += self.down_horizontal_changed
        
        self.down_vertical_label = forms.Label(Text='小块状花点垂直间距：')
        self.down_vertical_input = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.down_vertical))
        self.down_vertical_input.Size = drawing.Size(60, -1)
        self.down_vertical_input.TextChanged += self.down_vertical_changed
        
        self.layout = forms.DynamicLayout()
        self.layout.DefaultSpacing = drawing.Size(10, 10)
       
        # default is circle dot
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.basic_setting_label, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.outer_block_k_label,self.outer_block_k,self.outer_block_r_label,self.outer_block_r,None)
        self.layout.AddRow(self.inner_block_k_label,self.inner_block_k,self.inner_block_r_label,self.inner_block_r,None)
        
        self.layout.AddRow(self.border_k_label,self.border_k,self.border_r_label,self.border_r,None)
        
        self.layout.AddRow(self.black_band_k1_label,self.black_band_k1,self.black_band_h1_label,self.black_band_h1,None)
        self.layout.AddRow(self.black_band_k2_label,self.black_band_k2,self.black_band_h2_label,self.black_band_h2,None)
        
        self.layout.AddRow(self.down_block_area_k1_label,self.down_block_area_k1,self.down_block_area_h1_label,self.down_block_area_h1,None)
        self.layout.AddRow(self.down_block_area_k2_label,self.down_block_area_k2,self.down_block_area_h2_label,self.down_block_area_h2,None)
        self.layout.AddRow(self.down_block_area_k3_label,self.down_block_area_k3,self.down_block_area_h3_label,self.down_block_area_h3,None)
        self.layout.AddRow(self.down_block_area_k4_label,self.down_block_area_k4,self.down_block_area_h4_label,self.down_block_area_h4,None)
        self.layout.AddRow(self.down_block_area_k5_label,self.down_block_area_k5,self.down_block_area_h5_label,self.down_block_area_h5,None)
        
        
        self.layout.AddRow(self.stepping_label,self.stepping_input,self.position_label,self.position_input,None)
        self.layout.AddRow(self.down_horizontal_label,self.down_horizontal_input,self.down_vertical_label,self.down_vertical_input,None)
        
        self.layout.EndVertical()
        self.Content = self.layout
        
        
    def outer_block_k_changed(self, sender, e):
        try:
            self.model.round_rect_config.outer_block_k = float(self.outer_block_k.Text)
            
        except:
            pass
    def outer_block_r_changed(self, sender, e):
        try:
            self.model.round_rect_config.outer_block_r = float(self.outer_block_r.Text)
            
        except:
            pass
    def inner_block_k_changed(self, sender, e):
        try:
            self.model.round_rect_config.inner_block_k = float(self.inner_block_k.Text)
            
        except:
            pass
    def inner_block_r_changed(self, sender, e):
        try:
            self.model.round_rect_config.inner_block_r = float(self.inner_block_r.Text)
            
        except:
            pass
    def border_k_changed(self, sender, e):
        try:
            self.model.round_rect_config.border_k = float(self.border_k.Text)
            
        except:
            pass
    def border_r_changed(self, sender, e):
        try:
            self.model.round_rect_config.border_r = float(self.border_r.Text)
            
        except:
            pass
    def black_band_k1_changed(self, sender, e):
        try:
            self.model.round_rect_config.black_band_k1 = float(self.black_band_k1.Text)
            
        except:
            pass
    def black_band_k2_changed(self, sender, e):
        try:
            self.model.round_rect_config.black_band_k2 = float(self.black_band_k2.Text)
            
        except:
            pass
    def black_band_h1_changed(self, sender, e):
        try:
            self.model.round_rect_config.black_band_h1 = float(self.black_band_h1.Text)
            
        except:
            pass
    def black_band_h2_changed(self, sender, e):
        try:
            self.model.round_rect_config.black_band_h2 = float(self.black_band_h2.Text)
            
        except:
            pass
    def down_block_area_k1_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_block_area_k1 = float(self.down_block_area_k1.Text)
            
        except:
            pass
    def down_block_area_k2_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_block_area_k2 = float(self.down_block_area_k2.Text)
            
        except:
            pass
    def down_block_area_k3_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_block_area_k3 = float(self.down_block_area_k3.Text)
            
        except:
            pass
    def down_block_area_k4_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_block_area_k4 = float(self.down_block_area_k4.Text)
            
        except:
            pass
    def down_block_area_k5_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_block_area_k5 = float(self.down_block_area_k5.Text)
            
        except:
            pass
    
    
    def down_block_area_h1_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_block_area_h1 = float(self.down_block_area_h1.Text)
            
        except:
            pass
    def down_block_area_h2_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_block_area_h2 = float(self.down_block_area_h2.Text)
            
        except:
            pass
    def down_block_area_h3_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_block_area_h3= float(self.down_block_area_h3.Text)
            
        except:
            pass
    def down_block_area_h4_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_block_area_h4 = float(self.down_block_area_h4.Text)
            
        except:
            pass
    def down_block_area_h5_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_block_area_h5 = float(self.down_block_area_h5.Text)
            
        except:
            pass
    
    def down_horizontal_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_horizontal = float(self.down_horizontal_input.Text)
            
        except:
            pass
    
    def down_vertical_changed(self, sender, e):
        try:
            self.model.round_rect_config.down_vertical = float(self.down_vertical_input.Text)
            
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