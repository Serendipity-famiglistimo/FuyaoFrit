#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, August 17th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import imp
import Rhino
import Eto.Forms as forms
import Eto.Drawing as drawing
from Eto.Drawing import Size, Font, FontStyle
import RowControl
reload(RowControl)
# from RowControl import RowControl

class FritDialog(forms.Dialog[bool]):
    def __init__(self):
        self.Title = '福耀印刷花点排布工具'
        self.Padding = drawing.Padding(10)
        self.Resizable = True
        self.Closing += self.OnFormClosed
 
        # 标题
        self.heading_label = forms.Label(Text= '带状区域', Font = Font('Microsoft YaHei', 14., FontStyle.Bold))
        # self.m_headding.Color = drawing.Color.FromArgb(255, 0, 0)
        self.heading_label.TextAlignment = forms.TextAlignment.Center
        self.addButton = forms.Button(Text='添加行')
        self.addButton.Click += self.AddButtonClick
        self.layout = forms.DynamicLayout()
        # default is circle dot
        self.layout.AddRow(self.addButton)
        self.Content = self.layout 

    # Start of the class functions
    def OnFormClosed(self, sender, e):
        pass

    def AddButtonClick(self, sender, e):
        new_row = RowControl.RowControl(0)
        self.dot_type_label = forms.Label(Text = '花点类型：')
        self.layout.AddRow(self.dot_type_label)
        self.layout.AddRow(new_row)
        self.layout.Create()
        self.Content = self.layout
        

if __name__ == "__main__":
    dialog = FritDialog();
    # rc = dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    Rhino.UI.EtoExtensions.ShowSemiModal(dialog, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)