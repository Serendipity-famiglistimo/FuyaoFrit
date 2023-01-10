#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, August 22nd 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import Rhino
import math
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
import Eto.Forms as forms
import Eto.Drawing as drawing
from Eto.Drawing import Size, Font, FontStyle
import Rhino as rc
import Grasshopper as gh
import scriptcontext
import copy
import System.Guid
from Rhino.UI import * 
from Eto.Forms import * 
from Eto.Drawing import * 
import clr
import re
import datetime
import sys
clr.AddReference("System.Management")
clr.AddReference("System")
import System as st
import System.Management as SM
import System.Text as txt
import System.Security.Cryptography as ct
import System.IO as io
import os
import clr
#from RowControl import RowControl
from System.Drawing import Color
clr.AddReference("System.Xml")
import System.Xml as XML
from scriptcontext import doc
from System.Windows.Forms import *
import Rhino.UI
from System import Environment

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
from model.dzBlockZone import dzBlockZone
import model.BlockZone
import model.dzBlockZone
reload(model.BlockZone)
reload(model.dzBlockZone)
from model.RowFrits import RowFrits
from model.HoleFrits import HoleFrits
from RowConfigPanel import RowConfigPanel
from dzConfigPanel import DZ_ConfigPanel
from HoleConfigPanel import HoleConfigPanel
from Rhino.UI import * 
from Eto.Forms import * 
from Eto.Drawing import * 
import os
import clr
from LoadData import Save
clr.AddReference("System.Xml")
clr.AddReference("System")
import System.Xml as XML
from System import Environment

def XMLPATH():
    file_name = "";
    save_file_dialog = Rhino.UI.SaveFileDialog()
    save_file_dialog.FileName = ".xml"
    save_file_dialog.Filter = "(*.xml)"
    #save_file_dialog.InitialDirectory = \
    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)
    if save_file_dialog.ShowDialog() == DialogResult.OK:
        file_name = save_file_dialog.FileName
    print(file_name)
    return file_name

