#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, August 22nd 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import imp
import Rhino
import Rhino as rc
import Eto.Forms as forms
import Eto.Drawing as drawing
from model.HoleFrits import HoleFrits
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
from Eto.Drawing import Size, Font, FontStyle
from model.BlockZone import BlockZone
import model.BlockZone
reload(model.BlockZone)
from model.RowFrits import RowFrits
from model.HoleFrits import HoleFrits
from RowConfigPanel import RowConfigPanel
from HoleConfigPanel import HoleConfigPanel
from LoadData import Save
from Rhino.UI import * 
from Eto.Forms import * 
from Eto.Drawing import * 
import os
import clr

class BlockPage(forms.TabPage):
    
    # .net 必须使用__new__显示调用构造函数！！！
    def __new__(cls, *args):
        return forms.TabPage.__new__(cls)    

    def __init__(self, page_id):
        self.page_id = page_id
        self.Text = '块状区域'
        self.panel = forms.Scrollable()
        self.panel.Padding = drawing.Padding(10)
        self.model = BlockZone()
        self.row_panels = list()
        self.hole_panels = list()
        self.create_interface()
        self.pick_event_btn = None
        
    def create_interface(self):
        
        self.panel.RemoveAll()
        # Create a table layout and add all the controls
        self.layout = forms.DynamicLayout()
        self.pick_label = forms.Label(Text='- 拾取几何轮廓', Font = Font('Microsoft YaHei', 12.))
        self.refer_btn = forms.Button(Text='选取参考线1')
        self.refer_btn.Size = Size(100, 30)
        self.refer_btn.Click += self.PickReferCurve
        self.refer_btn.Tag = 'refer_btn'

        # checkbox
        self.flip_check = forms.CheckBox()
        self.flip_check.Tag = 'is_refer_flip'
        self.flip_check.CheckedChanged += self.FlipCheckClick
        self.flip_check.Text = '是否反转该曲线'
        self.is_pick_label = forms.Label()
        if self.model.curves[0] is None:
            self.is_pick_label.Text = '未选择曲线'
            self.is_pick_label.TextColor = drawing.Color.FromArgb(255, 0, 0)
        else:
            self.is_pick_label.Text = '选择了曲线{0}.'.format(self.model.curves[0])
            self.is_pick_label.TextColor = drawing.Color.FromArgb(44,162,95)

        self.inner_btn = forms.Button(Text='选取参考线2')
        self.inner_btn.Size = Size(100, 30)
        self.inner_btn.Click += self.PickReferCurve
        self.inner_btn.Tag = 'inner_btn'

        # checkbox
        self.flip_check2 = forms.CheckBox()
        self.flip_check2.Tag = 'is_inner_flip'
        self.flip_check2.CheckedChanged += self.FlipCheckClick
        self.flip_check2.Text = '是否反转该曲线'
        self.is_pick_label2 = forms.Label()
        if self.model.curves[1] is None:
            self.is_pick_label2.Text = '未选择曲线'
            self.is_pick_label2.TextColor = drawing.Color.FromArgb(255, 0, 0)
        else:
            self.is_pick_label2.Text = '选择了曲线{0}.'.format(self.model.curves[1])
            self.is_pick_label2.TextColor = drawing.Color.FromArgb(44,162,95)

        self.outer_btn = forms.Button(Text='选取参考线3')
        self.outer_btn.Size = Size(100, 30)
        self.outer_btn.Click += self.PickReferCurve
        self.outer_btn.Tag = 'outer_btn'
        
        # checkbox
        self.flip_check3 = forms.CheckBox()
        self.flip_check3.Tag = 'is_outer_flip'
        self.flip_check3.CheckedChanged += self.FlipCheckClick
        self.flip_check3.Text = '是否反转该曲线'
        self.is_pick_label3 = forms.Label()
        if self.model.curves[2] is None:
            self.is_pick_label3.Text = '未选择曲线'
            self.is_pick_label3.TextColor = drawing.Color.FromArgb(255, 0, 0)
        else:
            self.is_pick_label3.Text = '选择了曲线{0}.'.format(self.model.curves[2])
            self.is_pick_label3.TextColor = drawing.Color.FromArgb(44,162,95)

        self.fill_label = forms.Label(Text='- 设置或加载填充规则', Font = Font('Microsoft YaHei', 12.))
        self.fill_btn = forms.Button(Text='手动添加新行')
        self.fill_btn.Size = Size(100, 30)
        self.fill_btn.Click += self.AddButtonClick

