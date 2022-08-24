#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Sunday, August 21st 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import Rhino
import Eto.Forms as forms
import Eto.Drawing as drawing
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp


class TransitCurveDialog(forms.Dialog[bool]):
    
    def __init__(self):
        self.refer_crv = None
        self.Title = '曲线过渡工具'
        self.Padding = drawing.Padding(10)
        self.Resizable = False
        self.Closing += self.OnFormClosed
        self.MinimumSize = drawing.Size(400, 300)

        self.refer_btn = forms.Button(Text='选取参考轮廓线')
        self.refer_btn.Size = drawing.Size(100, 30)
        self.refer_btn.Click += self.PickReferCurve

        self.left_label = forms.Label(Text='左侧偏移距离: ')
        self.left_text = forms.TextBox(Text='0.0')

        self.right_label = forms.Label(Text='右侧偏移距离：')
        self.right_text = forms.TextBox(Text='0.0')

        self.layout = forms.DynamicLayout()

        self.layout.DefaultSpacing = drawing.Size(8, 8)
        self.layout.BeginVertical(padding=drawing.Padding(20, 0, 0, 0))
        self.layout.AddRow(self.refer_btn, None)
        
    
    def OnGetRhinoObjects(self, sender, e):
        objectId = rs.GetCurveObject("Select curve:")
        if objectId is None: 
            print("Warning: No curve is selected")
            return
        print(objectId)
        print(self.model.curves)
        # python 2.7 clear list
        del self.model.curves[:]
        self.refer_crv = objectId[0]
        
    
    def PickReferCurve(self, sender, e):
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnGetRhinoObjects)