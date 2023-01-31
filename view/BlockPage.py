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
from model.ChooseZone import con
import os
import clr
from System.Drawing import Color
clr.AddReference("System.Xml")
import System.Xml as XML
from scriptcontext import doc
from System.Windows.Forms import *
import Rhino.UI
from System import Environment
from model.LoadData import Save
from model.XMLPATH import XMLPATH
from Rhino.UI import * 
from Eto.Forms import * 
from Eto.Drawing import * 
from frits import FritType
from model.HoleFrits import HoleArrangeType
from model.RowFrits import RowArrangeType
from model.ChooseZone import con

class BlockPage(forms.TabPage):
    
    # .net 必须使用__new__显示调用构造函数！！！
    def __new__(cls, *args):
        return forms.TabPage.__new__(cls)    

    def __init__(self, page_id):
        self.page_id = page_id
        self.Text = '第三遮阳区'
        self.panel = forms.Scrollable()
        self.panel.Padding = drawing.Padding(10)
        self.row_num = 1
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
        self.fill_btn1 = forms.Button(Text='手动添加新行(row)')
        self.fill_btn1.Size = Size(120, 30)
        self.fill_btn1.Click += self.AddButtonClick_row
        self.fill_btn2 = forms.Button(Text='手动添加新行(hole)')
        self.fill_btn2.Size = Size(120, 30)
        self.fill_btn2.Click += self.AddButtonClick_hole
        self.insert_btn = forms.Button(Text='一键填充')
        self.insert_btn.Size = Size(120, 30)
        self.insert_btn.Click += self.InsertButtonClick
        self.xml_btn = forms.Button(Text='导出XML文件')
        self.xml_btn.Size = Size(120, 30)
        self.xml_btn.Click += self.XMLButtonClick
        #groupbox1
        self.m_groupbox = forms.GroupBox(Text = '参考线示意图')
        self.m_groupbox.Padding = drawing.Padding(5)
 
        grouplayout = forms.DynamicLayout()
        grouplayout.Spacing = Size(3, 3)
        current_path1 = os.getcwd()
 
        self.img = ImageView()
        if con.type == "88LF":
            self.img.Image = Bitmap("C:\\ico\\0088.png")
        elif con.type == "76720LFW00027": 
            self.img.Image = Bitmap("C:\\ico\\76720.png")
        elif con.type == "00841LFW00001": 
            self.img.Image = Bitmap("C:\\ico\\00841.png")
        elif con.type == "00399LFW00012": 
            self.img.Image = Bitmap("C:\\ico\\00399.png")
        elif con.type == "00792LFW000023": 
            self.img.Image = Bitmap("C:\\ico\\00792.png")
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
        self.layout.AddRow(self.m_groupbox2, self.m_groupbox)
        #self.layout.AddRow(self.insert_btn,self.xml_btn, None)
        self.layout.EndVertical()
        self.layout.AddSeparateRow(self.fill_label, None)
        self.layout.AddSeparateRow(padding=drawing.Padding(20, 0, 0, 0), controls=[self.insert_btn,self.fill_btn1,self.fill_btn2,self.xml_btn, None])
        ##self.layout.AddSeparateRow(padding=drawing.Padding(20, 0, 0, 0), controls=[self.fill_btn,  None])
        
        if len(self.model.rows) == 0:
            try:
                file_name = Save.path_data
                rows = RowFrits.load_block_xml(file_name, self.model)
                holes = HoleFrits.load_block_xml(file_name, self.model)
                for i in range(len(rows)):
                    self.model.rows.append(rows[i])
                for i in range(len(holes)):
                    self.model.holes.append(holes[i])
            except:
                pass
        del self.row_panels[:]
        del self.hole_panels[:]
        self.layout.BeginVertical()
        for i in range(len(self.model.rows)):
            rpanel = RowConfigPanel(self, self.model.rows[i])
            self.layout.AddRow(rpanel)
            self.row_panels.append(rpanel)
        for i in range(len(self.model.holes)):
            hpanel = HoleConfigPanel(self, self.model.holes[i])
            self.layout.AddRow(hpanel)
            self.hole_panels.append(hpanel)
        self.layout.EndVertical()
        self.layout.AddSpace()
        self.panel.Content = self.layout
        self.Content = self.panel
    

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


    def AddButtonClick_row(self, sender, e):
        self.row_num = len(self.model.rows)
        self.row_num += 1
        row_frits = RowFrits(len(self.model.rows), self.model)
        self.model.rows.append(row_frits)
        self.create_interface()
        
    def AddButtonClick_hole(self, sender, e):
        self.hole_num = len(self.model.holes)
        self.hole_num += 1
        hole_frits = HoleFrits(len(self.model.holes), self.model)
        self.model.holes.append(hole_frits)
        self.create_interface()
    
    
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
            #row_id = xml.CreateAttribute('id')
            row.SetAttribute('id',str(i))
            if self.model.rows[i].dot_type == FritType.CIRCLE_DOT:
                type = xml.CreateAttribute('type')
                type.Value = 'circle'
                row.Attributes.Append(type)
                if self.model.rows[i].arrange_type == RowArrangeType.HEADING:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'heading'
                    row.Attributes.Append(arrange)
                else:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'cross'
                    row.Attributes.Append(arrange)
                #print('圆形') row.circle_config.r
                r = xml.CreateElement('r')
                r.InnerText = str(self.model.rows[i].circle_config.r)
                row.AppendChild(r)
                
                step = xml.CreateElement('stepping')
                step.InnerText = str(self.model.rows[i].stepping)
                row.AppendChild(step)
                
                position = xml.CreateElement('position')
                position.InnerText = str(self.model.rows[i].position)
                row.AppendChild(position)
                if self.model.rows[i].is_transit:
                    transit = xml.CreateElement('transit')
                    transit.InnerText = str(self.model.rows[i].transit_radius)
                    row.AppendChild(transit)
                    
                    transit_position = xml.CreateElement('transitposition')
                    transit_position.InnerText = str(self.model.rows[i].transit_position)
                    row.AppendChild(transit_position)
            elif self.model.rows[i].dot_type == FritType.ROUND_RECT:
                type = xml.CreateAttribute('type')
                type.Value = 'roundrect'
                row.Attributes.Append(type)
                if self.model.rows[i].arrange_type == RowArrangeType.HEADING:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'heading'
                    row.Attributes.Append(arrange)
                else:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'cross'
                    row.Attributes.Append(arrange)
                #print('圆形') row.circle_config.r
                r = xml.CreateElement('r')
                r.InnerText = str(self.model.rows[i].round_rect_config.r)
                row.AppendChild(r)
                
                k = xml.CreateElement('k')
                k.InnerText = str(self.model.rows[i].round_rect_config.k)
                row.AppendChild(k)
                
                step = xml.CreateElement('stepping')
                step.InnerText = str(self.model.rows[i].stepping)
                row.AppendChild(step)
                
                position = xml.CreateElement('position')
                position.InnerText = str(self.model.rows[i].position)
                row.AppendChild(position)
                if self.model.rows[i].is_transit:
                    transit = xml.CreateElement('transit')
                    transit.InnerText = str(self.model.rows[i].transit_radius)
                    row.AppendChild(transit)
                    
                    transit_position = xml.CreateElement('transitposition')
                    transit_position.InnerText = str(self.model.rows[i].transit_position)
                    row.AppendChild(transit_position)
            elif self.model.rows[i].dot_type == FritType.ARC_CIRCLE:
                type = xml.CreateAttribute('type')
                type.Value = 'arcdot'
                row.Attributes.Append(type)
                if self.model.rows[i].arrange_type == RowArrangeType.HEADING:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'heading'
                    row.Attributes.Append(arrange)
                else:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'cross'
                    row.Attributes.Append(arrange)
                #print('圆形') row.circle_config.r
                lr = xml.CreateElement('lr')
                lr.InnerText = str(self.model.rows[i].arc_config.lr)
                row.AppendChild(lr)
                
                sr = xml.CreateElement('sr')
                sr.InnerText = str(self.model.rows[i].arc_config.sr)
                row.AppendChild(sr)
                
                angle = xml.CreateElement('angle')
                angle.InnerText = str(self.model.rows[i].arc_config.angle)
                row.AppendChild(angle)
                
                step = xml.CreateElement('stepping')
                step.InnerText = str('2.2')
                row.AppendChild(step)
                
                position = xml.CreateElement('position')
                position.InnerText = str('0.2')
                row.AppendChild(position)
                if self.model.rows[i].is_transit:
                    
                    transit = xml.CreateElement('transit')
                    transit.InnerText = str(self.model.rows[i].transit_radius)
                    row.AppendChild(transit)
                    
                    transit_position = xml.CreateElement('transitposition')
                    transit_position.InnerText = str(self.model.rows[i].transit_position)
                    row.AppendChild(transit_position)
            elif self.model.rows[i].dot_type == FritType.TRI_ARC:
                type = xml.CreateAttribute('type')
                type.Value = 'triarc'
                row.Attributes.Append(type)
                if self.model.rows[i].arrange_type == RowArrangeType.HEADING:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'heading'
                    row.Attributes.Append(arrange)
                else:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'cross'
                    row.Attributes.Append(arrange)
                #print('圆形') row.circle_config.r
                lr = xml.CreateElement('lr')
                lr.InnerText = str(self.model.rows[i].tri_arc_config.lr)
                row.AppendChild(lr)
                
                sr = xml.CreateElement('sr')
                sr.InnerText = str(self.model.rows[i].tri_arc_config.sr)
                row.AppendChild(sr)
                
                angle = xml.CreateElement('angle')
                angle.InnerText = str(self.model.rows[i].tri_arc_config.angle)
                row.AppendChild(angle)
                
                step = xml.CreateElement('stepping')
                step.InnerText = str('2.2')
                row.AppendChild(step)
                
                position = xml.CreateElement('position')
                position.InnerText = str('0.2')
                row.AppendChild(position)
                
                if self.model.rows[i].is_transit:
                    transit = xml.CreateElement('transit')
                    transit.InnerText = str(self.model.rows[i].transit_radius)
                    row.AppendChild(transit)
                    
                    transit_position = xml.CreateElement('transitposition')
                    transit_position.InnerText = str(self.model.rows[i].transit_position)
                    row.AppendChild(transit_position)
        #f_path = XMLPATH()
        #xml.Save(f_path)
        for i in range(len(self.model.holes)):
            print(i)
            hole = xml.CreateElement('hole')
            block.AppendChild(hole)
            #row_id = xml.CreateAttribute('id')
            hole.SetAttribute('id',str(i))
            if self.model.holes[i].dot_type == FritType.CIRCLE_DOT:
                type = xml.CreateAttribute('type')
                type.Value = 'circle'
                hole.Attributes.Append(type)
                if self.model.holes[i].arrange_type == RowArrangeType.HEADING:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'heading'
                    hole.Attributes.Append(arrange)
                else:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'cross'
                    hole.Attributes.Append(arrange)
                #print('圆形') row.circle_config.r
                r = xml.CreateElement('r')
                r.InnerText = str(self.model.holes[i].circle_config.r)
                hole.AppendChild(r)
                
                #k = xml.CreateElement('k')
                #k.InnerText = str(self.model.rows[i].circle_config.k)
                #row.AppendChild(k)
                
                step = xml.CreateElement('stepping')
                step.InnerText = str(self.model.holes[i].stepping)
                hole.AppendChild(step)
                
                vspace = xml.CreateElement('vspace')
                vspace.InnerText = str(self.model.holes[i].vspace)
                hole.AppendChild(vspace)
                
                fposition = xml.CreateElement('fposition')
                fposition.InnerText = str(self.model.holes[i].first_line_position)
                hole.AppendChild(fposition)
                
            elif self.model.holes[i].dot_type == FritType.ROUND_RECT:
                type = xml.CreateAttribute('type')
                type.Value = 'roundrect'
                hole.Attributes.Append(type)
                if self.model.holes[i].arrange_type == RowArrangeType.HEADING:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'heading'
                    hole.Attributes.Append(arrange)
                else:
                    arrange = xml.CreateAttribute('arrange')
                    arrange.Value = 'cross'
                    hole.Attributes.Append(arrange)
                #print('圆形') row.circle_config.r
                r = xml.CreateElement('r')
                r.InnerText = str(self.model.holes[i].round_rect_config.r)
                hole.AppendChild(r)
                
                k = xml.CreateElement('k')
                k.InnerText = str(self.model.holes[i].round_rect_config.k)
                hole.AppendChild(k)
                
                step = xml.CreateElement('stepping')
                step.InnerText = str(self.model.holes[i].stepping)
                hole.AppendChild(step)
                
                vspace = xml.CreateElement('vspace')
                vspace.InnerText = str(self.model.holes[i].vspace)
                hole.AppendChild(vspace)
                
                fposition = xml.CreateElement('fposition')
                fposition.InnerText = str(self.model.holes[i].first_line_position)
                hole.AppendChild(fposition)
                
        f_path = XMLPATH()
        xml.Save(f_path)
        
        
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
