#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Sunday, August 7th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
from Rhino import *
from Rhino.DocObjects import *
from Rhino.Commands import *
from Rhino.Input import *
from Rhino.Input.Custom import *
from scriptcontext import doc
import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import System
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms
from Eto.Drawing import Size, Font, FontStyle
import ghpythonlib.components as ghcomp

class MainDialog(forms.Dialog[bool]):
 
    # Dialog box Class initializer
    def __init__(self):
        # Initialize dialog box
        self.Title = '福耀印刷花点排布工具'
        self.Padding = drawing.Padding(10)
        self.Resizable = True
 
        # 标题
        self.heading_label = forms.Label(Text= '福耀印刷花点排布工具', Font = Font('Microsoft YaHei', 14., FontStyle.Bold))
        # self.m_headding.Color = drawing.Color.FromArgb(255, 0, 0)
        self.heading_label.TextAlignment = forms.TextAlignment.Center 
        # 选择填充类型
        self.type_label = forms.Label(Text = '选择填充类型')
        self.type_radio = forms.RadioButtonList(
			DataStore = ['孔状区域', '块状区域', '带状区域'],
			SelectedIndex = 0,
			Spacing = Size(9,0))
        
        # 拾取几何轮廓
        self.pick_label = forms.Label(Text='拾取几何轮廓')
        
        self.inner_btn = forms.Button(Text='选取内边界曲线')
        self.inner_btn.Click += self.SelectObjButtonClick
        self.outer_btn = forms.Button(Text='选取外边界曲线')
        self.outer_btn.Click += self.SelectObjButtonClick
        self.refer_btn = forms.Button(Text='选取参考轮廓线')
        self.refer_btn.Click += self.SelectObjButtonClick
        
        # 花点参数设置（mm）
        self.params_label = forms.Label(Text='参数设置')
        self.radius_label = forms.Label(Text='Radius')
        self.radius_text = forms.TextBox(Text='0.425 0.6 0.85')
        self.hspace_label = forms.Label(Text='hspace')
        self.hspace_text = forms.TextBox(Text='2.2')
        self.vspace_label = forms.Label(Text='vspace')
        self.vspace_text = forms.TextBox(Text='1.4 1.7')
        self.horizontal_label = forms.Label(Text='horizontal')
        self.horizontal_text = forms.TextBox(Text='2.2')
        self.vertical_label = forms.Label(Text='vertical')
        self.vertical_text = forms.TextBox(Text='1.7')
        self.inner_radius_label = forms.Label(Text='inner radius')
        self.inner_radius_text = forms.TextBox(Text='0.5')
        self.iter_num_label = forms.Label(Text='iteration nums')
        self.iter_num_text = forms.TextBox(Text='100')
        
        self.generate_btn = forms.Button(Text='生成')
        
        # 布局
        layout = forms.DynamicLayout()
        layout.Spacing = drawing.Size(5, 5)
        layout.AddSeparateRow(self.heading_label)
        layout.AddSeparateRow(self.type_label)
        layout.AddSeparateRow(self.type_radio)
        
        layout.BeginVertical()
        layout.AddRow(self.pick_label)
        layout.Spacing = drawing.Size(5, 5)
        layout.AddRow(self.inner_btn, self.outer_btn, self.refer_btn)
        layout.EndVertical()
        layout.BeginVertical()
        layout.Spacing = drawing.Size(5, 5)
        layout.AddRow(self.params_label)
        layout.AddRow(self.radius_label, self.radius_text)
        layout.AddRow(self.hspace_label, self.hspace_text)
        layout.AddRow(self.vspace_label, self.vspace_text)
        layout.AddRow(self.horizontal_label, self.horizontal_text)
        layout.AddRow(self.vertical_label, self.vertical_text)
        layout.AddRow(self.inner_radius_label, self.inner_radius_text)
        layout.AddRow(self.iter_num_label, self.iter_num_text)
        layout.AddRow(self.generate_btn)
    
        layout.EndVertical()
        # Set the dialog content
        self.Content = layout
        
    # Start of the class functions
    def OnGetRhinoObjects(self, sender, e):
        objectId = rs.GetCurveObject("Select curve")
        if objectId is None: 
            MessageBox.Show("未选中任何曲线")
            return
        print(objectId)
        len = ghcomp.Length(objectId[0])
        print(len)
        # MessBox.Show(len)
        
    def SelectObjButtonClick(self, sender, e):
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnGetRhinoObjects)
        
if __name__ == "__main__":
    dialog = MainDialog();
    rc = dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)