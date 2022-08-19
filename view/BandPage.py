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
from model.BandZone import BandZone
import ghpythonlib.components as ghcomp


class BandPageView(forms.TabPage):
    
    # .net 必须使用__new__显示调用构造函数！！！
    def __new__(cls, *args):
        return forms.TabPage.__new__(cls)    

    def __init__(self, display):
        self.Text = '带状区域'
        self.row_num = 1
        self.panel = forms.Scrollable()
        self.panel.Padding = drawing.Padding(10)
        self.model = BandZone()
        self.display = display 
        self.create_interface()
        
    def create_interface(self):
        
        self.panel.RemoveAll()
        # Create a table layout and add all the controls
        self.layout = forms.DynamicLayout()
        self.pick_label = forms.Label(Text='- 拾取几何轮廓', Font = Font('Microsoft YaHei', 12.))
        self.refer_btn = forms.Button(Text='选取参考轮廓线')
        self.refer_btn.Size = Size(100, 30)
        self.refer_btn.Click += self.PickReferCurve
        # checkbox
        self.flip_check = forms.CheckBox()
        self.flip_check.Text = '是否反转该曲线'
        self.is_pick_label = forms.Label()
        if len(self.model.curves) == 0:
            self.is_pick_label.Text = '未选择曲线'
            self.is_pick_label.TextColor = drawing.Color.FromArgb(255, 0, 0)
        else:
            self.is_pick_label.Text = '选择了曲线{0}.'.format(self.model.curves[0])
            self.is_pick_label.TextColor = drawing.Color.FromArgb(44,162,95)

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
        self.layout.AddRow(self.flip_check, None)
        self.layout.AddRow(self.is_pick_label, None)
        self.layout.EndVertical()
        self.layout.AddSeparateRow(self.fill_label, None)
        self.layout.AddSeparateRow(padding=drawing.Padding(20, 0, 0, 0), controls=[self.fill_btn, self.load_btn, None])
       
   
        self.layout.BeginVertical()
        for i in range(len(self.model.rows)):
            self.layout.AddRow(RowConfigPanel(self.display, self.model.rows[i]))
        self.layout.EndVertical()
        self.layout.AddSpace()
        self.panel.Content = self.layout
        self.Content = self.panel


    def AddButtonClick(self, sender, e):
        self.row_num += 1
        row_frits = RowFrits(len(self.model.rows), self.model)
       
        self.model.rows.append(row_frits)
        # row_frits.band_model = self.model  # type: ignore
        self.create_interface()
    
    def LoadButtonClick(self, sender, e):
        # 清空现有的填充规则
        self.model.rows.clear()
        self.create_interface()
        pass
    
    def OnGetRhinoObjects(self, sender, e):
        objectId = rs.GetCurveObject("Select curve:")
        if objectId is None: 
            print("Warning: No curve is selected")
            return
        print(objectId)
        print(self.model.curves)
        # python 2.7 clear list
        del self.model.curves[:]
        crv = objectId[0]
        if self.flip_check.Checked:
            crv, _ = ghcomp.FlipCurve(crv)
        self.model.curves.append(crv)
        print(self.model.curves)
        self.create_interface()
    
    def PickReferCurve(self, sender, e):
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnGetRhinoObjects)
