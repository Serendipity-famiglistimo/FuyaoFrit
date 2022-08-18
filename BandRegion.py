#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, August 15th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
from Region import Region
import Eto.Forms as forms
import Eto.Drawing as drawing
import Rhino
import rhinoscriptsyntax as rs

class BandRegion(Region):
    def __init__(self):
        Region.__init__(self)
        pass

class TextAreaPanel(forms.Scrollable):
    # Initializer
    def __init__(self):
        # create a control
        text = forms.TextArea()
        text.Text = "Every Good Boy Deserves Fudge."
        # create a layout
        layout = forms.TableLayout()
        layout.Padding = drawing.Padding(10)
        layout.Spacing = drawing.Size(5, 5)
        layout.Rows.Add(text)
        # set the panel content
        self.Content = layout

class BandRegionPage(forms.TabPage):
    def __init__(self):
        forms.TabPage.__init__(self)
        panel = forms.Scrollable()
        panel.Padding = drawing.Padding(10)
        # Create a table layout and add all the controls
        layout = forms.DynamicLayout()
        layout.Spacing = drawing.Size(5, 5)

        self.pick_label = forms.Label(Text='拾取几何轮廓')
        self.inner_btn = forms.Button(Text='选取内边界曲线')
        self.inner_btn.Click += self.PickInnerCurve
        self.outer_btn = forms.Button(Text='选取外边界曲线')
        self.outer_btn.Click += self.PickOuterCurve
        self.refer_btn = forms.Button(Text='选取参考轮廓线')
        self.refer_btn.Click += self.PickReferCurve
        layout.BeginVertical()
        layout.AddRow(self.pick_label)
        layout.Spacing = drawing.Size(5, 5)
        layout.AddRow(self.inner_btn, self.outer_btn, self.refer_btn)
        layout.EndVertical()
        panel.Content = layout

        self.Content = panel
    
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