#        self.load_btn = forms.Button(Text='加载填充规则')
#        self.load_btn.Size = Size(100, 30)
#        self.load_btn.Click += self.LoadButtonClick

        self.insert_btn = forms.Button(Text='一键填充')
        self.insert_btn.Size = Size(100, 30)
        self.insert_btn.Click += self.InsertButtonClick
#groupbox1
        self.m_groupbox = forms.GroupBox(Text = '参考线示意图')
        self.m_groupbox.Padding = drawing.Padding(5)
 
        grouplayout = forms.DynamicLayout()
        grouplayout.Spacing = Size(3, 3)
        current_path1 = os.getcwd()
 
        self.img = ImageView()
        self.img.Image = Bitmap(current_path1+"\\ico\\block.png")
        grouplayout.AddRow(self.img.Image)
        self.m_groupbox.Content = grouplayout

#groupbox2
        self.m_groupbox2 = forms.GroupBox(Text = '参考线选取')
        self.m_groupbox2.Padding = drawing.Padding(5)
 
        grouplayout = forms.DynamicLayout()
        grouplayout.Spacing = Size(3, 3)
        grouplayout.AddRow(self.pick_label)
#        self.layout.BeginVertical(padding=drawing.Padding(20, 0, 0, 0))
        grouplayout.AddRow(self.refer_btn)
        grouplayout.AddRow(self.flip_check)
        grouplayout.AddRow(self.is_pick_label)

        grouplayout.AddRow(self.inner_btn)
        grouplayout.AddRow(self.flip_check2)
        grouplayout.AddRow(self.is_pick_label2)

        grouplayout.AddRow(self.outer_btn)
        grouplayout.AddRow(self.flip_check3)
        grouplayout.AddRow(self.is_pick_label3)
        #grouplayout.AddRow(self.img.Image)
        self.m_groupbox2.Content = grouplayout





        self.layout.DefaultSpacing = drawing.Size(8, 8)
        self.layout.AddSeparateRow(self.pick_label, None)
        self.layout.BeginVertical(padding=drawing.Padding(20, 0, 0, 0))