class dzBlockPage(forms.TabPage):
    
    # .net 必须使用__new__显示调用构造函数！！！
    def __new__(cls, *args):
        return forms.TabPage.__new__(cls)    

    def __init__(self, page_id):
        self.page_id = page_id
        self.Text = '块状区域-大众'
        self.panel = forms.Scrollable()
        self.panel.Padding = drawing.Padding(10)
        self.model = dzBlockZone()
        self.row_panels = list()
        self.hole_panels = list()
        self.create_interface()
        self.pick_event_btn = None
        
    def create_interface(self):
        
        self.panel.RemoveAll()
        # Create a table layout and add all the controls
        self.layout = forms.DynamicLayout()
        self.pick_label = forms.Label(Text='- 拾取几何轮廓', Font = Font('Microsoft YaHei', 12.))
        

        self.outer_btn = forms.Button(Text='选取参考线1')
        self.outer_btn.Size = Size(100, 30)
        self.outer_btn.Click += self.PickReferCurve
        self.outer_btn.Tag = 'outer_btn'
        self.flip_check3 = forms.CheckBox()
        self.flip_check3.Tag = 'is_outer_flip'
        self.flip_check3.CheckedChanged += self.FlipCheckClick
        self.flip_check3.Text = '是否反转该曲线'
        self.is_pick_label3 = forms.Label()
        if self.model.curves[0] is None:
            self.is_pick_label3.Text = '未选择曲线'
            self.is_pick_label3.TextColor = drawing.Color.FromArgb(255, 0, 0)
        else:
            self.is_pick_label3.Text = '选择了曲线{0}.'.format(self.model.curves[0])
            self.is_pick_label3.TextColor = drawing.Color.FromArgb(44,162,95)
        
        
        
        
        self.inner_btn = forms.Button(Text='选取参考线2')
        self.inner_btn.Size = Size(100, 30)
        self.inner_btn.Click += self.PickReferCurve
        self.inner_btn.Tag = 'inner_btn'
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
            
            
            
        self.refer_btn = forms.Button(Text='选取参考线3')
        self.refer_btn.Size = Size(100, 30)
        self.refer_btn.Click += self.PickReferCurve
        self.refer_btn.Tag = 'refer_btn'
        self.flip_check = forms.CheckBox()
        self.flip_check.Tag = 'is_refer_flip'
        self.flip_check.CheckedChanged += self.FlipCheckClick
        self.flip_check.Text = '是否反转该曲线'
        self.is_pick_label = forms.Label()
        if self.model.curves[2] is None:
            self.is_pick_label.Text = '未选择曲线'
            self.is_pick_label.TextColor = drawing.Color.FromArgb(255, 0, 0)
        else:
            self.is_pick_label.Text = '选择了曲线{0}.'.format(self.model.curves[2])
            self.is_pick_label.TextColor = drawing.Color.FromArgb(44,162,95)
            
            
        self.top_btn = forms.Button(Text='选取参考线4')
        self.top_btn.Size = Size(100, 30)
        self.top_btn.Click += self.PickReferCurve
        self.top_btn.Tag = 'top_btn'
        self.flip_check4 = forms.CheckBox()
        self.flip_check4.Tag = 'is_top_flip'
        self.flip_check4.CheckedChanged += self.FlipCheckClick
        self.flip_check4.Text = '是否反转该曲线'
        self.is_pick_label4 = forms.Label()
        if self.model.curves[3] is None:
            self.is_pick_label4.Text = '未选择曲线'
            self.is_pick_label4.TextColor = drawing.Color.FromArgb(255, 0, 0)
        else:
            self.is_pick_label4.Text = '选择了曲线{0}.'.format(self.model.curves[3])
            self.is_pick_label4.TextColor = drawing.Color.FromArgb(44,162,95)
            
            
        self.bottom_btn = forms.Button(Text='选取参考线5')
        self.bottom_btn.Size = Size(100, 30)
        self.bottom_btn.Click += self.PickReferCurve
        self.bottom_btn.Tag = 'bottom_btn'
        self.flip_check5 = forms.CheckBox()
        self.flip_check5.Tag = 'is_bottom_flip'
        self.flip_check5.CheckedChanged += self.FlipCheckClick
        self.flip_check5.Text = '是否反转该曲线'
        self.is_pick_label5 = forms.Label()
        if self.model.curves[4] is None:
            self.is_pick_label5.Text = '未选择曲线'
            self.is_pick_label5.TextColor = drawing.Color.FromArgb(255, 0, 0)
        else:
            self.is_pick_label5.Text = '选择了曲线{0}.'.format(self.model.curves[4])
            self.is_pick_label5.TextColor = drawing.Color.FromArgb(44,162,95)
            
            
        self.bottom1_btn = forms.Button(Text='选取参考线6')
        self.bottom1_btn.Size = Size(100, 30)
        self.bottom1_btn.Click += self.PickReferCurve
        self.bottom1_btn.Tag = 'bottom1_btn'
        self.flip_check6 = forms.CheckBox()
        self.flip_check6.Tag = 'is_bottom1_flip'
        self.flip_check6.CheckedChanged += self.FlipCheckClick
        self.flip_check6.Text = '是否反转该曲线'
        self.is_pick_label6 = forms.Label()
        if self.model.curves[5] is None:
            self.is_pick_label6.Text = '未选择曲线'
            self.is_pick_label6.TextColor = drawing.Color.FromArgb(255, 0, 0)
        else:
            self.is_pick_label6.Text = '选择了曲线{0}.'.format(self.model.curves[5])
            self.is_pick_label6.TextColor = drawing.Color.FromArgb(44,162,95)


        
        self.fill_label = forms.Label(Text='- 设置或加载填充规则', Font = Font('Microsoft YaHei', 12.))
        self.fill_btn = forms.Button(Text='手动添加新行')
        self.fill_btn.Size = Size(100, 30)
        self.fill_btn.Click += self.AddButtonClick
        self.insert_btn = forms.Button(Text='一键填充')
        self.insert_btn.Size = Size(100, 30)
        self.insert_btn.Click += self.InsertButtonClick
        self.xml_btn = forms.Button(Text='导出XML文件')
        self.xml_btn.Size = Size(100, 30)
        self.xml_btn.Click += self.XMLButtonClick
        
        #groupbox1
        self.m_groupbox = forms.GroupBox(Text = '参考线示意图')
        self.m_groupbox.Padding = drawing.Padding(5)
 
        grouplayout = forms.DynamicLayout()
        grouplayout.Spacing = Size(3, 3)
        current_path1 = os.getcwd()
 
        self.img = ImageView()
        self.img.Image = Bitmap("C:\\ico\\dz_block.png")
        grouplayout.AddRow(self.img.Image)
        self.m_groupbox.Content = grouplayout
        #groupbox2
        self.m_groupbox2 = forms.GroupBox(Text = '参考线示意图')
        self.m_groupbox2.Padding = drawing.Padding(5)
 
        grouplayout = forms.DynamicLayout()
        grouplayout.Spacing = Size(3, 3)
        grouplayout.AddRow(self.pick_label)
        grouplayout.AddRow(self.outer_btn)
        grouplayout.AddRow(self.flip_check3)
        grouplayout.AddRow(self.is_pick_label3)
        
        grouplayout.AddRow(self.inner_btn)
        grouplayout.AddRow(self.flip_check2)
        grouplayout.AddRow(self.is_pick_label2)
        
        grouplayout.AddRow(self.refer_btn)
        grouplayout.AddRow(self.flip_check)
        grouplayout.AddRow(self.is_pick_label)
        
        grouplayout.AddRow(self.top_btn)
        grouplayout.AddRow(self.flip_check4)
        grouplayout.AddRow(self.is_pick_label4)
        
        grouplayout.AddRow(self.bottom_btn)
        grouplayout.AddRow(self.flip_check5)
        grouplayout.AddRow(self.is_pick_label5)
        
        grouplayout.AddRow(self.bottom1_btn)
        grouplayout.AddRow(self.flip_check6)
        grouplayout.AddRow(self.is_pick_label6)
        
        
        self.m_groupbox2.Content = grouplayout
        self.layout.DefaultSpacing = drawing.Size(8, 8)
        #        self.layout.AddSeparateRow(self.pick_label, None)
        self.layout.BeginVertical(padding=drawing.Padding(20, 0, 0, 0))
        self.layout.AddRow(self.m_groupbox2, self.m_groupbox)
        self.layout.EndVertical()
        self.layout.AddSeparateRow(self.fill_label, None)
        self.layout.AddSeparateRow(padding=drawing.Padding(20, 0, 0, 0), controls=[self.fill_btn,self.insert_btn,self.xml_btn,None])
        #self.layout.AddRow(self.fill_btn,self.insert_btn,self.xml_btn, None)
        #self.layout.AddSeparateRow(padding=drawing.Padding(20, 0, 0, 0), controls=[self.fill_btn,self.insert_btn,self.xml_btn  None])
        if len(self.model.rows) == 0:
            try:
                file_name = Save.path_data
                rows = RowFrits.load_dz_block_xml(file_name, self.model)
                holes = HoleFrits.load_block_xml(file_name, self.model)
                self.model.holes = holes
                self.model.rows = rows
            except:
                pass
            #DZ_ConfigPanel
        del self.row_panels[:]
        self.layout.BeginVertical()
        for i in range(len(self.model.rows)):
            rpanel = DZ_ConfigPanel(self, self.model.rows[i])
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
            
        #else:
            #self.layout.BeginVertical()
            #self.warn_label = forms.Label(Text='---未加载块状配置---', Font = Font('Microsoft YaHei', 12.), TextColor = drawing.Color.FromArgb(255, 0, 0))
            #self.layout.AddRow(self.warn_label)
            #print('获取文件路径失败')
            #self.layout.EndVertical()

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
        self.row_num = len(self.model.rows)
        self.row_num += 1
        row_frits = RowFrits(len(self.model.rows), self.model)
       
        self.model.rows.append(row_frits)
        
        # row_frits.band_model = self.model  # type: ignore
        self.create_interface()
    
    def InsertButtonClick(self, sender, e):
        self.clear_dots()
        HoleFrits(1,self.model).dazhong_fill_dots()
        
    def XMLButtonClick(self, sender, e):
        xml = XML.XmlDocument()
        xml_declaration = xml.CreateXmlDeclaration("1.0","UTF-8","yes")
        xml.AppendChild(xml_declaration)
        set = xml.CreateElement('setting')
        block = xml.CreateElement('block')
        set.AppendChild(block)
        xml.AppendChild(set)
        for i in range(len(self.model.rows)):
            print(i)
            row = xml.CreateElement('row')
            block.AppendChild(row)
            row.SetAttribute('id',str(i))
            
            r1 = xml.CreateElement('cross_k1')
            r1.InnerText = str(self.model.rows[i].circle_config.cross_k1)
            row.AppendChild(r1)
            
            r2 = xml.CreateElement('cross_position3')
            r2.InnerText = str(self.model.rows[i].circle_config.cross_position3)
            row.AppendChild(r2)
            
            r3 = xml.CreateElement('cross_position2')
            r3.InnerText = str(self.model.rows[i].circle_config.cross_position2)
            row.AppendChild(r3)
            
            r4 = xml.CreateElement('cross_position1')
            r4.InnerText = str(self.model.rows[i].circle_config.cross_position1)
            row.AppendChild(r4)
            
            r5 = xml.CreateElement('cross_k2')
            r5.InnerText = str(self.model.rows[i].circle_config.cross_k2)
            row.AppendChild(r5)
            
            r6 = xml.CreateElement('cross_round_rect_r')
            r6.InnerText = str(self.model.rows[i].circle_config.cross_round_rect_r)
            row.AppendChild(r6)
            
            r7 = xml.CreateElement('cross_r2')
            r7.InnerText = str(self.model.rows[i].circle_config.cross_r2)
            row.AppendChild(r7)
            
            r8 = xml.CreateElement('cross_r1')
            r8.InnerText = str(self.model.rows[i].circle_config.cross_r1)
            row.AppendChild(r8)
            
            r9 = xml.CreateElement('slope_r1')
            r9.InnerText = str(self.model.rows[i].circle_config.slope_r1)
            row.AppendChild(r9)
            
            r10 = xml.CreateElement('slope_r2')
            r10.InnerText = str(self.model.rows[i].circle_config.slope_r2)
            row.AppendChild(r10)
            
            r11 = xml.CreateElement('slope_r3')
            r11.InnerText = str(self.model.rows[i].circle_config.slope_r3)
            row.AppendChild(r11)
            
            r12 = xml.CreateElement('slope_r4')
            r12.InnerText = str(self.model.rows[i].circle_config.slope_r4)
            row.AppendChild(r12)
            
            stepping = xml.CreateElement('horizontal')
            stepping.InnerText = str(self.model.rows[i].stepping)
            row.AppendChild(stepping)
            
            position = xml.CreateElement('vertical')
            position.InnerText = str(self.model.rows[i].position)
            row.AppendChild(position)
        f_path = XMLPATH()
        xml.Save(f_path)
    
    def FlipCheckClick(self, sender, e):
        if sender.Tag == 'is_outer_flip':
            self.model.is_flip[0] = self.flip_check3.Checked
        elif sender.Tag == 'is_inner_flip':
            self.model.is_flip[1] = self.flip_check2.Checked
        elif sender.Tag == 'is_refer_flip':
            self.model.is_flip[2] = self.flip_check.Checked
        elif sender.Tag == 'is_top_flip':
            self.model.is_flip[3] = self.flip_check.Checked
        elif sender.Tag == 'is_bottom_flip':
            self.model.is_flip[4] = self.flip_check.Checked
        elif sender.Tag == 'is_bottom1_flip':
            self.model.is_flip[5] = self.flip_check.Checked
    
    def OnGetRhinoObjects(self, sender, e):
        objectId = rs.GetCurveObject("Select curve:")
        if objectId is None: 
            print("Warning: No curve is selected")
            return
      
        crv = objectId[0]
        if self.pick_event_btn.Tag == 'outer_btn':
            self.model.curves[0] = crv
        elif self.pick_event_btn.Tag == 'inner_btn':
            self.model.curves[1] = crv
        elif self.pick_event_btn.Tag == 'refer_btn':
            self.model.curves[2] = crv
        elif self.pick_event_btn.Tag == 'top_btn':
            self.model.curves[3] = crv
        elif self.pick_event_btn.Tag == 'bottom_btn':
            self.model.curves[4] = crv
        elif self.pick_event_btn.Tag == 'bottom1_btn':
            self.model.curves[5] = crv
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