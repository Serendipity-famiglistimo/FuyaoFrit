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
import Rhino as rc
import scriptcontext
import System
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms
from Eto.Drawing import Size, Font, FontStyle
import ghpythonlib.components as ghcomp
import FuyaoFrit
reload(FuyaoFrit)
import sys
print(sys.path)

class MainDialog(forms.Dialog[bool]):
 
    # Dialog box Class initializer
    def __init__(self):
        
        self.fuyaoFrit = FuyaoFrit.FuyaoFrit()
        # Initialize dialog box
        self.Title = '福耀印刷花点排布工具'
        self.Padding = drawing.Padding(10)
        self.Resizable = True
        self.Closing += self.OnFormClosed
 
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
        self.inner_btn.Click += self.PickInnerCurve
        self.outer_btn = forms.Button(Text='选取外边界曲线')
        self.outer_btn.Click += self.PickOuterCurve
        self.refer_btn = forms.Button(Text='选取参考轮廓线')
        self.refer_btn.Click += self.PickReferCurve
        self.active_btn = 0
        
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
        self.generate_btn.Click += self.GenerateBtnClick
        
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
    def OnFormClosed(self, sender, e):
        self.fuyaoFrit.close()
        
    def OnGetRhinoObjects(self, sender, e):
        objectId = rs.GetCurveObject("Select curve:")
        if objectId is None: 
            print("Warning: No curve is selected")
            return
        print(objectId)
        len = ghcomp.Length(objectId[0])
        print("select curve length: {0}".format(len))
        if self.active_btn == 1:
            self.fuyaoFrit.inner_curve = objectId[0]
        elif self.active_btn == 2:
            self.fuyaoFrit.outer_curve = objectId[0]
        elif self.active_btn == 3:
            self.fuyaoFrit.refer_curve = objectId[0]
        self.active_btn = 0
        
    def PickInnerCurve(self, sender, e):
        self.active_btn = 1
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnGetRhinoObjects)
    
    def PickOuterCurve(self, sender, e):
        self.active_btn = 2
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnGetRhinoObjects)
    
    def PickReferCurve(self, sender, e):
        self.active_btn = 3
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnGetRhinoObjects)

    def GenerateBtnClick(self, sender, e):
        # check data
        # run fuyao frit
        self.fuyaoFrit.run()

        
if __name__ == "__main__":
    dialog = MainDialog();
    rc = dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)