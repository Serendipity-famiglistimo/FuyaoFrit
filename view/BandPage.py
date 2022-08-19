#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, August 15th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''

import Eto.Forms as forms
import Eto.Drawing as drawing
import Rhino
import rhinoscriptsyntax as rs
from Eto.Drawing import Size, Font, FontStyle
from view.RowConfigPanel import RowConfigPanel
from model.RowFrits import RowFrits

class BandPage(forms.TabPage):
    def __init__(self):
        forms.TabPage.__init__(self)
        self.Text = '带状区域'
        self.row_num = 1
        self.panel = forms.Scrollable()
        
        self.panel.Padding = drawing.Padding(10)
        self.data = []
        self.create_interface()
        
    def create_interface(self):
        
        self.panel.RemoveAll()
        # Create a table layout and add all the controls
        self.layout = forms.DynamicLayout()
        self.pick_label = forms.Label(Text='- 拾取几何轮廓', Font = Font('Microsoft YaHei', 12.))
        self.refer_btn = forms.Button(Text='选取参考轮廓线')
        self.refer_btn.Size = Size(100, 30)
        self.refer_btn.Click += self.PickReferCurve
        self.is_pick_label = forms.Label(Text='当前未选择曲线')
        self.is_pick_label.TextColor = drawing.Color.FromArgb(255, 0, 0)

        self.fill_label = forms.Label(Text='- 设置或加载填充规则', Font = Font('Microsoft YaHei', 12.))
        self.fill_btn = forms.Button(Text='手动添加新行')
        self.fill_btn.Size = Size(100, 30)
        self.fill_btn.Click += self.AddButtonClick

        self.load_btn = forms.Button(Text='加载填充规则')
        self.load_btn.Size = Size(100, 30)
        self.load_btn.Click += self.LoadButtonClick

        self.layout.DefaultSpacing = drawing.Size(8, 8)
        self.layout.AddSeparateRow(self.pick_label, None)
        self.layout.BeginVertical(padding=drawing.Padding(20, 0, 0, 0))
        self.layout.AddRow(self.refer_btn, None)
        self.layout.AddRow(self.is_pick_label, None)
        self.layout.EndVertical()
        self.layout.AddSeparateRow(self.fill_label, None)
        self.layout.AddSeparateRow(padding=drawing.Padding(20, 0, 0, 0), controls=[self.fill_btn, self.load_btn, None])
       
   
        self.layout.BeginVertical()
        for i in range(len(self.data)):
            self.layout.AddRow(RowConfigPanel(self.data[i]))
        self.layout.EndVertical()
        self.layout.AddSpace()
        self.panel.Content = self.layout
        self.Content = self.panel


    def AddButtonClick(self, sender, e):
        self.row_num += 1
        row_frits = RowFrits()
        row_frits.row_id = len(self.data)
        self.data.append(row_frits)
        self.create_interface()
    
    def LoadButtonClick(self, sender, e):
        # 清空现有的填充规则
        self.data.clear()
        self.create_interface()
        pass
    
    def OnGetRhinoObjects(self, sender, e):
        objectId = rs.GetCurveObject("Select curve:")
        if objectId is None: 
            print("Warning: No curve is selected")
            return
        print(objectId)
        
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
