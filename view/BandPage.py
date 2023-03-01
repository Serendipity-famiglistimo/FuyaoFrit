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
import utils
import os
reload(utils)
import model.BandZone
reload(model.BandZone)
from model.XMLPATH import XMLPATH

from model.LoadData import Save
from Rhino.UI import * 
from Eto.Forms import * 
from Eto.Drawing import * 
import os
import clr
from System.Drawing import Color
clr.AddReference("System.Xml")
import System.Xml as XML
from scriptcontext import doc
from System.Windows.Forms import *
import Rhino.UI
from System import Environment
from frits import FritType
from model.HoleFrits import HoleArrangeType
from model.RowFrits import RowArrangeType
from model.XML_Output import X_Choose
from model.Warning_type import Warning 



class BandPage(forms.TabPage):
    
    # .net 必须使用__new__显示调用构造函数！！！
    def __new__(cls, *args):
        return forms.TabPage.__new__(cls)    

    def __init__(self, page_id, band_type='general'):
        self.page_id = page_id
        self.band_type = band_type
        self.Text = '黑花边'
        if self.band_type == 'bottom':
            self.Text = '底部黑花边'
        print(self.band_type)
        self.row_num = 1
        self.model = BandZone()
        self.row_panels = list()
        X_Choose.Band_XML_OUT = False
        self.panel = forms.Scrollable()
        self.panel.Padding = drawing.Padding(10)
        
        
        self.create_interface()
        
    def create_interface(self):
        
        self.panel.RemoveAll()
        # Create a table layout and add all the controls
        self.layout = forms.DynamicLayout()
        self.pick_label = forms.Label(Text='- 拾取几何轮廓', Font = Font('Microsoft YaHei', 12.))
        self.refer_btn = forms.Button(Text='选取参考轮廓线')
        self.refer_btn.Size = Size(100, 30)
        self.refer_btn.Tag = 'refer_btn'
        self.refer_btn.Click += self.PickReferCurve
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

        self.inner_btn = forms.Button(Text='选取参考线')
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
        
        self.outer_btn = forms.Button(Text='选取外部参考线')
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
        self.add_btn = forms.Button(Text='手动添加新行')
        self.add_btn.Size = Size(100, 30)
        self.add_btn.Click += self.AddButtonClick
        self.fill_btn = forms.Button(Text='一键填充')
        self.fill_btn.Size = Size(100, 30)
        self.fill_btn.Click += self.FillButtonClick
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
        if self.band_type == 'bottom':
            self.img.Image = Bitmap("C:\\ico\\bottom.png")
        else:
            self.img.Image = Bitmap("C:\\ico\\band.png")
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
        
        self.m_groupbox2.Content = grouplayout
        self.layout.DefaultSpacing = drawing.Size(8, 8)
        self.layout.BeginVertical(padding=drawing.Padding(20, 0, 0, 0))
        self.layout.AddRow(self.m_groupbox2, self.m_groupbox)

        self.layout.EndVertical()
        self.layout.AddSeparateRow(self.fill_label, None)
        self.layout.AddSeparateRow(padding=drawing.Padding(20, 0, 0, 0), controls=[self.add_btn,self.fill_btn,self.xml_btn,None])
        
        if len(self.model.rows) == 0:
            try:
                file_name = Save.path_data
                rows = RowFrits.load_band_xml(file_name, self.model, self.band_type)
                for i in range(len(rows)):
                    self.model.rows.append(rows[i])
            except:
                pass
            
        del self.row_panels[:]
        self.layout.BeginVertical()
        for i in range(len(self.model.rows)):
            rpanel = RowConfigPanel(self, self.model.rows[i])
            self.layout.AddRow(rpanel)
            self.row_panels.append(rpanel)
        self.layout.EndVertical()
        self.layout.AddSpace()
        self.panel.Content = self.layout
        self.Content = self.panel
            

    def AddButtonClick(self, sender, e):
        self.row_num = len(self.model.rows)
        self.row_num += 1
        row_frits = RowFrits(len(self.model.rows), self.model)
        self.model.rows.append(row_frits)
        self.create_interface()


    def FillButtonClick(self,sender,e):
        if X_Choose.Band_XML_OUT == False:
            band_dialog = Warning('band')
            band_dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
            if X_Choose.Band_xml == False:
                for row_panel in self.row_panels:
                    row_panel.fill_row_frits(None, None)
            elif X_Choose.Band_xml == True:
                XML_BAND(self.model,self.band_type).run()
                for row_panel in self.row_panels:
                    row_panel.fill_row_frits(None, None)
        elif X_Choose.Band_XML_OUT == True:
            for row_panel in self.row_panels:
                    row_panel.fill_row_frits(None, None)
    def XMLButtonClick(self,sender, e):
        XML_BAND(self.model,self.band_type).run()
        
        
    def FlipCheckClick(self, sender, e):
        if sender.Tag == 'is_refer_flip':
            self.model.is_flip[0] = self.flip_check.Checked
        elif sender.Tag == 'is_inner_flip':
            self.model.is_flip[1] = self.flip_check2.Checked
        elif sender.Tag == 'is_outer_flip':
            self.model.is_flip[2] = self.flip_check3.Checked
        
        
        pass
    
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

    def bake(self):
        for r in self.row_panels:
            r.bake()
        
