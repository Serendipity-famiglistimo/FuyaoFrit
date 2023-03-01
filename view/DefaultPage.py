#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, August 18th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import Eto.Forms as forms
from Eto.Drawing import Size, Font, FontStyle
from model.LoadData import Save
import Rhino
import Eto.Drawing as drawing

class DefaultPage(forms.TabPage):
    def __init__(self):
        forms.TabPage.__init__(self)
        #self.type = '大众算法'
        self.panel = forms.Scrollable()
        #self.Topmost = True
        self.panel.Padding = drawing.Padding(10)
        self.create()
        
        
    def create(self):
        self.Text = '基本属性'
        self.layout = forms.DynamicLayout()
        self.pick_label = forms.Label(Text='选择填充规则:', Font=Font('Microsoft YaHei', 12.))
        
        #self.list.SelectedIndexChanged += self.typeselected
        self.load_btn = forms.Button(Text='加载填充规则')
        self.load_btn.Size = Size(100, 30)
        self.load_btn.Click += self.LoadButtonClick
        
        self.layout.DefaultSpacing = drawing.Size(8, 8)
        self.layout.AddSeparateRow(self.pick_label, None, None)
        #self.layout.AddSeparateRow(self.list, None, None)
        self.layout.AddSeparateRow(self.load_btn, None, None)
        
        
        
        
        
        self.layout.AddSpace()
        self.panel.Content = self.layout
        self.Content = self.panel
        
        
    def LoadButtonClick(self, sender, e):
        # 清空现有的填充规则
#        fd = Rhino.UI.OpenFileDialog()
#        #fd.Topmost = True
#        fd.Title = '加载规则文件'
#        fd.Filter = '规则文件 (*.xml)'
#        fd.MultiSelect = False
#        if fd.ShowOpenDialog():
#            Save.path_data = fd.FileName
        try:
            fd = forms.OpenFileDialog()
        except:
            print(1)
        try:
            fd.Title = '加载规则文件'
        except:
            print(2)
        try:
            filter = forms.FileFilter('XML file',".xml")
        except:
            print(3)
        try:
            fd.Filters.Add(filter)
        except:
            print(4)
        try:
            fd.MultiSelect = False
        except:
            print(5)
        try:
            fd.ShowDialog(Rhino.UI.RhinoEtoApp.MainWindow)##   
        except:
            print(6)
        try:
            Save.path_data = fd.FileName
            print(fd.FileName)
        except:
            print('文件路径获取失败')


