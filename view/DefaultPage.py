#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, August 18th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import imp
import Rhino
import Rhino as rc
import Eto.Forms as forms
import Eto.Drawing as drawing
import BandPage
import BlockPage
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
from model.BlockZone import BlockZone
import model.BlockZone
reload(model.BlockZone)
import utils
reload(utils)
from model.RowFrits import RowFrits
from model.HoleFrits import HoleFrits
from RowConfigPanel import RowConfigPanel
from HoleConfigPanel import HoleConfigPanel
from Eto.Drawing import Size, Font, FontStyle
from LoadData import Save
import BlockPage

class control():
    def __init__(self):
        self.type = '大众算法'
con = control()

class DefaultPage(forms.TabPage):
    def __init__(self):
        forms.TabPage.__init__(self)
        self.type = '大众算法'
        self.panel = forms.Scrollable()
        self.panel.Padding = drawing.Padding(10)
        self.create(self.type)
        
        
    def create(self,type):
        self.Text = '基本属性'
        self.layout = forms.DynamicLayout()
        self.pick_label = forms.Label(Text='选择填充算法:', Font=Font('Microsoft YaHei', 12.))
        self.list = forms.RadioButtonList()
        self.list.DataStore = ['大众算法', '奥迪算法', '其他']
        self.list.Orientation = forms.Orientation.Vertical
        self.list.SelectedIndex = self.list.DataStore.index(type)
        self.list.SelectedIndexChanged += self.typeselected
        self.load_btn = forms.Button(Text='加载填充规则')
        self.load_btn.Size = Size(100, 30)
        self.load_btn.Click += self.LoadButtonClick
        
        self.layout.DefaultSpacing = drawing.Size(8, 8)
        self.layout.AddSeparateRow(self.pick_label, None, None)
        self.layout.AddSeparateRow(self.list, None, None)
        self.layout.AddSeparateRow(self.load_btn, None, None)
        
        
        
        
        
        self.layout.AddSpace()
        self.panel.Content = self.layout
        self.Content = self.panel
        
        

    def typeselected(self, sender, e):
        print('typeselected被调用为'+con.type)
        if self.list.SelectedIndex == 0:
            self.type = '大众算法'
            
        elif self.list.SelectedIndex == 1:
            self.type = '奥迪算法'
            
        elif self.list.SelectedIndex == 2:
            self.type = '其他'
        con.type = self.type
        self.create(self.type)
        print('DEF界面下传的self'+con.type)
        
        
    def LoadButtonClick(self, sender, e):
        # 清空现有的填充规则
        fd = Rhino.UI.OpenFileDialog()
        fd.Title = '加载规则文件'
        fd.Filter = '规则文件 (*.xml)'
        fd.MultiSelect = False
        if fd.ShowOpenDialog():
            Save.path_data = fd.FileName