class XML_BAND():
    def __init__(self,model,band_type):
        self.model = model
        self.band_type = band_type
        #print('1')
    def run(self):
        #print('2')
        try:
            xml = XML.XmlDocument()
            xml_declaration = xml.CreateXmlDeclaration("1.0","UTF-8","yes")
            xml.AppendChild(xml_declaration)
            set = xml.CreateElement('setting')
            
            if self.band_type == 'general':
                band = xml.CreateElement('band')
                set.AppendChild(band)
                xml.AppendChild(set)
                for i in range(len(self.model.rows)):
                    print(i)
                    
                    row = xml.CreateElement('row')
                    band.AppendChild(row)
                    #row_id = xml.CreateAttribute('id')
                    row.SetAttribute('id',str(i))
                    #row.Attributes.Append(row_id)
                    #xml.AppendChild(row)
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
                f_path = XMLPATH()
                xml.Save(f_path)
                X_Choose.Band_XML_OUT = True
                
            elif self.band_type == 'bottom':
                bottom = xml.CreateElement('bottom')
                set.AppendChild(bottom)
                xml.AppendChild(set)
                for i in range(len(self.model.rows)):
                    print(i)
                    
                    row = xml.CreateElement('row')
                    bottom.AppendChild(row)
                    #row_id = xml.CreateAttribute('id')
                    row.SetAttribute('id',str(i))
                    #row.Attributes.Append(row_id)
                    #xml.AppendChild(row)
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
                f_path = XMLPATH()
                xml.Save(f_path)
                X_Choose.Band_XML_OUT = True
        except:
            #print('4')
            pass
        

            
#class Warning_Band(forms.Dialog):
#
#    def __init__(self):
#        self.Title = "提醒"
#        self.ClientSize = drawing.Size(350, 65)
#        self.Padding = drawing.Padding(5)
#        self.Resizable = False
#        #self.text = 
#        #con.type = '关于我们'
#        X_Choose.Band_xml = False
#        self.warn_label = forms.Label(Text='您还未保存XML文件,是否保存?', Font=Font('Microsoft YaHei', 12.))
#        self.CommitButton = forms.Button(Text = '确认')
#        self.CommitButton.Click += self.OnCommitButtonClick
#        self.CancelButton = forms.Button(Text = '取消')
#        self.CancelButton.Click += self.OnCancelButtonClick
#        
#        layout = forms.DynamicLayout()
#        layout.Spacing = drawing.Size(5, 5)
#        layout.AddSeparateRow(None,self.warn_label,None)
#        layout.AddSeparateRow(None,self.CommitButton,None,self.CancelButton,None)
#        self.Content = layout
#        
#    
#    def OnCancelButtonClick(self,sender,e):
#        self.Close()
#    
#    
#    def OnCommitButtonClick(self,sender,e):
#        X_Choose.Band_xml = True
#        self.Close()
        
        
        

#def Warning_Band_dialog():
#    band_dialog = Warning_Band()
#    band_dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)