#        self.layout.AddRow(self.refer_btn, None)
#        self.layout.AddRow(self.flip_check, None)
#        self.layout.AddRow(self.is_pick_label, None)
#
#        self.layout.AddRow(self.inner_btn, None)
#        self.layout.AddRow(self.flip_check2, None)
#        self.layout.AddRow(self.is_pick_label2, None)
#
#        self.layout.AddRow(self.outer_btn, None)
#        self.layout.AddRow(self.flip_check3, None)
#        self.layout.AddRow(self.is_pick_label3, None)
        self.layout.AddRow(self.m_groupbox2, self.m_groupbox)
        self.layout.AddRow(self.insert_btn, None)
        self.layout.EndVertical()
        self.layout.AddSeparateRow(self.fill_label, None)
        self.layout.AddSeparateRow(padding=drawing.Padding(20, 0, 0, 0), controls=[self.fill_btn,  None])
        
        
        
        if Save.path_data:
            file_name = Save.path_data
            rows = RowFrits.load_block_xml(file_name, self.model)
            holes = HoleFrits.load_block_xml(file_name, self.model)
            self.model.holes = holes
            self.model.rows = rows
            
            del self.row_panels[:]
            self.layout.BeginVertical()
            for i in range(len(self.model.rows)):
                rpanel = RowConfigPanel(self, self.model.rows[i])
                self.layout.AddRow(rpanel)
                self.row_panels.append(rpanel)
            self.layout.EndVertical()
    
            del self.hole_panels[:]
            self.layout.BeginVertical()
            for i in range(len(self.model.holes)):
                rpanel = HoleConfigPanel(self, self.model.holes[i])
                self.layout.AddRow(rpanel)
                self.hole_panels.append(rpanel)
            self.layout.EndVertical()
        else:
            self.layout.BeginVertical()
            self.warn_label = forms.Label(Text='---未加载块状配置---', Font = Font('Microsoft YaHei', 12.), TextColor = drawing.Color.FromArgb(255, 0, 0))
            self.layout.AddRow(self.warn_label)
            print('获取文件路径失败')
            self.layout.EndVertical()

        # self.block_fill_label = forms.Label(Text='- 填充块状区域', Font = Font('Microsoft YaHei', 12.))
        # self.block_fill_btn = forms.Button(Text='填充块状部分')
        # self.block_fill_btn.Size = Size(100, 30)
        # self.block_fill_btn.Click += self.BlockFillBtnClick

        # self.layout.BeginVertical()
        # self.layout.AddRow(self.block_fill_label, None)
        # self.layout.AddRow(self.block_fill_btn, None)
        # self.layout.EndVertical()


        self.layout.AddSpace()
        self.panel.Content = self.layout
        self.Content = self.panel


    def AddButtonClick(self, sender, e):
        self.row_num += 1
        row_frits = RowFrits(len(self.model.rows), self.model)
       
        self.model.rows.append(row_frits)
        # row_frits.band_model = self.model  # type: ignore
        self.create_interface()
    
    def InsertButtonClick(self, sender, e):
        self.clear_dots()
        self.model.fill_dots()
        self.display = rc.Display.CustomDisplay(True)
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)
        for d in self.model.dots:
            d.draw(self.display, self.display_color)
        
    
    def FlipCheckClick(self, sender, e):
        if sender.Tag == 'is_refer_flip':
            self.model.is_flip[0] = self.flip_check.Checked
        elif sender.Tag == 'is_inner_flip':
            self.model.is_flip[1] = self.flip_check2.Checked
        elif sender.Tag == 'is_outer_flip':
            self.model.is_flip[2] = self.flip_check3.Checked
    
#    def LoadButtonClick(self, sender, e):
#        # 清空现有的填充规则
#        del self.model.rows[:]
#        fd = Rhino.UI.OpenFileDialog()
#        fd.Title = '加载规则文件'
#        fd.Filter = '规则文件 (*.xml)'
#        fd.MultiSelect = False
#        if fd.ShowOpenDialog():
#            file_name = fd.FileName
#            rows = RowFrits.load_block_xml(file_name, self.model)
#            holes = HoleFrits.load_block_xml(file_name, self.model)
#            self.model.holes = holes
#            self.model.rows = rows
#        self.create_interface()
    
    def OnGetRhinoObjects(self, sender, e):
        objectId = rs.GetCurveObject("Select curve:")
        if objectId is None: 
            print("Warning: No curve is selected")
            return
      
        crv = objectId[0]
        if self.pick_event_btn.Tag == 'refer_btn':
            self.model.curves[0] = crv
        elif self.pick_event_btn.Tag == 'inner_btn':
            self.model.curves[1] = crv
        elif self.pick_event_btn.Tag == 'outer_btn':
            self.model.curves[2] = crv
        self.create_interface()
    
    def PickReferCurve(self, sender, e):
        self.pick_event_btn = sender
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnGetRhinoObjects)
    


    def clear_dots(self):
        for r in self.row_panels:
            r.clear_dots()
        for r in self.hole_panels:
            r.clear_dots()
        
    def bake(self):
        for r in self.row_panels:
            r.bake()
        
        for r in self.hole_panels:
            r.bake()
