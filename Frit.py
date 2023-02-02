#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, August 17th 2022
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

#算法选择UI
class SelectedDialog(forms.Dialog):

    def __init__(self):
        self.Title = "算法选择"
        self.ClientSize = drawing.Size(200, 200)
        self.Padding = drawing.Padding(5)
        self.Resizable = False
        con.type = '大众图纸'
        con.choose = 'false'
        self.pick_label = forms.Label(Text='选择填充算法:', Font=Font('Microsoft YaHei', 12.))
        self.list = forms.RadioButtonList()
        self.list.DataStore = ['大众图纸', '斜向普通填法', '斜向等距填法','普通块状填法','斜向辅助线填法','三角块状填法','斜向贴边填法']
        self.list.Orientation = forms.Orientation.Vertical
        self.list.SelectedIndex = self.list.DataStore.index(con.type)
        self.list.SelectedIndexChanged += self.typeselected
        self.CommitButton = forms.Button(Text = '确认')
        self.CommitButton.Click += self.OnCommitButtonClick
        layout = forms.DynamicLayout()
        layout.Spacing = drawing.Size(5, 5)
        layout.AddRow(self.pick_label,None)
        layout.AddRow(self.list,None)
        layout.AddRow(self.CommitButton,None)
        self.Content = layout
        
    
    def OnCommitButtonClick(self,sender,e):
        con.choose = 'true'
        self.Close()
        
    def typeselected(self, sender, e):
        #print('typeselected被调用为'+con.type)
        if self.list.SelectedIndex == 0:
            self.type = '大众图纸'
            
        elif self.list.SelectedIndex == 1:
            self.type = '88LF'
            
        elif self.list.SelectedIndex == 2:
            self.type = '76720LFW00027'
        elif self.list.SelectedIndex == 3:
            self.type = '00841LFW00001'
        elif self.list.SelectedIndex == 4:
            self.type = '00399LFW00012'
        elif self.list.SelectedIndex == 5:
            self.type = '00792LFW000023'
        elif self.list.SelectedIndex == 6:
            self.type = 'New_165'
        con.type = self.type
        #self.create(self.type)
        print(con.type)
        
        

def selectedtoDialog():
    dialog1 = SelectedDialog()
    dialog1.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)


#XML文件导出
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


class NewBlockPage(forms.TabPage):
    
    # .net 必须使用__new__显示调用构造函数！！！
    def __new__(cls, *args):
        return forms.TabPage.__new__(cls)    

    def __init__(self, page_id):
        self.page_id = page_id
        self.Text = '第三遮阳区-165通用型'
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
        self.img.Image = Bitmap("C:\\ico\\New165.png")
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
                rows = RowFrits.load_New_block_xml(file_name, self.model)
                holes = HoleFrits.load_block_xml(file_name, self.model)
                self.model.holes = holes
                self.model.rows = rows
            except:
                pass
            #DZ_ConfigPanel
        del self.row_panels[:]
        self.layout.BeginVertical()
        for i in range(len(self.model.rows)):
            rpanel = NewConfigPanel(self, self.model.rows[i])
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
        HoleFrits(1,self.model).New165_fill_dots()
        
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
            
            r1 = xml.CreateElement('New_cross_position3')
            r1.InnerText = str(self.model.rows[i].circle_config.New_cross_position3)
            row.AppendChild(r1)
            
            r2 = xml.CreateElement('New_cross_position2')
            r2.InnerText = str(self.model.rows[i].circle_config.New_cross_position2)
            row.AppendChild(r2)
            
            r3 = xml.CreateElement('New_cross_position1')
            r3.InnerText = str(self.model.rows[i].circle_config.New_cross_position1)
            row.AppendChild(r3)
            
            r4 = xml.CreateElement('New_cross_r1')
            r4.InnerText = str(self.model.rows[i].circle_config.New_cross_r1)
            row.AppendChild(r4)
            
            
            r5 = xml.CreateElement('New_cross_r2')
            r5.InnerText = str(self.model.rows[i].circle_config.New_cross_r2)
            row.AppendChild(r5)
            
            r6 = xml.CreateElement('New_cross_r3')
            r6.InnerText = str(self.model.rows[i].circle_config.New_cross_r3)
            row.AppendChild(r6)
            
            
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


#主程序UI
class FritDialog(forms.Dialog[bool]):
    def __init__(self):
        current_path1 = os.getcwd()
        self.Title = '福耀印刷花点排布工具'
        self.Icon = drawing.Icon("C:\\ico\\FY.ico")
        self.Padding = drawing.Padding(10)
        #self.type = type
        self.Resizable = False
        self.Closing += self.OnFormClosed
        self.MinimumSize = Size(800, 600)
        # 菜单
        self.create_menu()
        self.create_toolbar()
        self.tab = forms.TabControl()
        self.tab.TabPosition = forms.DockPosition.Top
        default_page = DefaultPage()
        # default_page.create()
        self.tab.Pages.Add(default_page)
        self.regions = []
        self.layout = forms.DynamicLayout()
        # default is circle dot
        self.layout.AddRow(self.tab)
        self.Content = self.layout 

    def create_menu(self):
        
        
        self.Menu = forms.MenuBar()
        current_path = os.getcwd()
        
        file_menu = self.Menu.Items.GetSubmenu("文件")
        edit_menu = self.Menu.Items.GetSubmenu("编辑")
        
        open_menu = forms.Command()
        open_menu.MenuText = "打开"
        open_menu.Image = drawing.Bitmap('C:\\ico\\file-open.png')
        file_menu.Items.Add(open_menu, 0)
        
        add_region_menu = forms.Command(self.AddBandRegionCommand)
        add_region_menu.MenuText = "添加黑花边区域"
        add_region_menu.Image = drawing.Bitmap('C:\\ico\\line.png')
        edit_menu.Items.Add(add_region_menu,0)
        
        add_region_menu1 = forms.Command(self.AddBlockRegionCommand)
        add_region_menu1.MenuText = "添加第三遮阳区域"
        add_region_menu1.Image = drawing.Bitmap('C:\\ico\\rect.png')
        edit_menu.Items.Add(add_region_menu1,1)

        add_region_menu2 = forms.Command(self.AddBottomRegionCommand)
        add_region_menu2.MenuText = "添加底部黑花边区域"
        add_region_menu2.Image = drawing.Bitmap('C:\\ico\\rect.png')
        edit_menu.Items.Add(add_region_menu2,1)
            
    
    def create_toolbar(self):
        current_path = os.getcwd()
        self.ToolBar = forms.ToolBar()
        # cmdButton = new Command { MenuText = "Click Me!", ToolBarText = "Click Me!" };
        
        transit_curve = forms.Command(self.TransitCurveCommand)
        transit_curve.MenuText = '过渡曲线'
        transit_curve.Image = drawing.Bitmap('C:\\ico\\cross.png')
        self.ToolBar.Items.Add(transit_curve)

        bake_dots = forms.Command(self.BakeDotsCommand)
        bake_dots.MenuText = '导出花点'
        bake_dots.Image = drawing.Bitmap('C:\\ico\\bake.png')
        self.ToolBar.Items.Add(bake_dots)

        # self.ToolBar.Items.Add(bake_dots)



    # Start of the class functions
    def OnFormClosed(self, sender, e):
        for region in self.regions:
            region.clear_dots()
        # self.display.Clear()
    

    def AddBandRegionCommand(self, sender, e):
        page = BandPage(len(self.regions))
        self.regions.append(page)
        self.tab.Pages.Add(page)
    
    def AddBottomRegionCommand(self, sender, e):
        page = BandPage(len(self.regions), 'bottom')
        self.regions.append(page)
        self.tab.Pages.Add(page)

    def AddBlockRegionCommand(self, sender, e):
        selectedtoDialog()
        if con.choose == 'true':
            if con.type == '大众图纸':
                page = dzBlockPage(len(self.regions))
                self.regions.append(page)
                self.tab.Pages.Add(page)
            elif con.type == 'New_165':
                page = NewBlockPage(len(self.regions))
                self.regions.append(page)
                self.tab.Pages.Add(page)
            else:
                page = BlockPage(len(self.regions))
                self.regions.append(page)
                self.tab.Pages.Add(page)
        else:
            pass

    def HandleTransitCurve(self, sender, e):
        objectId = rs.GetCurveObject("Select curve:")
        if objectId is None: 
            print("Warning: No curve is selected")
            return
        crv = objectId[0]
        l = rs.GetReal("Set left offset:")
        r = rs.GetReal("Set right offset:")
        left_curve = ghcomp.OffsetCurve(crv, distance=l, corners=1)
        right_curve = ghcomp.OffsetCurve(crv, distance=r, corners=1)
        left_pts, _, _ = ghcomp.DivideCurve(left_curve, 100, False)
        right_pts, _, _ = ghcomp.DivideCurve(right_curve, 100, False)
        pts_num = len(left_pts)
        new_pts = []
        for i in range(pts_num):
            lp = left_pts[i]
            rp = right_pts[i]
            x = lp.X * (1.0 - i * 1.0 / (pts_num - 1)) + rp.X * (i * 1.0 / (pts_num - 1))
            y = lp.Y * (1.0 - i * 1.0 / (pts_num - 1)) + rp.Y * (i * 1.0 / (pts_num - 1))
            new_pts.append(Rhino.Geometry.Point3d(x, y, 0))
        # ply_line = Rhino.Geometry.Polyline(new_pts)
        rs.AddInterpCurve(new_pts)
        print('finish')


    def TransitCurveCommand(self, sender, e):
        Rhino.UI.EtoExtensions.PushPickButton(self, self.HandleTransitCurve)
    
    def BakeDotsCommand(self, sender, e):
        main_layer = 'fuyao_frits'
        if rs.IsLayer(main_layer):
            # delete all sublayers
            layers = rs.LayerChildren(main_layer)
            for layer in layers:
                rs.PurgeLayer(layer)
            rs.DeleteLayer(main_layer)
        rs.AddLayer('fuyao_frits')
        for page in self.regions:
            page.bake()
            page.clear_dots()
            
            
#XML文件读取路径保存
class Data():
    def __init__(self):
        self.path_data = None
        
Save = Data()

#程序默认页UI
class control():
    def __init__(self):
        self.type = '大众图纸'
        self.choose = 'false'
con = control()
#程序默认页UI
class DefaultPage(forms.TabPage):
    def __init__(self):
        forms.TabPage.__init__(self)
        #self.type = '大众算法'
        self.panel = forms.Scrollable()
        self.panel.Padding = drawing.Padding(10)
        self.create()
        
        
    def create(self):
        self.Text = '基本属性'
        self.layout = forms.DynamicLayout()
        self.pick_label = forms.Label(Text='选择填充算法:', Font=Font('Microsoft YaHei', 12.))
        
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
        fd = Rhino.UI.OpenFileDialog()
        fd.Title = '加载规则文件'
        fd.Filter = '规则文件 (*.xml)'
        fd.MultiSelect = False
        if fd.ShowOpenDialog():
            Save.path_data = fd.FileName

#原Zone
class Zone:
    def __init__(self):
        pass
        
#原BandZone 初始化带状填充区域变量
class BandZone(Zone):
    def __init__(self):
        Zone.__init__(self)
        self.type = 'band'
        self.rows = list()
        self.curves = [None, None, None]
        self.is_flip = [False, False]
        self.relations = {}
    
    def add_relation(self):
        pass

#原BlockZone 初始化块状填充区域变量 封装普通型号块状填充算法
class BlockZone(Zone):
    def __init__(self):
        Zone.__init__(self)
        self.type = 'block'
        # 每一排都包括row id
        # row从下往上编号为0， 1， 2， 3， 4...
        # row 从上往下编号为-1, -2, -3...
        self.rows = list()
        self.holes = list()
        self.curves = [None, None, None]
        self.is_flip = [False, False, False]
        self.block_dots = []
        self.dots = []
    
    def get_top_row(self):
        for row in self.rows:
            if row.row_id < 0:
                return row
    
    def fill_dots(self):
        # 填充最顶部的一行
        row_num = len(self.rows)
        top_curve = None
        bottom_curve = self.curves[0]
        first_bottom_row = None
        for i in range(row_num):
            if self.rows[i].row_id < 0:
                self.rows[i].fill_dots()
                self.block_dots.append(self.rows[i].dots)
                if self.rows[i].row_id == -1:
                    first_bottom_row = self.rows[i]
        bottom_curve = self.curves[0]
        top_curve = self.rows[-1].get_bottom_curve()
        current_row_id = self.rows[-1].row_id
        current_vspace = self.rows[-1].position - first_bottom_row.position
        self.border_curve = self.construct_border(top_curve, bottom_curve)
        bbox = self.border_curve.GetBoundingBox(True)
        
        leftup = bbox.Min
        bottomright = bbox.Max

        stepping = self.holes[0].stepping
        vspace = self.holes[0].vspace
        arrange_type = self.holes[0].arrange_type
        
        yStart = leftup.Y
        yEnd = bottomright.Y
        yLength = yEnd - yStart 
        yCount = abs(int(math.ceil(yLength / vspace)))
        for i in range(yCount):
            current_row_id -= 1
            dots = list()
            if current_row_id % 2 == 0:
                dots = first_bottom_row.shift_y_mid_dots(-current_vspace - vspace * (i+1))
            else:
                dots = first_bottom_row.shift_y_dots(-current_vspace - (i + 1) * vspace)
            # use hole config for these dots
            # modify after
            new_row = []
            for dot in dots:
                # is in curve
                is_in_curve = self.border_curve.Contains(dot.centroid)
                if is_in_curve == rg.PointContainment.Inside:
                    new_dot = None
                    if self.holes[0].dot_type == FritType.CIRCLE_DOT:
                        new_dot = CircleDot(dot.centroid.X, dot.centroid.Y, self.holes[0].circle_config)
                    elif self.dot_type == FritType.ROUND_RECT:
                        new_dot = RoundRectDot(dot.centroid.X, dot.centroid.Y, self.holes[0].round_rect_config, dot.theta)
                    new_row.append(new_dot)
            self.block_dots.append(new_row)

        for row in self.block_dots:
            self.dots += row
    
    def trim_curve(self, crv, t1, t2):
        _, crv_domain = ghcomp.CurveDomain(crv)
        tstart, tend = ghcomp.DeconstructDomain(crv_domain)
        mid = (tstart + tend) / 2
        if t1 > mid:
            t1 = tstart
        if t2 < mid:
            t2 = tend
        domain = ghcomp.ConstructDomain(t1, t2)
        subcrv = ghcomp.SubCurve(crv, domain)
        
        return subcrv
        
    def construct_border(self, top_border, bottom_border):
        _, tA, tB = ghcomp.CurveXCurve(top_border, bottom_border)
        top_subcrv = top_border
        bottom_subcrv = bottom_border
        
        if tA:
            try:
                top_subcrv = self.trim_curve(top_border, tA[0], tA[-1])
            except:
                top_subcrv = self.trim_curve(top_border, tA, tA)
        if tB:
            try:
                bottom_subcrv = self.trim_curve(bottom_border, tB[0], tB[-1])
            except:
                bottom_subcrv = self.trim_curve(bottom_border, tB, tB)
        
        #self.display.AddCurve(top_subcrv)
        #self.display.AddCurve(bottom_subcrv)
        
        blocksrf = ghcomp.RuledSurface(top_subcrv, bottom_subcrv)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        #self.display.AddCurve(blockborder)
        
        return blockborder

#原dzBlockZone  初始化大众块状填充区域变量
class dzBlockZone(Zone):
    def __init__(self):
        Zone.__init__(self)
        self.type = 'block'
        # 每一排都包括row id
        # row从下往上编号为0， 1， 2， 3， 4...
        # row 从上往下编号为-1, -2, -3...
        self.rows = list()
        self.holes = list()
        self.curves = [None, None, None, None, None, None]
        self.is_flip = [False, False, False, False, False, False]
        self.block_dots = []
        self.dots = []
        
    def get_top_row(self):
        for row in self.rows:
            if row.row_id < 0:
                return row
    
    def fill_dots(self):
        # 填充最顶部的一行
        row_num = len(self.rows)
        top_curve = None
        bottom_curve = self.curves[0]
        first_bottom_row = None
        for i in range(row_num):
            if self.rows[i].row_id < 0:
                self.rows[i].fill_dots()
                self.block_dots.append(self.rows[i].dots)
                if self.rows[i].row_id == -1:
                    first_bottom_row = self.rows[i]
        bottom_curve = self.curves[0]
        top_curve = self.rows[-1].get_bottom_curve()
        current_row_id = self.rows[-1].row_id
        current_vspace = self.rows[-1].position - first_bottom_row.position
        self.border_curve = self.construct_border(top_curve, bottom_curve)
        bbox = self.border_curve.GetBoundingBox(True)
        
        leftup = bbox.Min
        bottomright = bbox.Max

        stepping = self.holes[0].stepping
        vspace = self.holes[0].vspace
        arrange_type = self.holes[0].arrange_type
        
        yStart = leftup.Y
        yEnd = bottomright.Y
        yLength = yEnd - yStart 
        yCount = abs(int(math.ceil(yLength / vspace)))
        for i in range(yCount):
            current_row_id -= 1
            dots = list()
            if current_row_id % 2 == 0:
                dots = first_bottom_row.shift_y_mid_dots(-current_vspace - vspace * (i+1))
            else:
                dots = first_bottom_row.shift_y_dots(-current_vspace - (i + 1) * vspace)
            # use hole config for these dots
            # modify after
            new_row = []
            for dot in dots:
                # is in curve
                is_in_curve = self.border_curve.Contains(dot.centroid)
                if is_in_curve == rg.PointContainment.Inside:
                    new_dot = None
                    if self.holes[0].dot_type == FritType.CIRCLE_DOT:
                        new_dot = CircleDot(dot.centroid.X, dot.centroid.Y, self.holes[0].circle_config)
                    elif self.dot_type == FritType.ROUND_RECT:
                        new_dot = RoundRectDot(dot.centroid.X, dot.centroid.Y, self.holes[0].round_rect_config, dot.theta)
                    new_row.append(new_dot)
            self.block_dots.append(new_row)

        for row in self.block_dots:
            self.dots += row
    
    def trim_curve(self, crv, t1, t2):
        _, crv_domain = ghcomp.CurveDomain(crv)
        tstart, tend = ghcomp.DeconstructDomain(crv_domain)
        mid = (tstart + tend) / 2
        if t1 > mid:
            t1 = tstart
        if t2 < mid:
            t2 = tend
        domain = ghcomp.ConstructDomain(t1, t2)
        subcrv = ghcomp.SubCurve(crv, domain)
        
        return subcrv
        
    def construct_border(self, top_border, bottom_border):
        _, tA, tB = ghcomp.CurveXCurve(top_border, bottom_border)
        top_subcrv = top_border
        bottom_subcrv = bottom_border
        
        if tA:
            try:
                top_subcrv = self.trim_curve(top_border, tA[0], tA[-1])
            except:
                top_subcrv = self.trim_curve(top_border, tA, tA)
        if tB:
            try:
                bottom_subcrv = self.trim_curve(bottom_border, tB[0], tB[-1])
            except:
                bottom_subcrv = self.trim_curve(bottom_border, tB, tB)
        
        #self.display.AddCurve(top_subcrv)
        #self.display.AddCurve(bottom_subcrv)
        
        blocksrf = ghcomp.RuledSurface(top_subcrv, bottom_subcrv)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        #self.display.AddCurve(blockborder)
        
        return blockborder

#原HoleFrits 块状填充算法
class HoleArrangeType:
    HEADING=0
    CROSS=1
    @staticmethod
    def get_hole_arrange_type():
        return ['顶头', '交错']

#原HoleFrits 块状填充算法
class Dazhong_fill_holes:
    def __init__(self, upline, midline, downline, boundary, split_crv, edge_crv, horizontal, vertical, region, aligned = False):
        self.upline = upline
        self.midline = midline
        self.downline = downline
        self.boundary = boundary
        self.split_crv = split_crv
        self.edge_crv = edge_crv
        self.frit_black = []
        self.frit_white = []
        self.frit_bound = []
        
        self.horizontal = horizontal
        self.vertical = vertical
        self.aligned = aligned
        self.tolerance = 0.5
        self.region = region
        
        self.display_color = rc.Display.ColorHSL(0, 1, 0)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
        
        print(self.region.rows[0].circle_config.cross_k1)
        print(self.region.rows[0].circle_config.cross_position3)
        print(self.region.rows[0].circle_config.cross_position2)
        print(self.region.rows[0].circle_config.cross_position1)
        print(self.region.rows[0].circle_config.cross_k2)
    
    def _generate_grid_pts(self, base_pts, vertical, downline):
        pts = []
        bound_pts = []
        dest_pts = []
        
        dest_pts0, _, dis = ghcomp.CurveClosestPoint(base_pts, downline)
        max = 0
        for i in range(len(dis)):
            if dis[i]>max:
                max = dis[i]
        
        base_vec = ghcomp.UnitY(-1)
        
        for i in range(len(dis)):
            base_line = ghcomp.LineSDL(base_pts[i], base_vec, 1.25*max)
            dest_pt, _, _ = ghcomp.CurveXCurve(base_line, downline)
            if dest_pt:
                dest_pts.append(dest_pt)
            else:
                dest_pts.append(dest_pts0[i])
        
        v_dis = ghcomp.Distance(base_pts, dest_pts)
        vlength = ghcomp.Average(v_dis)
        v_num = int(math.floor(vlength/vertical))
        if v_num%2 != 0:
            v_num = v_num - 1
        
        relation, _ = ghcomp.PointInCurve(base_pts, self.boundary)
        base_array_pts, _ = ghcomp.Dispatch(base_pts, relation)
        if base_array_pts:
            bound_pts.append(base_array_pts[0])
    
        for i in range(1, v_num):
            cur_pts = []
            for j in range(len(base_pts)):
                cur_base = base_pts[j]
                cur_dest = dest_pts[j]
                cur_vec, _ = ghcomp.Vector2Pt(cur_base, cur_dest, True)
                cur_dis = i*v_dis[j]/v_num
                line = ghcomp.LineSDL(cur_base, cur_vec, cur_dis)
                _, cur_pt = ghcomp.EndPoints(line)
                cur_pts.append(cur_pt)
            if self.aligned == False:
                if i%2 == 1:
                    shift_pts = []
                    for k in range(len(cur_pts)-1):
                        shift_pts.append(ghcomp.Division(ghcomp.Addition(cur_pts[k], cur_pts[k+1]),2))
                    cur_pts = shift_pts
            relation, _ = ghcomp.PointInCurve(cur_pts, self.boundary)
            cur_pts, _ = ghcomp.Dispatch(cur_pts, relation)
            if cur_pts:
                cur_pts = construct_safe_pts_list(cur_pts)
                pts += cur_pts
                bound_pts.append(cur_pts[0])
        return dest_pts, pts, bound_pts
    
    def generate_grid_pts(self):
        pts = []
        bound_pts = []
        uplength = ghcomp.Length(self.upline)
        num = int(math.floor(uplength/self.horizontal)+1)
        up_pts, _, _ = ghcomp.DivideCurve(self.upline, num, False)
        mid_pts, um_pts, um_bound = self._generate_grid_pts(up_pts, self.vertical, self.midline)
        if self.downline:
            down_pts, md_pts, md_bound = self._generate_grid_pts(mid_pts, self.vertical, self.downline)
        
        bound_pts += um_bound
        if self.downline:
            bound_pts += md_bound
        bound_pts, _ = ghcomp.DeleteConsecutive(bound_pts, False)
        #relation, _ = ghcomp.PointInCurve(bound_pts, self.boundary)
        #bound_pts, _ = ghcomp.Dispatch(bound_pts, relation)
        pts += up_pts
        pts += mid_pts
        if self.downline:
            pts += down_pts
        
        relation, _ = ghcomp.PointInCurve(pts, self.boundary)
        
        pts, _ = ghcomp.Dispatch(pts, relation)
        
        pts += um_pts
        #self.display.AddCircle(pts, self.display_color, 1, 1.2)
        
        #for i in range(len(pts)):
            #self.display.AddCircle(rc.Geometry.Circle(pts[i],0.5),self.display_color,1)
        if self.downline:
            pts += md_pts
        return pts, bound_pts
        
    def generate_bound_pts(self, head_pts, pts):
        tolerance = 0.1
        
        unit_length = 1
        if self.aligned == False:
            unit_length = math.sqrt(0.25*self.horizontal*self.horizontal+self.vertical*self.vertical)
        else:
            unit_length = math.sqrt(self.horizontal*self.horizontal+self.vertical*self.vertical)
            
        num = int(math.floor(ghcomp.Length(self.split_crv)/unit_length)+1)
        aux_pts, _, _ = ghcomp.DivideCurve(self.split_crv, 3*num, False)
        aux_bound_pts, _, _ = ghcomp.ClosestPoint(aux_pts, pts)
        aux_bound_pts, _ = ghcomp.DeleteConsecutive(aux_bound_pts, False)
        
        _, anchor, _ = ghcomp.Deconstruct(aux_bound_pts[0])
        bound_pts = []
        for i in range(len(head_pts)):
            cur_pt = head_pts[i]
            _, cur_y, _ = ghcomp.Deconstruct(cur_pt)
            if cur_y <= anchor:
                bound_pts.append(cur_pt)
        
        head_pts = bound_pts
        bound_pts = []
        i=0
        j=0
        pre_pt = head_pts[0]
        while i<len(head_pts) and j<len(aux_bound_pts):
            cur_head = head_pts[i]
            cur_aux = aux_bound_pts[j]
            if ghcomp.Distance(cur_head, cur_aux)<tolerance:
                bound_pts.append(cur_head)
                pre_pt = cur_head
                i += 1
                j += 1
            else:
                dis_head = ghcomp.Distance(cur_head, pre_pt)
                dis_aux = ghcomp.Distance(cur_aux, pre_pt)
                if dis_head < dis_aux:
                    bound_pts.append(cur_head)
                    i += 1
                    pre_pt = cur_head
                else:
                    bound_pts.append(cur_aux)
                    j += 1
                    pre_pt = cur_aux
                    
        if i!=len(head_pts):
            for k in range(i, len(head_pts)):
                bound_pts.append(head_pts[k])
        if j!=len(aux_pts):
            for k in range(j, len(aux_bound_pts)):
                bound_pts.append(aux_bound_pts[k])
            
        i=1
        count = len(bound_pts)
        while i<count-1:
            pre_pt = bound_pts[i-1]
            cur_pt = bound_pts[i]
            suc_pt = bound_pts[i+1]
            _, pre_y, _ = ghcomp.Deconstruct(pre_pt)
            _, cur_y, _ = ghcomp.Deconstruct(cur_pt)
            _, suc_y, _ = ghcomp.Deconstruct(suc_pt)
            if cur_y>pre_y and cur_y>suc_y:
                bound_pts.pop(i)
                count -= 1
                continue
            i += 1
        return bound_pts
    
    def ifright(self, pt1, pt2):
        right = False
        x1, y1, z1 = ghcomp.Deconstruct(pt1)
        x2, y2, z2 = ghcomp.Deconstruct(pt2)
        #if ghcomp.Absolute(x2-x1-horizontal) < tolerance:
        if ghcomp.Absolute(y1-y2) < self.tolerance:
            right = True
        return right
    
    def ifdown(self, pt1, pt2):
        down = False
        x1, y1, z1 = ghcomp.Deconstruct(pt1)
        x2, y2, z2 = ghcomp.Deconstruct(pt2)
        #if ghcomp.Absolute(y1-y2-vertical) < tolerance:
        if ghcomp.Absolute(x1-x2) < self.tolerance:
            down = True
        return down
    
    def generate_white_direc(self, white_pts):
        white_direc = []
        for i in range(len(white_pts)):
            cur_pt = white_pts[i]
            _, t1, d1 = ghcomp.CurveClosestPoint(cur_pt, self.upline)
            std_pt, t2, d2 = ghcomp.CurveClosestPoint(cur_pt, self.midline)
            _, t3, d3 = ghcomp.CurveClosestPoint(cur_pt, self.downline)
            _, cur_y, _ = ghcomp.Deconstruct(cur_pt)
            _, std_y, _ = ghcomp.Deconstruct(std_pt)
            cur_direc = ghcomp.VectorXYZ(-1, 0, 0)
            if cur_y > std_y:
                _, tgt1, _ = ghcomp.EvaluateCurve(self.upline, t1)
                _, tgt2, _ = ghcomp.EvaluateCurve(self.midline, t2)
                cur_direc = ghcomp.Addition(ghcomp.Multiplication(tgt1, d2/(d1+d2)),ghcomp.Multiplication(tgt2, d1/(d1+d2)))
            elif cur_y < std_y:
                _, tgt2, _ = ghcomp.EvaluateCurve(self.midline, t2)
                _, tgt3, _ = ghcomp.EvaluateCurve(self.downline, t3)
                cur_direc = ghcomp.Addition(ghcomp.Multiplication(tgt2, d3/(d2+d3)),ghcomp.Multiplication(tgt3, d2/(d2+d3)))
            else:
                cur_direc = tgt2
            white_direc.append(cur_direc)
        return white_direc
    
    def generate_black_pts(self, white_pts, white_direc, upline):
        
        horizontal = self.horizontal
        if self.aligned == False:
            horizontal = horizontal/2
            
        black_pts = []
        black_direc = []
        for i in range(len(white_pts)):
            cur_pt = white_pts[i]
            cur_direc = white_direc[i]
            black_direc.append(cur_direc)
            """
            pt_ori, t, _ = ghcomp.CurveClosestPoint(cur_pt, upline)
            _, direc_ori, _ = ghcomp.EvaluateCurve(upline, t)
            
            aux_line = ghcomp.LineSDL(pt_ori, ghcomp.Multiplication(-1, direc_ori), self.horizontal)
            _, black_pt_ori = ghcomp.EndPoints(aux_line)
            """
            cur_line = ghcomp.LineSDL(cur_pt, ghcomp.Multiplication(-1, cur_direc), horizontal)
            #cur_black_pt, _, _ = ghcomp.CurveClosestPoint(black_pt_ori, cur_line)
            _, cur_black_pt = ghcomp.EndPoints(cur_line)
            black_pts.append(cur_black_pt)
        return black_pts, black_direc
    
    def generate_seq(self, white_pts, black_pts, white_direc, black_direc):
        seq_pts = []
        seq_direc = []
        pre_pt = white_pts[0]
        
        for i in range(len(white_pts)):
            cur_white = white_pts[i]
            cur_black = black_pts[i]
            if i==0:
                seq_pts.append(cur_black)
                seq_direc.append(black_direc[i])
                seq_pts.append(cur_white)
                seq_direc.append(white_direc[i])
                pre_pt = cur_white
            else:
                if self.ifdown(pre_pt, cur_black):
                    seq_pts.append(cur_black)
                    seq_direc.append(black_direc[i])
                    seq_pts.append(cur_white)
                    seq_direc.append(white_direc[i])
                    pre_pt = cur_white
                elif self.ifright(pre_pt, cur_black):
                    seq_pts.append(cur_black)
                    seq_direc.append(black_direc[i])
                    seq_pts.append(cur_white)
                    seq_direc.append(white_direc[i])
                    pre_pt = cur_white
                else:
                    seq_pts.pop(-1)
                    seq_direc.pop(-1)
                    seq_pts.append(cur_white)
                    seq_direc.append(white_direc[i])
                    pre_pt = cur_white
                    
        return seq_pts, seq_direc
    
    def generate_rect(self, center_pts, ks, r, n, pattern = None):
        sr = r
        lr = sr
        #默认圆角矩形的边方向为逆时针（黑），白色则为顺时针
        bound_crv = []
        rect_crv = []
        #TODO: modify line to nurbscurve
        
        #k = k/2
        #ang, _ = ghcomp.Angle(ghcomp.UnitY(-1), n)
        
        for i in range(len(center_pts)):
            k = ks[i]/2
            cur_rect = {}
            cur_pt = center_pts[i]
            x = cur_pt.X
            y = cur_pt.Y
            z = cur_pt.Z
            cur_n = n[i]
            #cur_ang = ang[i]
            #if n[i].X < 0:
            #    cur_ang = -cur_ang
            
            std_vec = ghcomp.UnitX(1)
            
            luarc_ct = ghcomp.ConstructPoint(x-k+r, y+k-r, 0)
            lu_angle = ghcomp.ConstructDomain(ghcomp.Pi(0.5), ghcomp.Pi(1))
            luarc, _ = ghcomp.Arc(ghcomp.XYPlane(luarc_ct), r, lu_angle)
            luarc = rg.NurbsCurve.CreateFromArc(luarc)
            luarc, _ = ghcomp.RotateDirection(luarc, cur_pt, std_vec, cur_n)
            #luarc, _ = ghcomp.Rotate(luarc, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                luarc, _ = ghcomp.FlipCurve(luarc)
            bound_crv.append(luarc)
            cur_rect['lu'] = luarc
            
            up_l = ghcomp.ConstructPoint(x-k+r, y+k, 0)
            up_r = ghcomp.ConstructPoint(x+k-r, y+k, 0)
            up_crv = ghcomp.Line(up_r, up_l)
            up_crv = rg.NurbsCurve.CreateFromLine(up_crv)
            up_crv, _ = ghcomp.RotateDirection(up_crv, cur_pt, std_vec, cur_n)
            #up_crv, _ = ghcomp.Rotate(up_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                up_crv, _ = ghcomp.FlipCurve(up_crv)
            bound_crv.append(up_crv)
            cur_rect['up'] = up_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(up_crv, luarc), True)
            
            ruarc_ct = ghcomp.ConstructPoint(x+k-r, y+k-r, 0)
            ru_angle = ghcomp.ConstructDomain(ghcomp.Pi(0), ghcomp.Pi(0.5))
            ruarc, _ = ghcomp.Arc(ghcomp.XYPlane(ruarc_ct), r, ru_angle)
            ruarc = rg.NurbsCurve.CreateFromArc(ruarc)
            ruarc, _ = ghcomp.RotateDirection(ruarc, cur_pt, std_vec, cur_n)
            #ruarc, _ = ghcomp.Rotate(ruarc, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                ruarc, _ = ghcomp.FlipCurve(ruarc)
            bound_crv.append(ruarc)
            cur_rect['ru'] = ruarc
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(ruarc, rec_crv), True)
            
            right_u = ghcomp.ConstructPoint(x+k, y+k-r, 0)
            r = sr
            right_b = ghcomp.ConstructPoint(x+k, y-k+r, 0)
            right_crv = ghcomp.Line(right_b, right_u)
            right_crv = rg.NurbsCurve.CreateFromLine(right_crv)
            right_crv, _ = ghcomp.RotateDirection(right_crv, cur_pt, std_vec, cur_n)
            #right_crv, _ = ghcomp.Rotate(right_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                right_crv, _ = ghcomp.FlipCurve(right_crv)
            bound_crv.append(right_crv)
            cur_rect['right'] = right_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(right_crv, rec_crv), True)
            
            rbarc_ct = ghcomp.ConstructPoint(x+k-r, y-k+r, 0)
            rb_angle = ghcomp.ConstructDomain(ghcomp.Pi(-0.5), ghcomp.Pi(0))
            rbarc, _ = ghcomp.Arc(ghcomp.XYPlane(rbarc_ct), r, rb_angle)
            rbarc = rg.NurbsCurve.CreateFromArc(rbarc)
            rbarc, _ = ghcomp.RotateDirection(rbarc, cur_pt, std_vec, cur_n)
            #rbarc, _ = ghcomp.Rotate(rbarc, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                rbarc, _ = ghcomp.FlipCurve(rbarc)
            bound_crv.append(rbarc)
            cur_rect['rb'] = rbarc
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(rbarc, rec_crv), True)
            
            bottom_r = ghcomp.ConstructPoint(x+k-r, y-k, 0)
            bottom_l = ghcomp.ConstructPoint(x-k+r, y-k, 0)
            bottom_crv = ghcomp.Line(bottom_l, bottom_r)
            bottom_crv = rg.NurbsCurve.CreateFromLine(bottom_crv)
            bottom_crv, _ = ghcomp.RotateDirection(bottom_crv, cur_pt, std_vec, cur_n)
            #bottom_crv, _ = ghcomp.Rotate(bottom_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                bottom_crv, _ = ghcomp.FlipCurve(bottom_crv)
            bound_crv.append(bottom_crv)
            cur_rect['bottom'] = bottom_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(bottom_crv, rec_crv), True)
            
            lbarc_ct = ghcomp.ConstructPoint(x-k+r, y-k+r, 0)
            lb_angle = ghcomp.ConstructDomain(ghcomp.Pi(-1), ghcomp.Pi(-0.5))
            lbarc, _ = ghcomp.Arc(ghcomp.XYPlane(lbarc_ct), r, lb_angle)
            lbarc = rg.NurbsCurve.CreateFromArc(lbarc)
            lbarc, _ = ghcomp.RotateDirection(lbarc, cur_pt, std_vec, cur_n)
            #lbarc, _ = ghcomp.Rotate(lbarc, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                lbarc, _ = ghcomp.FlipCurve(lbarc)
            bound_crv.append(lbarc)
            cur_rect['lb'] = lbarc
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(lbarc, rec_crv), True)
            
            left_b = ghcomp.ConstructPoint(x-k, y-k+r, 0)
            left_u = ghcomp.ConstructPoint(x-k, y+k-r, 0)
            left_crv = ghcomp.Line(left_u, left_b)
            left_crv = rg.NurbsCurve.CreateFromLine(left_crv)
            left_crv, _ = ghcomp.RotateDirection(left_crv, cur_pt, std_vec, cur_n)
            #left_crv, _ = ghcomp.Rotate(left_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            if pattern == "white":
                left_crv, _ = ghcomp.FlipCurve(left_crv)
            bound_crv.append(left_crv)
            cur_rect['left'] = left_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(left_crv, rec_crv), True)
            
            seamptl, seamptr = ghcomp.EndPoints(bottom_crv)
            #seampt = ghcomp.Division(ghcomp.Addition(seamptl, seamptr), 2)
            _, seamt, _ = ghcomp.CurveClosestPoint(seamptl, rec_crv)
            rec_crvl = ghcomp.Seam(rec_crv, seamt)
            cur_rect['rect'] = rec_crvl
            _, seamt, _ = ghcomp.CurveClosestPoint(seamptr, rec_crv)
            rec_crvr = ghcomp.Seam(rec_crv, seamt)
            cur_rect['rect2'] = rec_crvr
            
            rect_crv.append(cur_rect)
        
        return bound_crv, rect_crv
    
    def generate_h_link(self, rect1, rect2):
        crv1 = rect1['right']
        crv2 = rect2['left']
        link = ghcomp.TweenCurve(crv1, crv2, 0.5)
        return link
        
    def generate_v_link(self, rect1, rect2):
        crv1 = rect1['bottom']
        crv2 = rect2['up']
        link = ghcomp.TweenCurve(crv1, crv2, 0.5)
        return link
    
    def separate_pts(self, seq_pts, seq_direc):
        #data structure: 类似 dictionary
        #list[0]为当前类型的tag
        """ e.g. 
        [['slope', pts],
        ['cross', pts],
        ['slope', pts]]
        """
        
        slope_pts = []
        cross_pts = []
        slope_direcs = []
        cross_direcs = []
        
        pts = []
        direcs = []
        
        pre_type = None
        temp_head = None
        
        for i in range(len(seq_pts)):
            cur_pt = seq_pts[i]
            
            if i!=0:
                pre_pt = seq_pts[i-1]
                if self.ifright(pre_pt, cur_pt):
                    cross_pts.append(cur_pt)
                    cross_direcs.append(seq_direc[i])
                    if len(cross_pts) > 3:
                        if len(slope_pts) != 0:
                            temp_head = (cross_pts[0], cross_direcs[0])
                            #slope_pts.append(cross_pts[0])
                            #slope_direcs.append(cross_direcs[0])
                            cross_pts.insert(0, slope_pts[-1])
                            cross_direcs.insert(0, slope_direcs[-1])
                            slope_pts.append(temp_head[0])
                            slope_direcs.append(temp_head[1])
                            temp_head = None
                            pre_seq = ['slope', slope_pts]
                            pts.append(pre_seq)
                            direcs.append(slope_direcs)
                            slope_pts = []
                            slope_direcs = []
                            pre_type = 'slope'
                    
                else:
                    if len(cross_pts) > 10:
                        if pre_type == 'cross' and temp_head!=None:
                            cross_pts.insert(0, temp_head[0])
                            cross_direcs.insert(0, temp_head[1])
                            temp_head = None
                        pre_seq = ['cross', cross_pts]
                        pts.append(pre_seq)
                        direcs.append(cross_direcs)
                        pre_type = 'cross'
                        #slope_pts.pop()
                        #slope_direcs.pop()
                        temp_head = (cur_pt, seq_direc[i])
                    else:
                        slope_pts += cross_pts
                        slope_direcs += cross_direcs
                        slope_pts.append(cur_pt)
                        slope_direcs.append(seq_direc[i])
                    cross_pts = []
                    cross_direcs = []
            
            if i==len(seq_pts)-1:
                if len(slope_pts) != 0:
                    cur_seq = ['slope', slope_pts]
                    pts.append(cur_seq)
                    direcs.append(slope_direcs)
                    slope_pts = []
                    slope_direcs = []
                if len(cross_pts) != 0:
                    if pre_type == 'cross' and temp_head!=None:
                        cross_pts.insert(0, temp_head[0])
                        cross_direcs.insert(0, temp_head[1])
                        temp_head = None
                    cur_seq = ['cross', cross_pts]
                    pts.append(cur_seq)
                    direcs.append(cross_direcs)
                    cross_pts = []
                    cross_direcs = []
                
        return pts, direcs
    
    def generate_bound(self, seq_pts, seq_direc):
        white_rect = []
        black_rect = []
        bound_crv = []
        
        black_emu = ['lu', 'left', 'lb', 'bottom', 'rb', 'right', 'ru', 'up']
        white_emu = ['lu', 'up', 'ru', 'right', 'rb', 'bottom', 'lb', 'left']
        
        odd_even = ghcomp.Merge(0,1)
        white_pts, black_pts = ghcomp.Dispatch(seq_pts, odd_even)
        white_n, black_n = ghcomp.Dispatch(seq_direc, odd_even)
        
        white_ks = []
        black_ks = []
        
        white_seq_pts, _ = self.separate_pts(white_pts, white_n)
        for i in range(len(white_seq_pts)):
            cur_seq = white_seq_pts[i]
            if cur_seq[0] == 'slope':
                for j in range(len(cur_seq[1])):
                    white_ks.append(1.15)
            else:
                for j in range(len(cur_seq[1])):
                    white_ks.append(1.15)
        
        for i in range(len(black_pts)):
            black_ks.append(1.13)
        
        white_bound, white_rect = self.generate_rect(white_pts, white_ks, 0.2, white_n, pattern = "white")
        black_bound, black_rect = self.generate_rect(black_pts, black_ks, 0.2, black_n, pattern = "black")
        
        pre_pt = white_pts[0]
        link_crv = []
        for i in range(len(white_pts)):
            cur_black = black_pts[i]
            cur_white = white_pts[i]
            cur_white_rect = white_rect[i]
            cur_black_rect = black_rect[i]
            
            if i!=0:
                pre_white_rect = white_rect[i-1]
                if self.ifright(pre_pt, cur_black):
                    link_crv.append(self.generate_h_link(pre_white_rect, cur_black_rect))
                    pre_white_rect['end'] = 'ru'
                    cur_black_rect['start'] = 'lb'
                elif self.ifdown(pre_pt, cur_black):
                    link_crv.append(self.generate_v_link(pre_white_rect, cur_black_rect))
                    pre_white_rect['end'] = 'rb'
                    cur_black_rect['start'] = 'lu'
            else:
                cur_black_rect['start']='left'
                
            if self.ifright(cur_black, cur_white):
                link_crv.append(self.generate_h_link(cur_black_rect, cur_white_rect))
                cur_black_rect['end'] = 'rb'
                cur_white_rect['start'] = 'lu'
            elif self.ifdown(cur_black, cur_white):
                link_crv.append(self.generate_v_link(cur_black_rect, cur_white_rect))
                cur_black_rect['end'] = 'lb'
                cur_white_rect['start'] = 'ru'
            
            if i == len(white_pts)-1:
                cur_white_rect['end'] = 'right'
            
            pre_pt = cur_white
        
        for i in range(len(white_pts)):
            cur_black_rect = black_rect[i]
            cur_white_rect = white_rect[i]
            
            flag = False
            for k in black_emu:
                if k==cur_black_rect['start']:
                    flag = True
                if flag == True:
                    link_crv.append(cur_black_rect[k])
                if k==cur_black_rect['end']:
                    flag = False
                    break
            
            for k in white_emu:
                if k==cur_white_rect['start']:
                    flag = True
                if flag == True:
                    link_crv.append(cur_white_rect[k])
                if k==cur_white_rect['end']:
                    break
        
        bound_crv += white_bound
        bound_crv += black_bound
        
        link_crv = rg.Curve.JoinCurves(link_crv, 0.5, True)
        
        return bound_crv, link_crv, black_pts, black_n
    
    def generate_cross_band(self, cross_pts, edge_crv):
        #todo：用tweencrv进行offset
        cross_band = []
        shift_pts = []
        for i in range(len(cross_pts)-1):
            shift_pts.append(ghcomp.Division(ghcomp.Addition(cross_pts[i] + cross_pts[i+1]), 2))
        k0 = self.region.rows[0].circle_config.cross_k1
        h1 = self.region.rows[0].circle_config.cross_position3 + k0/2
        h2 = self.region.rows[0].circle_config.cross_position2 + k0/2
        h3 = self.region.rows[0].circle_config.cross_position1 + k0/2
        k1 = self.region.rows[0].circle_config.cross_k2
        sr1 = self.region.rows[0].circle_config.cross_round_rect_r
        r2 = self.region.rows[0].circle_config.cross_r2/2
        r3 = self.region.rows[0].circle_config.cross_r1/2
        
        std_crv = ghcomp.PolyLine(cross_pts, False)
        
        real_pts, _, dis = ghcomp.CurveClosestPoint(cross_pts, edge_crv)
        real_dis = ghcomp.Average(dis)
        factor = real_dis/(h3+r3)
        
        real_factor = ghcomp.Division(dis, h3+r3)
        
        des_crv = ghcomp.PolyLine(real_pts, False)
        
        #crv1 = ghcomp.TweenCurve(std_crv, des_crv, h1/(h3+r3))
        crv1 = ghcomp.OffsetCurve(std_crv, h1, ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), 1)
        band_pts1, t1, _ = ghcomp.CurveClosestPoint(shift_pts, crv1)
        _, tgt1, _ = ghcomp.EvaluateCurve(crv1, t1)
        ks1 = []
        for i in range(len(band_pts1)):
            ks1.append(k1)
        _, band_rect1 = self.generate_rect(band_pts1, ks1, sr1, tgt1, pattern = "black")
        for i in range(len(band_rect1)):
            cross_band.append(band_rect1[i]['rect'])
        
        crv21 = ghcomp.OffsetCurve(std_crv, h2, ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), 1)
        band_pts21, _, _ = ghcomp.CurveClosestPoint(cross_pts, crv21)
        crv22 = ghcomp.TweenCurve(std_crv, des_crv, h2/(h3+r3))
        band_pts22, _, _ = ghcomp.CurveClosestPoint(cross_pts, crv22)
        num = len(band_pts21)
        band_pts2 = []
        for i in range(num):
            cur_pt = ghcomp.Addition(ghcomp.Multiplication(band_pts21[i], 1.0*(num-i)/num), ghcomp.Multiplication(band_pts22[i], 1.0*i/num))
            
            band_pts2.append(cur_pt)
        
        crv3 = ghcomp.TweenCurve(std_crv, des_crv, h3/(h3+r3))
        band_pts3, _, _ = ghcomp.CurveClosestPoint(shift_pts, crv3)

        circle_band = []
        circle_band += ghcomp.Circle(band_pts2, ghcomp.Multiplication(real_factor, r2))
        circle_band += ghcomp.Circle(band_pts3, ghcomp.Multiplication(real_factor, r3))
        for i in range(len(circle_band)): 
            circle_band[i] = rg.NurbsCurve.CreateFromCircle(circle_band[i])
        
        cross_band += circle_band    
        return cross_band
    
    def generate_slope_band(self, slope_pts, h_direcs, edge_crv):
        slope_band = []
        
        r0 = self.region.rows[0].circle_config.slope_r1/2 #装饰性圆点
        r1 = self.region.rows[0].circle_config.slope_r2/2
        r2 = self.region.rows[0].circle_config.slope_r3/2
        r3 = self.region.rows[0].circle_config.slope_r4/2
        
        horizontal = self.horizontal
        if self.aligned == False:
            horizontal = horizontal/2
        
        unit_length = math.sqrt(horizontal*horizontal + self.vertical*self.vertical)
        threshold = 0.3
        
        for i in range(len(h_direcs)):
            cur_pt = slope_pts[i]
            #逆时针旋转45°
            line, _ = ghcomp.Rotate(ghcomp.LineSDL(cur_pt, h_direcs[i], 10), ghcomp.Pi(1.25), ghcomp.XYPlane(cur_pt))
            end_pt, _, _ = ghcomp.CurveXCurve(line, edge_crv)
            if end_pt:
                cur_direc, _ = ghcomp.Vector2Pt(cur_pt, end_pt, False)
                dist = ghcomp.Distance(cur_pt, end_pt)
                count = int(math.floor(dist/unit_length))
                cpst = dist - count * unit_length
                for j in range(count):
                    _, band_pt = ghcomp.EndPoints(ghcomp.LineSDL(cur_pt, cur_direc, unit_length*(j+1)))
                    if j==count-1:
                        if cpst > threshold * unit_length:
                            slope_band.append(ghcomp.Circle(band_pt, r1))
                        else:
                            _, cpst_pt = ghcomp.EndPoints(ghcomp.LineSDL(cur_pt, cur_direc, dist-r1))
                            slope_band.append(ghcomp.Circle(cpst_pt, r0))
                            
                    elif j==count-2:
                        slope_band.append(ghcomp.Circle(band_pt, r2))
                    else:
                        slope_band.append(ghcomp.Circle(band_pt, r3))
                        
                if cpst > (1-threshold) * unit_length:
                    _, cpst_pt = ghcomp.EndPoints(ghcomp.LineSDL(cur_pt, cur_direc, dist-r0))
                    slope_band.append(ghcomp.Circle(cpst_pt, r0))
        
        for i in range(len(slope_band)):
            slope_band[i] = rg.NurbsCurve.CreateFromCircle(slope_band[i])
        
        return slope_band
    
    def generate_black_band(self, bound_pts, bound_direcs):
        edge_crv = self.edge_crv
        
        black_band = []
        bug1 = []
        bug2 = []
        for i in range(len(bound_pts)):
            cur_seq = bound_pts[i]
            cur_type = cur_seq[0]
            if cur_type == "slope":
                cur_seq_pts = cur_seq[1]
                bug1 += cur_seq_pts
                cur_direcs = bound_direcs[i]
                black_band += self.generate_slope_band(cur_seq_pts, cur_direcs, edge_crv)
            elif cur_type == "cross":
                cur_seq_pts = cur_seq[1]
                bug2 += cur_seq_pts
                black_band += self.generate_cross_band(cur_seq_pts, edge_crv)
                
        #两部分点：斜向阵列和贴边装饰点
        #横向点直接遵照规则做offset和shift
        return black_band
        
    def bake(self):
        layer_name = 'fuyao_black'
        rs.AddLayer(layer_name, self.display_color)
        for i in range(len(self.frit_black)):
            obj = scriptcontext.doc.Objects.AddCurve(self.frit_black[i])
            rs.ObjectLayer(obj, layer_name)
        
        layer_name = 'fuyao_white'
        rs.AddLayer(layer_name, self.display_color)
        for i in range(len(self.frit_white)):
            obj = scriptcontext.doc.Objects.AddCurve(self.frit_white[i])
            rs.ObjectLayer(obj, layer_name)
        
        layer_name = 'fuyao_bound'
        rs.AddLayer(layer_name, self.display_color)
        for i in range(len(self.frit_bound)):
            obj = scriptcontext.doc.Objects.AddCurve(self.frit_bound[i])
            rs.ObjectLayer(obj, layer_name)
    
    def run(self):
        pts, bound_pts = self.generate_grid_pts()
            
        white_pts = self.generate_bound_pts(head_pts = bound_pts, pts = pts)
        
        white_direc = self.generate_white_direc(white_pts)
        black_pts, black_direc = self.generate_black_pts(white_pts, white_direc, self.upline)
        seq_pts, seq_direc = self.generate_seq(white_pts, black_pts, white_direc, black_direc)
        
        bound_crv, link_crv, black_seq_pts, black_n = self.generate_bound(seq_pts, seq_direc)
        bound_pts, bound_direcs = self.separate_pts(black_seq_pts, black_n)
        black_band = self.generate_black_band(bound_pts, bound_direcs)
        
        for i in range(len(link_crv)):
            self.frit_bound.append(link_crv[i])
            #self.display.AddCurve(link_crv[i], self.display_color, 1)
        
        for i in range(len(black_band)):
            self.frit_black.append(black_band[i])
            #self.display.AddCurve(black_band[i],self.display_color,1)
        
        pat = ghcomp.Merge(True, False)
        _, white_list = ghcomp.Dispatch(seq_pts, pat)#OK
        _, Index_of_white, _ = ghcomp.ClosestPoint(white_list, pts)#OK
        
        #for i in range(len(Index_of_white)):
        #    print(Index_of_white[i])
        inner_of_holes = ghcomp.CullIndex(pts,Index_of_white,True)#OK.
        _, white_border, _ = ghcomp.ClosestPoint(seq_pts, inner_of_holes)#OK
        white_item = ghcomp.ListItem(inner_of_holes, white_border, True)#OK 222 values
        white_border_frit, _ = ghcomp.DeleteConsecutive(white_item, False)#OK 111 values
        
        for i in range(len(white_border_frit)):
            self.frit_white.append(rg.NurbsCurve.CreateFromCircle(rc.Geometry.Circle(white_border_frit[i],0.585)))
            #self.display.AddCircle(rc.Geometry.Circle(white_border_frit[i],0.585),self.display_color,1)
        
        #print(len(white_border_frit))
        #for i in range(len(white_border_frit)):
        #    print(white_border_frit[i])
        _, Index_boder_white, _ = ghcomp.ClosestPoint(white_border_frit, inner_of_holes)#OK 111 values
        white_hole_frit = ghcomp.CullIndex(inner_of_holes,Index_boder_white,True)#OK 3999 values
        #print(len(white_hole_frit))
        for i in range(len(white_hole_frit)):
            self.frit_white.append(rg.NurbsCurve.CreateFromCircle(rc.Geometry.Circle(white_hole_frit[i],0.5)))
            #self.display.AddCircle(rc.Geometry.Circle(white_hole_frit[i],0.5),self.display_color,1)
        
        self.bake()
        
class New_165_fill_holes:
    def __init__(self, upline, downline, boundary, slopeline, split_crv, edge_crv, horizontal, vertical, region, aligned = False):
        self.upline = upline
        self.downline = downline
        self.boundary = boundary
        self.slopeline = slopeline
        self.split_crv, _ = ghcomp.FlipCurve(split_crv)
        self.edge_crv = edge_crv
        self.frit_black = []
        
        self.horizontal = horizontal
        self.vertical = vertical
        self.aligned = aligned
        self.tolerance = 0.5
        self.region = region
        
        self.display_color = rc.Display.ColorHSL(0, 1, 0)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
        self.display.AddCurve(boundary, self.display_color, 1)
    
    def ifright(self, pt1, pt2):
        right = False
        x1, y1, z1 = ghcomp.Deconstruct(pt1)
        x2, y2, z2 = ghcomp.Deconstruct(pt2)
        #if ghcomp.Absolute(x2-x1-horizontal) < tolerance:
        if ghcomp.Absolute(y1-y2) < self.tolerance:
            right = True
        return right
    
    def ifdown(self, pt1, pt2):
        down = False
        x1, y1, z1 = ghcomp.Deconstruct(pt1)
        x2, y2, z2 = ghcomp.Deconstruct(pt2)
        #if ghcomp.Absolute(y1-y2-vertical) < tolerance:
        if ghcomp.Absolute(x1-x2) < self.tolerance:
            down = True
        return down
        
    def coverge_slope(self, pt, slopeline):
        _, cur_y, cur_z = ghcomp.Deconstruct(pt)
        left_vec = ghcomp.UnitX(-1)
        left_line = ghcomp.LineSDL(pt, left_vec, 10)
        l_pt, _, _ = ghcomp.CurveXCurve(left_line, slopeline)
        if l_pt:
            pt = l_pt
        else:
            right_vec = ghcomp.UnitX(1)
            right_line = ghcomp.LineSDL(pt, right_vec, 10)
            r_pt, _, _ = ghcomp.CurveXCurve(right_line, slopeline)
            if r_pt:
                pt = r_pt
        return pt
    
    def align_slope(self, pts, slopeline):
        slope_pts, _, dis = ghcomp.CurveClosestPoint(pts, slopeline)
        min = 1000
        anchor_r = -1
        for i in range(len(dis)):
            if dis[i] < min:
                min = dis[i]
                anchor_r = i
        anchor_pt = pts[anchor_r]
        anchor_pt = self.coverge_slope(anchor_pt, slopeline)
        anchor_x, _, _ = ghcomp.Deconstruct(anchor_pt)
    
        for i in range(len(pts)):
           _, cur_y, cur_z = ghcomp.Deconstruct(pts[i])
           align_x = anchor_x + (i-anchor_r)*self.horizontal
           align_pt = ghcomp.ConstructPoint(align_x, cur_y, cur_z)
           pts[i] = align_pt
            
        return pts, anchor_pt

    def generate_slope_grid_pts(self, base_pts, vertical, downline, slopeline):
        pts = []
        bound_pts = []
        dest_pts = []
        
        dest_pts0, _, dis = ghcomp.CurveClosestPoint(base_pts, downline)
        max = 0
        for i in range(len(dis)):
            if dis[i]>max:
                max = dis[i]
        
        base_vec = ghcomp.UnitY(-1)
        
        for i in range(len(dis)):
            base_line = ghcomp.LineSDL(base_pts[i], base_vec, 1.25*max)
            dest_pt, _, _ = ghcomp.CurveXCurve(base_line, downline)
            if dest_pt:
                dest_pts.append(dest_pt)
            else:
                dest_pts.append(dest_pts0[i])
        
        v_dis = ghcomp.Distance(base_pts, dest_pts)
        vlength = ghcomp.Average(v_dis)
        v_num = int(math.floor(vlength/vertical))
        if v_num%2 != 0:
            v_num = v_num - 1
        
        relation, _ = ghcomp.PointInCurve(base_pts, self.boundary)
        base_array_pts, _ = ghcomp.Dispatch(base_pts, relation)
        if base_array_pts:
            bound_pts.append(base_array_pts[0])
    
        for i in range(1, v_num):
            cur_pts = []
            for j in range(len(base_pts)):
                cur_base = base_pts[j]
                cur_dest = dest_pts[j]
                cur_vec, _ = ghcomp.Vector2Pt(cur_base, cur_dest, True)
                cur_dis = i*v_dis[j]/v_num
                line = ghcomp.LineSDL(cur_base, cur_vec, cur_dis)
                _, cur_pt = ghcomp.EndPoints(line)
                cur_pts.append(cur_pt)
            if self.aligned == False:
                if i%2 == 1:
                    shift_pts = []
                    for k in range(len(cur_pts)-1):
                        shift_pts.append(ghcomp.Division(ghcomp.Addition(cur_pts[k], cur_pts[k+1]),2))
                    cur_pts = shift_pts
            
            cur_pts, anchor_pt = self.align_slope(cur_pts, slopeline)
            #bug.append(anchor_pt)
            
            relation, _ = ghcomp.PointInCurve(cur_pts, self.boundary)
            cur_pts, _ = ghcomp.Dispatch(cur_pts, relation)
            if cur_pts:
                cur_pts = construct_safe_pts_list(cur_pts)
                pts += cur_pts
                bound_pts.append(cur_pts[0])
        return dest_pts, pts, bound_pts
    
    def generate_grid_pts(self):
        pts = []
        bound_pts = []
        uplength = ghcomp.Length(self.upline)
        num = int(math.floor(uplength/self.horizontal)+1)
        up_pts, _, _ = ghcomp.DivideCurve(self.upline, num, False)
        up_pts, _ = self.align_slope(up_pts, self.slopeline)
        mid_pts, um_pts, um_bound = self.generate_slope_grid_pts(up_pts, self.vertical, self.downline, self.slopeline)
        
        bound_pts += um_bound
        bound_pts, _ = ghcomp.DeleteConsecutive(bound_pts, False)
        #relation, _ = ghcomp.PointInCurve(bound_pts, boundary)
        #bound_pts, _ = ghcomp.Dispatch(bound_pts, relation)
        
        pts += up_pts
        pts += mid_pts
        relation, _ = ghcomp.PointInCurve(pts, self.boundary)
        pts, _ = ghcomp.Dispatch(pts, relation)
        
        if pts == None:
            pts = []
        pts += um_pts
        
        return pts, bound_pts
    
    def generate_bound_pts(self, head_pts, pts):
        tolerance = 0.1
        
        unit_length = 1
        if self.aligned == False:
            unit_length = math.sqrt(0.25*self.horizontal*self.horizontal+self.vertical*self.vertical)
        else:
            unit_length = math.sqrt(self.horizontal*self.horizontal+self.vertical*self.vertical)
       
        num = int(math.floor(ghcomp.Length(self.split_crv)/unit_length)+1)
        aux_pts, _, _ = ghcomp.DivideCurve(self.split_crv, 3*num, False)
        aux_bound_pts, _, _ = ghcomp.ClosestPoint(aux_pts, pts)
        aux_bound_pts, _ = ghcomp.DeleteConsecutive(aux_bound_pts, False)
        
        _, anchor, _ = ghcomp.Deconstruct(aux_bound_pts[0])
        bound_pts = []
        for i in range(len(head_pts)):
            cur_pt = head_pts[i]
            _, cur_y, _ = ghcomp.Deconstruct(cur_pt)
            if cur_y <= anchor:
                bound_pts.append(cur_pt)
        
        head_pts = bound_pts
        bound_pts = []
        i=0
        j=0
        pre_pt = head_pts[0]
        while i<len(head_pts) and j<len(aux_bound_pts):
            cur_head = head_pts[i]
            cur_aux = aux_bound_pts[j]
            if ghcomp.Distance(cur_head, cur_aux)<tolerance:
                bound_pts.append(cur_head)
                pre_pt = cur_head
                i += 1
                j += 1
            else:
                dis_head = ghcomp.Distance(cur_head, pre_pt)
                dis_aux = ghcomp.Distance(cur_aux, pre_pt)
                if dis_head < dis_aux:
                    bound_pts.append(cur_head)
                    i += 1
                    pre_pt = cur_head
                else:
                    bound_pts.append(cur_aux)
                    j += 1
                    pre_pt = cur_aux
                    
        if i!=len(head_pts):
            for k in range(i, len(head_pts)):
                bound_pts.append(head_pts[k])
        if j!=len(aux_pts):
            for k in range(j, len(aux_bound_pts)):
                bound_pts.append(aux_bound_pts[k])
            
        i=1
        count = len(bound_pts)
        while i<count-1:
            pre_pt = bound_pts[i-1]
            cur_pt = bound_pts[i]
            suc_pt = bound_pts[i+1]
            _, pre_y, _ = ghcomp.Deconstruct(pre_pt)
            _, cur_y, _ = ghcomp.Deconstruct(cur_pt)
            _, suc_y, _ = ghcomp.Deconstruct(suc_pt)
            if cur_y>pre_y and cur_y>suc_y:
                bound_pts.pop(i)
                count -= 1
                continue
            i += 1
        return bound_pts
        
    def generate_white_direc(self, white_pts):
        white_direc = []
        for i in range(len(white_pts)):
            cur_pt = white_pts[i]
            _, t1, d1 = ghcomp.CurveClosestPoint(cur_pt, self.upline)
            _, t2, d2 = ghcomp.CurveClosestPoint(cur_pt, self.downline)
            cur_direc = ghcomp.VectorXYZ(-1, 0, 0)
            _, tgt1, _ = ghcomp.EvaluateCurve(self.upline, t1)
            _, tgt2, _ = ghcomp.EvaluateCurve(self.downline, t2)
            cur_direc = ghcomp.Addition(ghcomp.Multiplication(tgt1, d2/(d1+d2)),ghcomp.Multiplication(tgt2, d1/(d1+d2)))
            white_direc.append(cur_direc)
        return white_direc
    
    def separate_pts(self, seq_pts, seq_direc):
        #data structure: 类似 dictionary
        #list[0]为当前类型的tag
        """ e.g. 
        [['slope', pts],
        ['cross', pts],
        ['slope', pts]]
        """
        
        slope_pts = []
        cross_pts = []
        slope_direcs = []
        cross_direcs = []
        
        pts = []
        direcs = []
        
        pre_type = None
        temp_head = None
        
        for i in range(len(seq_pts)):
            cur_pt = seq_pts[i]
            
            if i!=0:
                pre_pt = seq_pts[i-1]
                if self.ifright(pre_pt, cur_pt):
                    cross_pts.append(cur_pt)
                    cross_direcs.append(seq_direc[i])
                    if len(cross_pts) > 3:
                        if len(slope_pts) != 0:
                            temp_head = (cross_pts[0], cross_direcs[0])
                            #slope_pts.append(cross_pts[0])
                            #slope_direcs.append(cross_direcs[0])
                            cross_pts.insert(0, slope_pts[-1])
                            cross_direcs.insert(0, slope_direcs[-1])
                            slope_pts.append(temp_head[0])
                            slope_direcs.append(temp_head[1])
                            temp_head = None
                            pre_seq = ['slope', slope_pts]
                            pts.append(pre_seq)
                            direcs.append(slope_direcs)
                            slope_pts = []
                            slope_direcs = []
                            pre_type = 'slope'
                    
                else:
                    if len(cross_pts) > 10:
                        if pre_type == 'cross' and temp_head!=None:
                            cross_pts.insert(0, temp_head[0])
                            cross_direcs.insert(0, temp_head[1])
                            temp_head = None
                        pre_seq = ['cross', cross_pts]
                        pts.append(pre_seq)
                        direcs.append(cross_direcs)
                        pre_type = 'cross'
                        #slope_pts.pop()
                        #slope_direcs.pop()
                        temp_head = (cur_pt, seq_direc[i])
                    else:
                        slope_pts += cross_pts
                        slope_direcs += cross_direcs
                        slope_pts.append(cur_pt)
                        slope_direcs.append(seq_direc[i])
                    cross_pts = []
                    cross_direcs = []
            
            if i==len(seq_pts)-1:
                if len(slope_pts) != 0:
                    cur_seq = ['slope', slope_pts]
                    pts.append(cur_seq)
                    direcs.append(slope_direcs)
                    slope_pts = []
                    slope_direcs = []
                if len(cross_pts) != 0:
                    if pre_type == 'cross' and temp_head!=None:
                        cross_pts.insert(0, temp_head[0])
                        cross_direcs.insert(0, temp_head[1])
                        temp_head = None
                    cur_seq = ['cross', cross_pts]
                    pts.append(cur_seq)
                    direcs.append(cross_direcs)
                    cross_pts = []
                    cross_direcs = []
                
        return pts, direcs
    
    def generate_cross_band(self, cross_pts, edge_crv):
        #todo：用tweencrv进行offset
        cross_band = []
        shift_pts = []
        for i in range(len(cross_pts)-1):
            shift_pts.append(ghcomp.Division(ghcomp.Addition(cross_pts[i] + cross_pts[i+1]), 2))
        
        r1 = self.region.rows[0].circle_config.New_cross_r1
        h1 = self.region.rows[0].circle_config.New_cross_position1
        r2 = self.region.rows[0].circle_config.New_cross_r2
        h2 = self.region.rows[0].circle_config.New_cross_position2
        
        print("h1")
        print(h1)
        print("h2")
        print(h2)
        
        std_crv = ghcomp.PolyLine(cross_pts, False)
        real_pts, _, dis = ghcomp.CurveClosestPoint(cross_pts, edge_crv)
        real_dis = ghcomp.Average(dis)
        #factor = real_dis/(h1+r1)
        real_factor = ghcomp.Division(dis, h1+r1)
        des_crv = ghcomp.PolyLine(real_pts, False)
        
        crv21 = ghcomp.OffsetCurve(std_crv, h2, ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), 1)
        band_pts21, _, _ = ghcomp.CurveClosestPoint(shift_pts, crv21)
        crv22 = ghcomp.TweenCurve(std_crv, des_crv, h2/(h1+r1))
        band_pts22, _, _ = ghcomp.CurveClosestPoint(shift_pts, crv22)
        num = len(band_pts21)
        band_pts2 = []
        for i in range(num):
            cur_pt = ghcomp.Addition(ghcomp.Multiplication(band_pts21[i], 1.0*(num-i)/num), ghcomp.Multiplication(band_pts22[i], 1.0*i/num))
            band_pts2.append(cur_pt)

        crv1 = ghcomp.TweenCurve(std_crv, des_crv, h1/(h1+r1))
        band_pts1, _, _ = ghcomp.CurveClosestPoint(cross_pts, crv1)

        circle_band = []
        circle_band += ghcomp.Circle(band_pts2, ghcomp.Multiplication(real_factor, r2))
        circle_band += ghcomp.Circle(band_pts1, ghcomp.Multiplication(real_factor, r1))
        
        for i in range(len(circle_band)): 
            circle_band[i] = rg.NurbsCurve.CreateFromCircle(circle_band[i])
        
        cross_band += circle_band    
        return cross_band
    
    def generate_slope_band(self, slope_pts, h_direcs, edge_crv):
        slope_band = []
        
        r1 = self.region.rows[0].circle_config.New_cross_r1
        h1 = self.region.rows[0].circle_config.New_cross_position1
        r2 = self.region.rows[0].circle_config.New_cross_r2
        h2 = self.region.rows[0].circle_config.New_cross_position2
        r3 = self.region.rows[0].circle_config.New_cross_r3
        
        horizontal = self.horizontal
        if self.aligned == False:
            horizontal = horizontal/2
        
        unit_length = math.sqrt(horizontal*horizontal + self.vertical*self.vertical)
        threshold = 0.2
        
        for i in range(len(h_direcs)):
            cur_pt = slope_pts[i]
            #逆时针旋转45°
            unit_vec, _ = ghcomp.VectorXYZ(horizontal, self.vertical, 0)
            angle, _ = ghcomp.Angle(ghcomp.UnitX(1), unit_vec, ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)))
            
            line, _ = ghcomp.Rotate(ghcomp.LineSDL(cur_pt, h_direcs[i], 10), ghcomp.Pi(1.05)+angle, ghcomp.XYPlane(cur_pt))
            end_pt, _, _ = ghcomp.CurveXCurve(line, edge_crv)
            if end_pt:
                cur_direc, _ = ghcomp.Vector2Pt(cur_pt, end_pt, False)
                dist = ghcomp.Distance(cur_pt, end_pt)
                dist_fac = (dist*ghcomp.Cosine(angle/2))/(h1+r1)
                
                if dist_fac > (1+threshold):
                    line0 = ghcomp.Rotate(ghcomp.LineSDL(cur_pt, h_direcs[i], unit_length*0.9), ghcomp.Pi(1)+angle, ghcomp.XYPlane(cur_pt))
                    _, end_pt0 = ghcomp.EndPoints(line0)
                    slope_band.append(ghcomp.Circle(end_pt0, r2))
                    cur_pt = end_pt0
                    dist = ghcomp.Distance(cur_pt, end_pt)
                    dist_fac = (dist*ghcomp.Cosine(angle/2))/(h1+r1)
                
                _, band_pt2 = ghcomp.EndPoints(ghcomp.LineSDL(cur_pt, cur_direc, dist*h2/(h1+r1)))
                slope_band.append(ghcomp.Circle(band_pt2, r2*dist_fac))
            
            line, _ = ghcomp.Rotate(ghcomp.LineSDL(cur_pt, h_direcs[i], 10), ghcomp.Pi(1.06)+angle, ghcomp.XYPlane(cur_pt))
            end_pt, _, _ = ghcomp.CurveXCurve(line, edge_crv)
            if end_pt:
                cur_direc, _ = ghcomp.Vector2Pt(cur_pt, end_pt, False)
                dist = ghcomp.Distance(cur_pt, end_pt)
                
                _, band_pt1 = ghcomp.EndPoints(ghcomp.LineSDL(cur_pt, cur_direc, dist*h1/(h1+r1)))
                slope_band.append(ghcomp.Circle(band_pt1, r1*dist_fac))
        
        for i in range(len(slope_band)):
            slope_band[i] = rg.NurbsCurve.CreateFromCircle(slope_band[i])
        
        return slope_band
    
    def generate_black_band(self, bound_pts, bound_direcs):
        edge_crv = self.edge_crv
        
        black_band = []
        bug1 = []
        bug2 = []
        for i in range(len(bound_pts)):
            cur_seq = bound_pts[i]
            cur_type = cur_seq[0]
            if cur_type == "slope":
                cur_seq_pts = cur_seq[1]
                bug1 += cur_seq_pts
                cur_direcs = bound_direcs[i]
                black_band += self.generate_slope_band(cur_seq_pts, cur_direcs, edge_crv)
            elif cur_type == "cross":
                cur_seq_pts = cur_seq[1]
                bug2 += cur_seq_pts
                black_band += self.generate_cross_band(cur_seq_pts, edge_crv)
                
        #两部分点：斜向阵列和贴边装饰点
        #横向点直接遵照规则做offset和shift
        return black_band
        
    def bake(self):
        layer_name = 'fuyao_black'
        rs.AddLayer(layer_name, self.display_color)
        for i in range(len(self.frit_black)):
            obj = scriptcontext.doc.Objects.AddCurve(self.frit_black[i])
            rs.ObjectLayer(obj, layer_name)
    
    def run(self):
        pts, bound_pts = self.generate_grid_pts()
        seq_pts = self.generate_bound_pts(head_pts = bound_pts, pts = pts)
        seq_direc = self.generate_white_direc(seq_pts)
        bound_pts, bound_direcs = self.separate_pts(seq_pts, seq_direc)
        black_band = self.generate_black_band(bound_pts, bound_direcs)
        
        for i in range(len(pts)):
            cur_crv = rg.NurbsCurve.CreateFromCircle(rc.Geometry.Circle(pts[i], self.region.rows[0].circle_config.New_cross_r3))
            self.frit_black.append(cur_crv)
            #self.display.AddCurve(cur_crv, self.display_color, 1)
            
        for i in range(len(black_band)):
            self.frit_black.append(black_band[i])
            #self.display.AddCurve(black_band[i], self.display_color, 1)
       
        self.bake()

#原HoleFrits 块状填充算法
class HoleFrits:
    def __init__(self, hole_id, region):
        self.hole_id = hole_id
        self.dot_type = FritType.CIRCLE_DOT
        self.dot_config = CircleDotConfig()
        self.stepping = 0
        self.vspace = 0
        self.first_line_position = 0
        self.circle_config = CircleDotConfig()
        self.round_rect_config = RoundRectConfig()
        
        self.arrange_type = HoleArrangeType.CROSS
        self.dots = []
        self.region = region
        self.top_curve = None
        self.bottom_curve = None
        self.border_curve = None
    
    def New165_fill_dots(self):
        
        print("165算法调用")
        self.outer_crv = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.outer_crv, _ = ghcomp.FlipCurve(self.outer_crv)
        
        self.inner_crv = self.region.curves[1]
        self.inner_crv, _ = ghcomp.FlipCurve(self.inner_crv)
        if self.region.is_flip[1] == True:
            self.inner_crv, _ = ghcomp.FlipCurve(self.inner_crv)
            
        self.top_crv = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_crv, _ = ghcomp.FlipCurve(self.top_crv)
            
        self.bottom_crv = self.region.curves[3]
        if self.region.is_flip[3] == True:
            self.bottom_crv, _ = ghcomp.FlipCurve(self.bottom_crv)
        
        self.refer_crv = self.region.curves[4]
        if self.region.is_flip[4] == True:
            self.refer_crv, _ = ghcomp.FlipCurve(self.refer_crv)
            
        #offset outer_crv
        self.display_color = rc.Display.ColorHSL(0, 1, 0)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
        #crv1 = ghcomp.OffsetCurve(self.outer_crv, distance= 2.4, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), corners=1)
        
        horizontal = self.region.rows[0].stepping
        crv1 = ghcomp.OffsetCurve(self.outer_crv, distance = horizontal, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), corners=1)
        endpt0, _ = ghcomp.EndPoints(self.outer_crv)
        endpt1, _ = ghcomp.EndPoints(crv1)
        _, y0, _ = ghcomp.Deconstruct(endpt0)
        _, y1, _ = ghcomp.Deconstruct(endpt1)
        if y0>y1:
            crv1 = ghcomp.OffsetCurve(self.outer_crv, distance= -horizontal, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), corners=1)
        
        band_config = self.region.rows[0].circle_config
        band_offset = band_config.New_cross_position1
        
        split_crv = ghcomp.OffsetCurve(self.inner_crv, distance = band_offset, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), corners=1)
        endpt0, _ = ghcomp.EndPoints(self.inner_crv)
        endpt1, _ = ghcomp.EndPoints(split_crv)
        _, y0, _ = ghcomp.Deconstruct(endpt0)
        _, y1, _ = ghcomp.Deconstruct(endpt1)
        if y0>y1:
            split_crv = ghcomp.OffsetCurve(self.inner_crv, distance= -band_offset, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), corners=1)
            
        blocksrf = ghcomp.RuledSurface(crv1, split_crv)
        edgelist = []
        
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        #self.display.AddCurve(blockborder, self.display_color, 1)
        
        vertical = self.region.rows[0].position
        unit_length = math.sqrt(0.25*horizontal*horizontal+vertical*vertical)
        offset_fac = 0.2*unit_length
        area0, _ = ghcomp.Area(blockborder)
        boundary_crv = ghcomp.OffsetCurve(blockborder, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), distance = offset_fac, corners=1)
        area1, _ = ghcomp.Area(boundary_crv)
        print("compare!!")
        print(area1)
        print(area0)
        if area1 < area0:
            boundary_crv = ghcomp.OffsetCurve(blockborder, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), distance = -offset_fac, corners=1)
        #self.display.AddCurve(boundary_crv, self.display_color, 1)
        
        upline_crv = ghcomp.OffsetCurve(self.top_crv, plane = rs.WorldXYPlane(), distance=0.5, corners=1)
        #stepping
        New_165_frit_generator = New_165_fill_holes(\
                                upline = self.top_crv, downline = self.bottom_crv, \
                                boundary = boundary_crv, slopeline = self.refer_crv, \
                                split_crv = split_crv, edge_crv = self.inner_crv, \
                                horizontal = horizontal, vertical = vertical, \
                                region = self.region, aligned = False)
        New_165_frit_generator.run()
        
    
    
    def bake(self):
        pass
    
    def dazhong_fill_dots(self):
        self.outer_crv = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.outer_crv, _ = ghcomp.FlipCurve(self.outer_crv)
            
        self.inner_crv = self.region.curves[1]
        self.inner_crv, _ = ghcomp.FlipCurve(self.inner_crv)
        if self.region.is_flip[1] == True:
            self.inner_crv, _ = ghcomp.FlipCurve(self.inner_crv)
            
        self.refer_crv = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.refer_crv, _ = ghcomp.FlipCurve(self.refer_crv)
            
        self.top_crv = self.region.curves[3]
        if self.region.is_flip[3] == True:
            self.top_crv, _ = ghcomp.FlipCurve(self.top_crv)
            
        self.bottom_crv = self.region.curves[4]
        if self.region.is_flip[4] == True:
            self.bottom_crv, _ = ghcomp.FlipCurve(self.bottom_crv)
            
        self.bottom1_crv = self.region.curves[5]
        if self.region.is_flip[5] == True:
            self.bottom1_crv, _ = ghcomp.FlipCurve(self.bottom1_crv)
            
        #offset outer_crv
        self.display_color = rc.Display.ColorHSL(0, 1, 0)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
        #crv1 = ghcomp.OffsetCurve(self.outer_crv, distance= 2.4, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), corners=1)
        
        crv1 = ghcomp.OffsetCurve(self.outer_crv, distance= 2.4, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), corners=1)
        endpt0, _ = ghcomp.EndPoints(self.outer_crv)
        endpt1, _ = ghcomp.EndPoints(crv1)
        _, y0, _ = ghcomp.Deconstruct(endpt0)
        _, y1, _ = ghcomp.Deconstruct(endpt1)
        if y0>y1:
            crv1 = ghcomp.OffsetCurve(self.outer_crv, distance= -2.4, plane = ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)), corners=1)
        
        blocksrf = ghcomp.RuledSurface(crv1, self.refer_crv)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        #self.display.AddCurve(blockborder, self.display_color, 1)
        boundary_crv = ghcomp.OffsetCurve(blockborder,  plane = rs.WorldXYPlane(),distance=-0.1, corners=1)
        #self.display.AddCurve(boundary_crv, self.display_color, 1)
        upline_crv = ghcomp.OffsetCurve(self.top_crv, plane = rs.WorldXYPlane(), distance=0.5, corners=1)
        #stepping
        dazhong_frit_generator = Dazhong_fill_holes(\
                                    upline = upline_crv, midline = self.bottom_crv, downline = self.bottom1_crv, \
                                    boundary = boundary_crv, split_crv = self.refer_crv, edge_crv = self.inner_crv, \
                                    horizontal = self.region.rows[0].stepping, vertical = self.region.rows[0].position, region = self.region,aligned = False)
        dazhong_frit_generator.run()
        
        
    def fill_dots_88LFW(self):
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        
        first_line_curve = ghcomp.OffsetCurve(self.top_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        crv_length = ghcomp.Length(first_line_curve)   
        pts_num = int(crv_length / self.stepping)
        line_pts, _, t = ghcomp.DivideCurve(first_line_curve, pts_num, False)
        new_t = []
        for i in range(len(t) - 1):
            new_t.append((t[i] + t[i + 1]) / 2)
        
        cross_pts, vec, _ = ghcomp.EvaluateCurve(first_line_curve, new_t)
        
        _, _, blockborder = self.construct_border(self.top_curve, self.bottom_curve)
        # 估计排数
        bbox = blockborder.GetBoundingBox(True)
        
        leftup = bbox.Min
        bottomright = bbox.Max
      
        yStart = leftup.Y
        yEnd = bottomright.Y
        
       
        yLength = yEnd - yStart 
        
        # 随便估算一下
        yCount = int(math.ceil(yLength / self.vspace) / 2 + 2)
        bottom_pts = []
        all_dots = []
        dots_list = []
        for i in range(yCount):
            l2 = ghcomp.Addition(rg.Vector3d(0, -self.vspace * 2 * i, 0), cross_pts)
            l3 = ghcomp.Addition(rg.Vector3d(0, -self.vspace * (2* i + 1), 0), line_pts)
            new_l2 = []
            new_l3 = []
            for pt in l2:
                PtCtmt = blockborder.Contains(pt)
                if PtCtmt == rg.PointContainment.Inside:
                    new_l2.append(pt)
            
            for pt in l3:
                PtCtmt = blockborder.Contains(pt)
                if PtCtmt == rg.PointContainment.Inside:
                    new_l3.append(pt)
            if len(new_l2):
                dots_list.append(new_l2)
            if len(new_l3):
                dots_list.append(new_l3)
        big_dots = []
        start_pt, end_pt = ghcomp.EndPoints(self.top_curve)
        #首先判断斜率得方向
        sx, sy, sz = ghcomp.Deconstruct(start_pt)
        ex, ey, ez = ghcomp.Deconstruct(end_pt)
        left_or_right = 1 # 左边
        if (ey - sy) * (ex - sx) > 0:
            left_or_right = -1 # 右边
        if left_or_right == 1:
            for i in range(len(dots_list)):
                for j in range(len(dots_list[i])):
                    if i == len(dots_list) - 1:
                        bottom_pts.append(dots_list[i][j])
                    else:
                        dot = dots_list[i][j]
                        dot1 = dots_list[i+1][0]
                        dx, _, _ = ghcomp.Deconstruct(dot)
                        dx1, _, _ = ghcomp.Deconstruct(dot1)
                        if dx < dx1:
                            bottom_pts.append(dot)
                        else:
                            break
        else:
            for i in range(len(dots_list)):
            
                for j in range(len(dots_list[i])):
                    if i == len(dots_list) - 1:
                        bottom_pts.append(dots_list[i][j])
                    else:
                        dot = dots_list[i][len(dots_list[i]) - 1- j]
                        dot1 = dots_list[i+1][len(dots_list[i + 1]) - 1]
                        dx, _, _ = ghcomp.Deconstruct(dot)
                        dx1, _, _ = ghcomp.Deconstruct(dot1)
                        if dx > dx1:
                            bottom_pts.append(dot)
                        else:
                            break
        for i in range(0, len(dots_list) - 1):
            big_dots += dots_list[i]
        big_dots += dots_list[-1]
        # draw big dots
        for i in range(len(big_dots)):
            theta = 0 # utils.tgt_angle(vec[i])
            c = CircleDotConfig()
            c.r = 1
            dot = CircleDot(big_dots[i].X, big_dots[i].Y, c, theta)
            self.dots.append(dot)

        
        small_curve = self.region.curves[1]
        if self.region.is_flip[1] == True:
            small_curve, _ = ghcomp.FlipCurve(small_curve)
         # 从顶部发射射线与下部相交
        default_length = 500
        dirc = rg.Vector3d(-left_or_right * self.stepping / 2, -self.vspace, 0)
        diag_lines = ghcomp.LineSDL(bottom_pts, dirc, default_length)

        # 射线与底线相交
        offset_dis = -0.5
        bcurve = ghcomp.OffsetCurve(small_curve, plane = rs.WorldXYPlane(), distance=offset_dis, corners=1)
        line = []
        fill_pts = []
        for i in range(len(diag_lines)):
            small_pts, _, _ = ghcomp.CurveXCurve(diag_lines[i], bcurve)
            if small_pts:
                line.append(ghcomp.Line(bottom_pts[i], small_pts))
            
        
        # line = ghcomp.Line(top_pts, bottom_pts)
        unit_length = math.sqrt(0.25 * self.stepping * self.stepping + self.vspace * self.vspace)
        for l in line:
            crv_length = ghcomp.Length(l)   
            pts_num = int(crv_length / unit_length)
            # offset curve
            line_pts, _, t = ghcomp.DivideCurve(l, pts_num, False)
            #line_pts.reverse()
            if line_pts:
                line_pts.reverse()
                # line_pts = line_pts[1:]
                if line_pts:
                    for i in range(len(line_pts) - 1): 
                        c = CircleDotConfig()
                        c.r = 0.5 + 0.1 * i
                        dot = CircleDot(line_pts[i].X, line_pts[i].Y, c, 0)
                        self.dots.append(dot)
        

    # 76720LFW00027
    def fill_dots_76720LFW00027(self):
        # top_curve
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        
        box = ghcomp.BoundingBox(self.top_curve, rs.WorldXYPlane())
        box_centroid, _, _, _, _ = ghcomp.BoxProperties(box)
        cx, cy, cz = ghcomp.Deconstruct(box_centroid[0])
        # 向下平移半径长度
        # 这里先假设是圆形
        curve = ghcomp.OffsetCurve(self.top_curve, plane = rs.WorldXYPlane(), distance=0.36, corners=1)
        # 先画一条水平线
        start_pt, end_pt = ghcomp.EndPoints(curve)
        #首先判断斜率得方向
        sx, sy, sz = ghcomp.Deconstruct(start_pt)
        ex, ey, ez = ghcomp.Deconstruct(end_pt)
        left_or_right = 1 # 左边
        if (ey - sy) * (ex - sx) > 0:
            left_or_right = -1 # 右边
        sx0 = sx - left_or_right * (sy - cy) / self.vspace / 2  * self.stepping
        ex0 = ex - left_or_right * (ey - cy) / self.vspace / 2 * self.stepping
        pts_num = int(abs(ex0 - sx0) / self.stepping)
        xs = []
        default_xd = 500
        top_pts = []
        for i in range(pts_num + 1):
            mx = sx0 + i * (ex0 - sx0) / pts_num
            lx = mx - default_xd
            ly = cy - left_or_right * default_xd * self.vspace * 2 / self.stepping
            rx = mx + default_xd
            ry = cy + left_or_right * default_xd * self.vspace * 2 /self.stepping
            line = ghcomp.Line(rg.Point3d(lx, ly, 0), rg.Point3d(rx, ry, 0))
            jpt, _, _ = ghcomp.CurveXCurve(line, curve)
            top_pts.append(jpt)
        # offset curve
        
        # 从顶部发射射线与下部相交
        default_length = 500
        dirc = rg.Vector3d(-left_or_right * self.stepping / 2, -self.vspace, 0)
        diag_lines = ghcomp.LineSDL(top_pts, dirc, default_length)

        # 射线与底线相交
        offset_dis = -0.5
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        bcurve = ghcomp.OffsetCurve(self.bottom_curve, plane = rs.WorldXYPlane(), distance=offset_dis, corners=1)
        line = []
        fill_pts = []
        for i in range(len(diag_lines)):
            bottom_pts, _, _ = ghcomp.CurveXCurve(diag_lines[i], bcurve)
            if bottom_pts:
                line.append(ghcomp.Line(top_pts[i], bottom_pts))
            
        
        # line = ghcomp.Line(top_pts, bottom_pts)
        unit_length = math.sqrt(0.25 * self.stepping * self.stepping + self.vspace * self.vspace)

        
        for l in line:
            crv_length = ghcomp.Length(l)   
            pts_num = int(crv_length / unit_length)
            # offset curve
            line_pts, _, t = ghcomp.DivideCurve(l, pts_num, False)
            if line_pts:
                fill_pts += line_pts[1:]
            

        for i in range(len(top_pts)):
            theta = ghcomp.Pi() * 0.25 # utils.tgt_angle(vec[i])
            c = RoundRectConfig()
            c.k = 0.6
            c.r = 0.15
            dot = RoundRectDot(top_pts[i].X, top_pts[i].Y, c, theta)
            self.dots.append(dot)

        for i in range(len(fill_pts)):
            theta = ghcomp.Pi() * 0.25 # utils.tgt_angle(vec[i])
            dot = RoundRectDot(fill_pts[i].X, fill_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)

    def fill_from_bottom(self):
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        
        start_pt, end_pt = ghcomp.EndPoints(self.top_curve)
        #首先判断斜率得方向
        sx, sy, sz = ghcomp.Deconstruct(start_pt)
        ex, ey, ez = ghcomp.Deconstruct(end_pt)
        left_or_right = 1 # 左边
        if (ey - sy) * (ex - sx) > 0:
            left_or_right = -1 # 右边
        first_line_curve = self.region.curves[1]
        if self.region.is_flip[1] == True:
            first_line_curve, _ = ghcomp.FlipCurve(self.region.curves[1])
        first_line_curve = ghcomp.OffsetCurve(first_line_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        crv_length = ghcomp.Length(first_line_curve)   
        pts_num = int(crv_length / self.stepping)
        line_pts, v1, t = ghcomp.DivideCurve(first_line_curve, pts_num, False)
         # cross
        new_t = []
        for i in range(len(t) - 1):
            new_t.append((t[i] + t[i + 1]) / 2)
        
        cross_pts, v1, _ = ghcomp.EvaluateCurve(first_line_curve, new_t)
        # 旋转90度做垂线，分别往两个方向分别取100个点
        v2 = rg.Vector3d(left_or_right * self.stepping / 2, self.vspace, 0)
        all_dots = list(cross_pts)
        for i in range(1, 300):
            l2 = ghcomp.Addition(ghcomp.Multiplication(v2, i), cross_pts) 
            all_dots += l2
        # 边界
        # bcurve = ghcomp.OffsetCurve(self.bottom_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        tcurve = self.top_curve
        bcurve = self.bottom_curve
        _, _, blockborder = self.construct_border(tcurve, bcurve)
        # blockborder = ghcomp.OffsetCurve(blockborder, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        filter_pts = []
        for pt in all_dots:
            PtCtmt = blockborder.Contains(pt)
            if PtCtmt == rg.PointContainment.Inside:
                filter_pts.append(pt)
        
        for i in range(len(filter_pts)):
            theta = 0
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(filter_pts[i].X, filter_pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(filter_pts[i].X, filter_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)

    # 针对00215 设计填充算法

    def fill_angle(self):
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        first_line_curve = self.region.curves[1]
        if self.region.is_flip[1] == True:
            first_line_curve, _ = ghcomp.FlipCurve(self.region.curves[1])
        first_line_curve = ghcomp.OffsetCurve(first_line_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        second_curve = ghcomp.OffsetCurve(self.bottom_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        # second_curve = ghcomp.RebuildCurve(second_curve, 3, 300, True) 
         # 先画一条水平线
        start_pt, end_pt = ghcomp.EndPoints(self.top_curve)
        #首先判断斜率得方向
        sx, sy, sz = ghcomp.Deconstruct(start_pt)
        ex, ey, ez = ghcomp.Deconstruct(end_pt)
        left_or_right = 1 # 左边
        if (ey - sy) * (ex - sx) > 0:
            left_or_right = -1 # 右边
        crv_length = ghcomp.Length(first_line_curve)   
        pts_num = int(crv_length / self.stepping)
        line_pts, v1, t = ghcomp.DivideCurve(first_line_curve, pts_num, False)
        # cross
        new_t = []
        for i in range(len(t) - 1):
            new_t.append((t[i] + t[i + 1]) / 2)
        
        cross_pts, v1, _ = ghcomp.EvaluateCurve(first_line_curve, new_t)
        # 旋转90度做垂线，分别往两个方向分别取100个点
        new_v = list()
        for i in range(len(v1)):
            new_v.append(v1[1])
        # fuck Fuck fuck!!! 离谱！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！必须写小数
        v2, _ = ghcomp.Rotate(new_v, ghcomp.Pi()*(-0.3333) * left_or_right, rg.Point3d(0, 0, 0))
        # ghcomp.Rotate(
        print(v2[0])
        
        top_pts = []
        
        for i in range(len(cross_pts)):     
            line = ghcomp.LineSDL(cross_pts[i], -v2[i], 500)
            # cl = rg.NurbsCurve.CreateFromLine(line)
            # events = rg.Intersect.Intersection.CurveCurve(second_curve, cl, 0.001, 0.0)
            # jpt = rs.CurveCurveIntersection(line,second_curve)
            jpt, _, _ = ghcomp.CurveXCurve(line, second_curve)
            if jpt:
                top_pts.append(jpt)
            line = ghcomp.LineSDL(cross_pts[i], v2[i], 500)
            jpt, _, _ = ghcomp.CurveXCurve(line, second_curve)
            if jpt:
                top_pts.append(jpt)
        # offset curve
        
        # 从顶部发射射线与下部相交
        default_length = 500
        
        diag_lines = ghcomp.LineSDL(top_pts, -v2[0] * left_or_right, default_length)

        # 射线与底线相交
        # offset_dis = self.first_line_position # self.region.rows[-1].position - self.vspace - 0.1
        
        bcurve = ghcomp.OffsetCurve(self.top_curve, plane = rs.WorldXYPlane(), distance=0, corners=1)
        line = []
        fill_pts = []
        for i in range(len(diag_lines)):
            bottom_pts, _, _ = ghcomp.CurveXCurve(diag_lines[i], bcurve)
            if bottom_pts:
                line.append(ghcomp.Line(top_pts[i], bottom_pts))
            else:
                fill_pts.append(top_pts[i])
        
        # line = ghcomp.Line(top_pts, bottom_pts)
        unit_length = math.sqrt(0.25 * self.stepping * self.stepping + self.vspace * self.vspace)

        
        for l in line:
            crv_length = ghcomp.Length(l)   
            pts_num = int(crv_length / unit_length)
            # offset curve
            line_pts, _, t = ghcomp.DivideCurve(l, pts_num, False)
            if line_pts:
                fill_pts += line_pts
            else:
                sp, ep = ghcomp.EndPoints(l)
                fill_pts.append(sp)

        # 边界
        blocksrf = ghcomp.RuledSurface(self.top_curve, self.bottom_curve)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        blockborder = ghcomp.OffsetCurve(blockborder, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        filter_pts = []
        for pt in fill_pts:
            PtCtmt = blockborder.Contains(pt)
            if PtCtmt == rg.PointContainment.Inside:
                filter_pts.append(pt)
        
        for i in range(len(filter_pts)):
            theta = tgt_angle(v1[0])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(filter_pts[i].X, filter_pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(filter_pts[i].X, filter_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)


    # 针对00841LFW00001 设计填充算法
    def fill_simple(self):
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        
        first_line_curve = ghcomp.OffsetCurve(self.top_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        crv_length = ghcomp.Length(first_line_curve)   
        pts_num = int(crv_length / self.stepping)
        line_pts, _, t = ghcomp.DivideCurve(first_line_curve, pts_num, False)
        new_t = []
        for i in range(len(t) - 1):
            new_t.append((t[i] + t[i + 1]) / 2)
        
        cross_pts, vec, _ = ghcomp.EvaluateCurve(first_line_curve, new_t)
        
        blocksrf = ghcomp.RuledSurface(self.top_curve, self.bottom_curve)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        # 估计排数
        bbox = blockborder.GetBoundingBox(True)
        
        leftup = bbox.Min
        bottomright = bbox.Max
      
        yStart = leftup.Y
        yEnd = bottomright.Y
        
       
        yLength = yEnd - yStart 
        
        # 随便估算一下
        yCount = int(math.ceil(yLength / self.vspace) / 2 + 2)
        all_dots = []
        for i in range(yCount):
            l2 = ghcomp.Addition(rg.Vector3d(0, -self.vspace * 2 * i, 0), line_pts)
            l3 = ghcomp.Addition(rg.Vector3d(0, -self.vspace * (2* i + 1), 0), cross_pts)
            all_dots += l2
            all_dots += l3
        if self.dot_type == FritType.CIRCLE_DOT:
            blockborder = ghcomp.OffsetCurve(blockborder, plane = rs.WorldXYPlane(), distance=-self.circle_config.r, corners=1)
        elif self.dot_type == FritType.ROUND_RECT:
             blockborder = ghcomp.OffsetCurve(blockborder, plane = rs.WorldXYPlane(), distance=-self.round_rect_config.k / 2, corners=1)
        filter_pts = []
        for pt in all_dots:
            PtCtmt = blockborder.Contains(pt)
            if PtCtmt == rg.PointContainment.Inside:
                filter_pts.append(pt)
        
        for i in range(len(filter_pts)):
            theta = 0
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(filter_pts[i].X, filter_pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(filter_pts[i].X, filter_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)

    # 针对00399LFW00012 设计填充算法
    # curve[0] 是黑白分界线
    # curve[1] 是分界线上的直线延长线，通过确保len(curve[1])= len(curve[0])保证了上下点对齐
    # curve[2] 是上分界线
    def fill_one_line(self):
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        first_line_curve = self.region.curves[1]
        if self.region.is_flip[1] == True:
            first_line_curve, _ = ghcomp.FlipCurve(self.region.curves[1])
        first_line_curve = ghcomp.OffsetCurve(first_line_curve, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        crv_length = ghcomp.Length(first_line_curve)   
        pts_num = int(crv_length / self.stepping)
        line_pts, v1, t = ghcomp.DivideCurve(first_line_curve, pts_num, False)
        
        # 旋转90度做垂线，分别往两个方向分别取100个点
        v2, _ = ghcomp.Rotate(v1, ghcomp.Pi(0.5), rg.Point3d(0, 0, 0))
        all_dots = list(line_pts)
        for i in range(1, 100):
            l2 = ghcomp.Addition(ghcomp.Multiplication(v2, i* self.vspace), line_pts) 
            all_dots += l2 
            l3 = ghcomp.Addition(ghcomp.Multiplication(v2, -i* self.vspace), line_pts)
            all_dots += l3
        
        # 边界
        blocksrf = ghcomp.RuledSurface(self.top_curve, self.bottom_curve)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        blockborder = ghcomp.OffsetCurve(blockborder, plane = rs.WorldXYPlane(), distance=self.first_line_position, corners=1)
        filter_pts = []
        for pt in all_dots:
            PtCtmt = blockborder.Contains(pt)
            if PtCtmt == rg.PointContainment.Inside:
                filter_pts.append(pt)
        
        for i in range(len(filter_pts)):
            theta = tgt_angle(v1[0])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(filter_pts[i].X, filter_pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(filter_pts[i].X, filter_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)


    # 针对00792LFW000023 设计填充算法
    def fill_dots_diag_and_sticky(self):
        # top_curve
        self.top_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            self.top_curve, _ = ghcomp.FlipCurve(self.top_curve)
        box = ghcomp.BoundingBox(self.top_curve, rs.WorldXYPlane())
        box_centroid, _, _, _, _ = ghcomp.BoxProperties(box)
        cx, cy, cz = ghcomp.Deconstruct(box_centroid[0])
        # 向下平移半径长度
        # 这里先假设是圆形
        curve = ghcomp.OffsetCurve(self.top_curve, plane = rs.WorldXYPlane(), distance=self.circle_config.r, corners=1)
        # 先画一条水平线
        start_pt, end_pt = ghcomp.EndPoints(curve)
        #首先判断斜率得方向
        sx, sy, sz = ghcomp.Deconstruct(start_pt)
        ex, ey, ez = ghcomp.Deconstruct(end_pt)
        left_or_right = 1 # 左边
        if (ey - sy) * (ex - sx) > 0:
            left_or_right = -1 # 右边
        sx0 = sx - left_or_right * (sy - cy) / self.vspace / 2  * self.stepping
        ex0 = ex - left_or_right * (ey - cy) / self.vspace / 2 * self.stepping
        pts_num = int(abs(ex0 - sx0) / self.stepping)
        xs = []
        default_xd = 500
        top_pts = []
        for i in range(pts_num + 1):
            mx = sx0 + i * (ex0 - sx0) / pts_num
            lx = mx - default_xd
            ly = cy - left_or_right * default_xd * self.vspace * 2 / self.stepping
            rx = mx + default_xd
            ry = cy + left_or_right * default_xd * self.vspace * 2 /self.stepping
            line = ghcomp.Line(rg.Point3d(lx, ly, 0), rg.Point3d(rx, ry, 0))
            jpt, _, _ = ghcomp.CurveXCurve(line, curve)
            top_pts.append(jpt)
        # offset curve
        
        # 从顶部发射射线与下部相交
        default_length = 500
        dirc = rg.Vector3d(-left_or_right * self.stepping / 2, -self.vspace, 0)
        diag_lines = ghcomp.LineSDL(top_pts, dirc, default_length)

        # 射线与底线相交
        offset_dis = self.region.rows[-1].position - self.vspace - 0.2
        self.bottom_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.bottom_curve, _ = ghcomp.FlipCurve(self.bottom_curve)
        bcurve = ghcomp.OffsetCurve(self.bottom_curve, plane = rs.WorldXYPlane(), distance=offset_dis, corners=1)
        line = []
        fill_pts = []
        for i in range(len(diag_lines)):
            bottom_pts, _, _ = ghcomp.CurveXCurve(diag_lines[i], bcurve)
            if bottom_pts:
                line.append(ghcomp.Line(top_pts[i], bottom_pts))
            else:
                fill_pts.append(top_pts[i])
        
        # line = ghcomp.Line(top_pts, bottom_pts)
        unit_length = math.sqrt(0.25 * self.stepping * self.stepping + self.vspace * self.vspace)

        
        for l in line:
            crv_length = ghcomp.Length(l)   
            pts_num = int(crv_length / unit_length)
            # offset curve
            line_pts, _, t = ghcomp.DivideCurve(l, pts_num, False)
            if line_pts:
                fill_pts += line_pts
            else:
                sp, ep = ghcomp.EndPoints(l)
                fill_pts.append(sp)
                
        for i in range(len(fill_pts)):
            theta = 0 # utils.tgt_angle(vec[i])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(fill_pts[i].X, fill_pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(fill_pts[i].X, fill_pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)

    def fill_dots(self):
        print(con.type+'算法')
        if con.type == '大众图纸':
            pass
        elif con.type == '88LF':
            self.fill_dots_88LFW()
        elif con.type == '76720LFW00027':
            self.fill_dots_76720LFW00027()
        #elif con.type == '00215':
            #self.fill_angle()
        elif con.type == '00841LFW00001':
            self.fill_simple()
        elif con.type == '00399LFW00012':
            self.fill_one_line()
        elif con.type == '00792LFW000023':
            self.fill_dots_diag_and_sticky()
        # self.fill_from_bottom()
        # self.fill_simple()
        # self.fill_dots_88LFW()
        # self.fill_dots_76720LFW00027()
        # self.fill_one_line()
        # self.fill_dots_diag_and_sticky()

    def general_fill_dots(self):
        #outer_anchor = []
        print(self.hole_id)
        row_num = len(self.region.rows)
        top_curve = None
        bottom_curve = None
        top_anchor = []
        bottom_anchor = []
        for i in range(row_num):
            if self.region.rows[i].row_id < 0:
                bottom_curve = self.region.rows[i - 1].get_top_curve()
                bottom_dots = self.region.rows[i - 1].dots
                for j in range(len(bottom_dots)):
                    bottom_anchor.append(bottom_dots[j].centroid)
                #outer_anchor += bottom_anchor
                #print(len(bottom_anchor))
                break
        
        top_curve = self.region.rows[-1].get_bottom_curve()
        top_dots = self.region.rows[-1].dots
        for j in range(len(top_dots)):
            top_anchor.append(top_dots[j].centroid)
            
        #top_anchor = ghcomp.ReverseList(top_anchor)
        #outer_anchor += top_anchor
        
        #print("*****get anchor*****")
        #print(len(top_anchor))
        #print(len(outer_anchor))
        #stepping = self.region.rows[-1].stepping
        
        _, _, self.border_curve = self.construct_border(top_curve, bottom_curve)
        
        self.block_fill(self.border_curve, top_anchor, bottom_anchor, self.stepping, self.vspace, self.arrange_type)

    def trim_curve(self, crv, t1, t2):
        _, crv_domain = ghcomp.CurveDomain(crv)
        tstart, tend = ghcomp.DeconstructDomain(crv_domain)
        mid = (tstart + tend) / 2
        if t1 > mid:
            t1 = tstart
        if t2 < mid:
            t2 = tend
        domain = ghcomp.ConstructDomain(t1, t2)
        subcrv = ghcomp.SubCurve(crv, domain)
        
        return subcrv
        
    def construct_border(self, top_border, bottom_border):
        _, tA, tB = ghcomp.CurveXCurve(top_border, bottom_border)
        top_subcrv = top_border
        bottom_subcrv = bottom_border
        
        if tA:
            try:
                top_subcrv = self.trim_curve(top_border, tA[0], tA[-1])
            except:
                top_subcrv = self.trim_curve(top_border, tA, tA)
        if tB:
            try:
                bottom_subcrv = self.trim_curve(bottom_border, tB[0], tB[-1])
            except:
                bottom_subcrv = self.trim_curve(bottom_border, tB, tB)
        
        #self.display.AddCurve(top_subcrv)
        #self.display.AddCurve(bottom_subcrv)
        
        blocksrf = ghcomp.RuledSurface(top_subcrv, bottom_subcrv)
        edgelist = []
        for i in range(blocksrf.Edges.Count):
            edgelist.append(blocksrf.Edges[i].EdgeCurve)
        blockborder = ghcomp.JoinCurves(edgelist)
        #self.display.AddCurve(blockborder)
        
        return top_subcrv, bottom_subcrv, blockborder

    def block_fill(self, Crv, top_outer_anchor, bottom_outer_anchor, horizontal, vertical, aligned):
        # self.display.AddCurve(blockborder)
        Pt = []

        threshold = min(horizontal, vertical)
        
        
        bbox = Crv.GetBoundingBox(True)
        
        leftup = bbox.Min
        bottomright = bbox.Max
        
        xStart = leftup.X
        xEnd = bottomright.X
        yStart = leftup.Y
        yEnd = bottomright.Y
        
        xLength = xEnd - xStart
        yLength = yEnd - yStart 
        
        xCount = int(math.ceil(xLength / horizontal))
        yCount = int(math.ceil(yLength / vertical))
        print(xCount, yCount)
        
        for i in range(xCount + 1):
            for j in range(yCount + 1):
                if aligned == HoleArrangeType.HEADING:
                    pt = rg.Point3d(xStart + i*horizontal, yStart + j*vertical, 0)
                else:
                    if j%2 == 0:
                        pt = rg.Point3d(xStart + i*horizontal, yStart + j*vertical, 0)
                    else:
                        pt = rg.Point3d(xStart + (i+0.5)*horizontal, yStart + j*vertical, 0)
                
                PtCtmt = Crv.Contains(pt)
                if PtCtmt == rg.PointContainment.Inside:
                    Pt.append(pt)
        
        #iterate force conduct algo
        pts = self.force_conduct(Pt, Crv, top_outer_anchor, bottom_outer_anchor, horizontal, vertical, aligned)
        #pts = Pt

        for i in range(len(pts)):
            theta = 0 # utils.tgt_angle(vec[i])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(pts[i].X, pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(pts[i].X, pts[i].Y, self.round_rect_config, theta)
            self.dots.append(dot)
    
    def force_conduct(self, inner_pts, outer_border, top_outer_anchor, bottom_outer_anchor, horizontal, vertical, aligned):
        #To do: send aligned parameters in !!!
        
        aligned = False
        
        outer_anchor = ghcomp.Merge(top_outer_anchor, bottom_outer_anchor)
        hspace = (horizontal+vertical)/2
        
        #outer_anchor_num = int(ghcomp.Length(outer_border)/hspace)
        #outer_anchor, _, _ = ghcomp.DivideCurve(outer_border, outer_anchor_num, False)
        
        offset = horizontal
        if aligned == True:
            offset = math.sqrt(horizontal*horizontal + vertical*vertical)
        
        else:
            offset = math.sqrt(0.25*horizontal*horizontal + vertical*vertical)
            vertical = 2 * vertical
        
        
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
        self.display.AddCurve(outer_border, self.display_color, 1)
        #scriptcontext.doc.Views.Redraw()
        
        inner_aux_border = ghcomp.OffsetCurve(outer_border, 5*offset, plane=ghcomp.XYPlane(), corners = 1)
        verbose_aux_border = ghcomp.OffsetCurve(outer_border, 6*offset, plane=ghcomp.XYPlane(), corners = 1)
        
        aux_num = int(3 * ghcomp.Length(inner_aux_border) / hspace)
        aux_pts, _, _ = ghcomp.DivideCurve(inner_aux_border, aux_num, False)
        verbose_pts, _, _ = ghcomp.ClosestPoint(aux_pts, inner_pts)
        verbose_pts, _ = ghcomp.DeleteConsecutive(verbose_pts, True)
        print("****check original verbose****")
        print(len(verbose_pts))
        
        flag = True
        inner_anchor = []
        while flag == True:
            temp = copy.deepcopy(verbose_pts)
            inner_anchor1, inner_anchor2, flag = remove_verbose(temp)
            #print("****check verbose****")
            #print(len(verbose_pts))
            #print(len(inner_anchor1))
            #print(len(inner_anchor2))
            inner_anchor = inner_anchor1
            verbose_pts = inner_anchor1
            if len(inner_anchor2) > len(inner_anchor1):
                inner_anchor = inner_anchor2
                verbose_pts = inner_anchor2
        
        """
        odd_even = ghcomp.Merge(True, False)
        odd_pts, even_pts = ghcomp.Dispatch(inner_anchor, odd_even)
        odd_pts, _ = ghcomp.DeleteConsecutive(odd_pts, False)
        even_pts, _ = ghcomp.DeleteConsecutive(even_pts, False)
        inner_anchor = ghcomp.Merge(odd_pts, even_pts)
        """
        
        inner_border = ghcomp.PolyLine(inner_anchor, True)
        self.display.AddCurve(inner_border, self.display_color, 1)
        scriptcontext.doc.Views.Redraw()
        
        relationship, _ = ghcomp.PointInCurve(inner_pts, inner_border)
        outside_pattern, _ = ghcomp.Equality(relationship, 0)
        iter_pts, _ = ghcomp.Dispatch(inner_pts, outside_pattern)
        inside_pattern, _ = ghcomp.Equality(relationship, 2)
        fix_pts, _ = ghcomp.Dispatch(inner_pts, inside_pattern)
        
        verbose_iter_pts = copy.deepcopy(iter_pts)
        relationship, _ = ghcomp.PointInCurve(iter_pts, verbose_aux_border)
        aux_pattern, _ = ghcomp.Equality(relationship, 2)
        bug_pts, iter_pts = ghcomp.Dispatch(iter_pts, aux_pattern)
        if bug_pts:
            if len(iter_pts) == len(verbose_iter_pts) - 1:
                fix_pts.append(ghcomp.ConstructPoint(bug_pts[0],bug_pts[1],bug_pts[2]))
            else:
                fix_pts += bug_pts
        
        anchor_pts = ghcomp.Merge(outer_anchor, inner_anchor)
        all_pts = ghcomp.Merge(anchor_pts, iter_pts)
        
        top_crv = ghcomp.PolyLine(top_outer_anchor, False)
        bottom_crv = ghcomp.PolyLine(bottom_outer_anchor, False)
        
        _, _, outer_anchor_border = self.construct_border(top_crv, bottom_crv)
        
        outer_mesh, inner_mesh, ring_mesh = self.construct_ring_mesh(outer_anchor_border, inner_border, all_pts)
        _, mesh_edges, _ = ghcomp.MeshEdges(ring_mesh)
        
        edge_midpt = ghcomp.CurveMiddle(mesh_edges)
        edge_pattern, _ = ghcomp.PointInCurve(edge_midpt, outer_anchor_border)
        raw_line, _ = ghcomp.Dispatch(mesh_edges, edge_pattern)
        start_pt, end_pt = ghcomp.EndPoints(raw_line)
        oncrv1, _ = ghcomp.PointInCurve(start_pt, outer_anchor_border)
        oncrv2, _ = ghcomp.PointInCurve(end_pt, outer_anchor_border)
        oncrv_pattern, _ = ghcomp.Equality(oncrv1, oncrv2)
        inner_line, border_line = ghcomp.Dispatch(mesh_edges, oncrv_pattern)
        
        #for i in range(len(inner_line)):
        #    crv = rg.NurbsCurve.CreateFromLine(inner_line[i])
        #    self.display.AddCurve(crv, self.display_color, 1)
        #iter_pts += anchor_pts
        
        threshold = horizontal
        if vertical < threshold:
            threshold = vertical
        if offset < threshold:
            threshold = offset
        #threshold = (offset + threshold)/2
        
        link = horizontal
        if vertical < link:
            link = vertical
        if offset > link:
            link = offset
        
        print("length parameter threshold offset link:")
        print(threshold)
        print(offset)
        print(link)
        
        
        goal_anchor = ghcomp.Kangaroo2Component.Anchor(point = anchor_pts, strength = 10000)
        goal_zfix = ghcomp.Kangaroo2Component.AnchorXYZ(point = all_pts, x = False, y = False, z = True, strength = 1000)
        goal_cpcin = ghcomp.Kangaroo2Component.CurvePointCollide(points = iter_pts, curve = outer_border, plane = ghcomp.XYPlane(), interior = True, strength = 1)
        goal_cpcout = ghcomp.Kangaroo2Component.CurvePointCollide(points = iter_pts, curve = inner_border, plane = ghcomp.XYPlane(), interior = False, strength = 1)
        goal_cpcin = [goal_cpcin]
        goal_cpcout = [goal_cpcout]
        goal_inner_length = ghcomp.Kangaroo2Component.LengthLine(line = inner_line, strength = 0.15)
        goal_inner_threshold = ghcomp.Kangaroo2Component.ClampLength(line = inner_line, lowerlimit = threshold, upperlimit = link, strength = 1)
        goal_border_length = ghcomp.Kangaroo2Component.LengthLine(line = border_line, length = offset, strength = 0.2)
        #goal_border_length = ghcomp.Kangaroo2Component.ClampLength(line = border_line, lowerlimit = threshold, upperlimit = offset, strength = 2)
        
        #goal_1 = ghcomp.Entwine(goal_anchor, goal_zfix)
        #goal_2 = ghcomp.Entwine(goal_cpcin, goal_cpcout)
        #goal_3 = ghcomp.Entwine(goal_inner_length, goal_inner_threshold, goal_border_length)
        #goal_obj = ghcomp.Entwine(goal_1, goal_2, goal_3)
        
        # Make an empty datatree
        goal_obj = gh.DataTree[object]()
        
        # Add data to it (note that you assign your own path to the level you like)
        goal_obj.AddRange(goal_anchor, gh.Kernel.Data.GH_Path(0,0))
        goal_obj.AddRange(goal_zfix, gh.Kernel.Data.GH_Path(0,1))
        goal_obj.AddRange(goal_cpcin, gh.Kernel.Data.GH_Path(0,2))
        goal_obj.AddRange(goal_cpcout, gh.Kernel.Data.GH_Path(0,3))
        goal_obj.AddRange(goal_inner_length, gh.Kernel.Data.GH_Path(0,4))
        goal_obj.AddRange(goal_inner_threshold, gh.Kernel.Data.GH_Path(0,5))
        goal_obj.AddRange(goal_border_length, gh.Kernel.Data.GH_Path(0,6))
        
        subiter = 1000
        _, pts, _ = ghcomp.Kangaroo2Component.StepSolver(goal_obj, 0.01, True, 0.99, subiter, True)
        
        filter, _ = ghcomp.PointInCurve(pts, outer_border)
        filter, _ = ghcomp.Equality(filter, 2)
        pts, _ = ghcomp.Dispatch(pts, filter)
        
        pts += fix_pts
        
        
        return pts
    
    def construct_ring_mesh(self, outer_border, inner_border, pts):
        outer_srf = ghcomp.BoundarySurfaces(outer_border)
        outer_mesh = rg.Mesh.CreateFromBrep(outer_srf)
        print("*****get outer mesh*******")
        print(len(outer_mesh))
        outer_mesh = outer_mesh[0]
        
        inner_srf = ghcomp.BoundarySurfaces(inner_border)
        inner_mesh = rg.Mesh.CreateFromBrep(inner_srf)
        print("*****get inner mesh*******")
        print(len(inner_mesh))
        inner_mesh = inner_mesh[0]
        
        raw_mesh = ghcomp.DelaunayMesh(pts, ghcomp.XYPlane())
        raw_center, _ = ghcomp.FaceNormals(raw_mesh)
        _, _, _, z_axis = ghcomp.DeconstructPlane(ghcomp.XYPlane())
        _, outer_hit = ghcomp.MeshXRay(outer_mesh, raw_center, z_axis)
        _, inner_hit = ghcomp.MeshXRay(inner_mesh, raw_center, z_axis)
        inner_unhit = ghcomp.GateNot(inner_hit)
        cull_pattern = ghcomp.GateAnd(outer_hit, inner_unhit)
        
        cull_pattern = ghcomp.GateNot(cull_pattern)
        ring_mesh = ghcomp.CullFaces(raw_mesh, cull_pattern)
        
        return outer_mesh, inner_mesh, ring_mesh

    def generate_grid_array(self, top_border, bottom_border, horizontal, vertical, block_aligned, band_aligned):
        top_border, bottom_border, border = self.construct_border(top_border, bottom_border)
        box, _ = ghcomp.BoundingBox(border, ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)))
        center_pt, d_vec, _, _, _ = ghcomp.BoxProperties(box)
        diag_length = ghcomp.VectorLength(d_vec)
        
        centerx, centery, centerz = ghcomp.Deconstruct(center_pt)
        x,y,z = ghcomp.DeconstructVector(d_vec)
        
        left_up = ghcomp.ConstructPoint(centerx - x/2, centery + y/2, z)
        left_down = ghcomp.ConstructPoint(centerx - x/2, centery - y/2, z)
        right_up = ghcomp.ConstructPoint(centerx + x/2, centery + y/2, z)
        right_down = ghcomp.ConstructPoint(centerx + x/2, centery - y/2, z)
        
        diag_direc = ghcomp.Subtraction(right_up, left_down)
        diag_line = ghcomp.LineSDL(right_down, diag_direc, diag_length)
        _, diag_pt = ghcomp.EndPoints(diag_line)
        extend_line = ghcomp.Line(left_up, diag_pt)
        
        grid_num = int(math.ceil(ghcomp.Length(extend_line)), horizontal)
        white_start, _, _ = ghcomp.DivideCurve(extend_line, grid_num, False)
        
        grid_vec, _ = ghcomp.VectorXYZ(-1, -1, 0)
        if block_aligned == False:
            grid_vec, _ = ghcomp.VectorXYZ(-horizontal/2, -vertical, 0)
        else:
            grid_vec, _ = ghcomp.VectorXYZ(-horizontal, -vertical, 0)
            
        white_grid_array = ghcomp.LineSDL(white_start, grid_vec, diag_length)
        
        black_start = []
        if band_aligned == False:
            for i in range(len(white_start)-1):
                black_start.append(ghcomp.Division(ghcomp.Addition(white_start[i]+white_start[i+1]),2))
        black_grid_array = ghcomp.LineSDL(black_start, grid_vec, diag_length)
        
        grid_start, _, _ = ghcomp.CurveXCurve(white_grid_array, top_border)
        grid_end, _, _ = ghcomp.CurveXCurve(white_grid_array, bottom_border)
        white_grid_line = ghcomp.Line(grid_start, grid_end)
        white_grid_line = white_grid_line.flatten()
        
        return white_grid_line, white_grid_array, black_grid_array
        
    def array_white_fill(self, grid_crv, horizontal, vertical, aligned, fit_ends):
        #给定上下边界填充斜向阵列
        pts = []
        unit_length = 1
        
        top_pts = []
        bottom_pts = []
        limbo_pts = []
        
        if aligned == False:
            unit_length = math.sqrt(0.25 * horizontal*horizontal + vertical*vertical)
        else:
            unit_length = math.sqrt(horizontal*horizontal + vertical*vertical)
        
        for i in range(len(fit_ends)):
            cur_crv = fit_ends[i]
            start_pt, end_pt = ghcomp.EndPoints(cur_crv)
            x = start_pt.X
            y = start_pt.Y
            z = start_pt.Z
            x_domain = end_pt.X - x
            y_domain = end_pt.Y - y
            z_domain = end_pt.Z - z
            num = int(math.floor(ghcomp.Length(cur_crv)/unit_length)+1)
            cur_pts = []
            for k in range(num+1):
                cur_fac = k/num
                cur_x = x + cur_fac*x_domain
                cur_y = y + cur_fac*y_domain
                cur_z = z + cur_fac*z_domain
                cur_pt = ghcomp.ConstructPoint(cur_x, cur_y, cur_z)
                cur_pts.append(cur_pt)
            for k in range(1, num-1):
                pts.append(cur_pts[k])
            if num>1:
                top_pts.append(cur_pts[0])
            bottom_pts.append(cur_pts[-1])
            limbo_pts.append(cur_pts[-2])
        
        return pts, top_pts, bottom_pts, limbo_pts
        
        
    @staticmethod
    def load_block_xml(file_path, region):
        xmldoc = System.Xml.XmlDocument()
        xmldoc.Load(file_path)
        items = xmldoc.SelectNodes("setting/block/hole")
        rows = []
        for item in items:
            nid = int(item.GetAttributeNode('id').Value)
            row = HoleFrits(nid, region)
            dot_type = item.GetAttributeNode('type').Value
            row.dot_type = {'circle': FritType.CIRCLE_DOT, 'roundrect': FritType.ROUND_RECT}[dot_type]
            arrange_type = item.GetAttributeNode('arrange').Value
            row.arrange_type = {'heading': HoleArrangeType.HEADING, 'cross': HoleArrangeType.CROSS }[arrange_type]
            val = dict()

            for node in item.ChildNodes:
                val[node.Name] = float(node.InnerText)
            row.stepping = val['stepping']
            row.vspace = val['vspace']
            if 'fposition' in val.keys():
                row.first_line_position = val['fposition']
            if row.dot_type == FritType.CIRCLE_DOT:
                row.circle_config.r = val['r']
            elif row.dot_type == FritType.ROUND_RECT:
                row.round_rect_config.k = val['k']
                row.round_rect_config.r = val['r']
            rows.append(row)
        return rows



#原RowFrits 带状填充算法
class RowArrangeType:
    HEADING=0
    CROSS=1
    @staticmethod
    def get_row_arrange_type():
        return ['顶头', '交错']
#原RowFrits 带状填充算法
class RowFrits:
    def __init__(self, row_id, region):
        self.row_id = row_id
        self.dot_type = FritType.CIRCLE_DOT
        self.dot_config = CircleDotConfig()
        self.stepping = 0
        self.position = 0

        self.circle_config = CircleDotConfig()
        self.round_rect_config = RoundRectConfig()
        self.arc_config = ArcDotConfig()
        self.tri_arc_config = TriArcConfig()

        self.is_transit = False
        self.transit_radius = 0
        self.transit_position = 0
        
        self.arrange_type = RowArrangeType.HEADING
        self.dots = []
        self.region = region
     
    def fill_dots(self):
        del self.dots[:]
        print(self.row_id)
        if self.region.type == 'band' and self.region.curves[0]:
            if self.is_transit:
                self.fill_transit_band()
                print('fill transit band')
            else:
                self.fill_general_band()
                print('fill general band')
        elif self.region.type == 'block' and self.region.curves[0] and self.region.curves[1]:
            if self.row_id >= 0:
                if self.is_transit:
                    
                    self.fill_transit_band()
                    print('fill transit band')
                else:
                    self.fill_general_band()
                    print('fill general band')
            else:
                self.fill_bottom_band()

    def fill_general_band(self):
        refer_curve = self.region.curves[0] 
        if self.region.is_flip[0] == True:
            refer_curve, _ = ghcomp.FlipCurve(refer_curve)
        curve = ghcomp.OffsetCurve(refer_curve, plane = rs.WorldXYPlane(), distance=self.position, corners=1)
        
        # crv = ghcomp.OffsetCurve(curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
        crv = refer_curve
        crv_length = ghcomp.Length(crv)   
        pts_num = int(crv_length / self.stepping)#计算出当前stepp规则下点在线上分布的数量
        # offset curve
        pts = None
        t = None
        pts, _, t = ghcomp.DivideCurve(crv, pts_num, False)
        if self.arrange_type == RowArrangeType.CROSS:
            new_t = []
            for i in range(len(t) - 1):
                new_t.append((t[i] + t[i + 1]) / 2)
            t = new_t
        pts, vec, _ = ghcomp.EvaluateCurve(crv, t)
        pts, t, _ = ghcomp.CurveClosestPoint(pts, curve)
        self.dots = list()
        for i in range(len(pts)):
            theta = tgt_angle(vec[i])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(pts[i].X, pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(pts[i].X, pts[i].Y, self.round_rect_config, theta)
            elif self.dot_type == FritType.ARC_CIRCLE:
                dot = ArcDot(pts[i].X, pts[i].Y, self.arc_config, theta)
            elif self.dot_type == FritType.TRI_ARC:
                dot = TriArc(pts[i].X, pts[i].Y, self.tri_arc_config, theta)
            self.dots.append(dot)
    
    def shift_y_dots(self, shift_y):
        new_dots = []
        for dot in self.dots:
            dot2 = Dot(dot.centroid.X, dot.centroid.Y + shift_y, None, dot.theta)
            new_dots.append(dot2)
        return new_dots
    
    def shift_y_mid_dots(self, shift_y):
        new_dots = []
        for i in range(len(self.dots) - 1):
            dot = self.dots[i]
            dot1 = self.dots[i + 1]
            dot2 = Dot((dot.centroid.X + dot1.centroid.X) / 2.0, (dot.centroid.Y + dot1.centroid.Y) / 2.0 + shift_y, None, dot.theta)
            new_dots.append(dot2)
        return new_dots

    def fill_transit_band(self):
        refer_curve = self.region.curves[0]
        if self.region.is_flip[0] == True:
            refer_curve, _ = ghcomp.FlipCurve(refer_curve)
        
        inner_curve = self.region.curves[1]
        if self.region.is_flip[1] == True:
            inner_curve, _ = ghcomp.FlipCurve(inner_curve)

        curve = ghcomp.OffsetCurve(refer_curve, plane = rs.WorldXYPlane(), distance=self.position, corners=1)
        
        # crv = ghcomp.OffsetCurve(curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
        crv = refer_curve
        crv_length = ghcomp.Length(crv)   
        pts_num = int(crv_length / self.stepping)
        # offset curve
        pts = None
        t = None
        pts, _, t = ghcomp.DivideCurve(crv, pts_num, False)
        if self.arrange_type == RowArrangeType.CROSS:
            new_t = []
            for i in range(len(t) - 1):
                new_t.append((t[i] + t[i + 1]) / 2)
            t = new_t
        pts, vec, _ = ghcomp.EvaluateCurve(crv, t)
        inner_pts, _, dis = ghcomp.CurveClosestPoint(pts, inner_curve)
        max_dis = max(dis)
        min_dis = min(dis)
        new_pts, t, _ = ghcomp.CurveClosestPoint(pts, curve)
        self.dots = list()
        for i in range(len(pts)):
            theta = tgt_angle(vec[i])
            dot = None
            tp = dis[i]
            rp = max_dis
            if self.transit_position != 0:
                tp = (dis[i] - min_dis) / (max_dis - min_dis) * (self.position - self.transit_position) + self.transit_position
                # tr = 0
                # if self.dot_type == FritType.CIRCLE_DOT:
                #     tr = (dis[i] - min_dis) / (max_dis - min_dis) * (self.circle_config.r - self.transit_radius) + self.transit_radius
                # elif self.dot_type == FritType.ROUND_RECT:
                #     tr = (dis[i] - min_dis) / (max_dis - min_dis) * (self.round_rect_config.k - self.transit_radius) + self.transit_radius
                tp = tp
                rp = self.position
            else:
                tp = 1.0
                rp = 1.0
            x = (1 - tp / rp) * pts[i].X + (tp / rp) * new_pts[i].X
            y = (1 - tp / rp) * pts[i].Y + (tp / rp) * new_pts[i].Y
            if self.dot_type == FritType.CIRCLE_DOT:
                new_config = CircleDotConfig()
                new_config.r = (dis[i] - min_dis) / (max_dis - min_dis) * (self.circle_config.r - self.transit_radius) + self.transit_radius
                dot = CircleDot(x, y, new_config)
            elif self.dot_type == FritType.ROUND_RECT:
                k = (dis[i] - min_dis) / (max_dis - min_dis) * (self.round_rect_config.k - self.transit_radius) + self.transit_radius
                r = k / self.round_rect_config.k * self.round_rect_config.r # dis[i] / max_dis * self.round_rect_config.r
                new_config = RoundRectConfig()
                new_config.k = k
                new_config.r = r
                dot = RoundRectDot(x, y, new_config, theta)
            self.dots.append(dot)
    
    def fill_bottom_band(self):
        refer_curve = self.region.curves[2]
        if self.region.is_flip[2] == True:
            refer_curve, _ = ghcomp.FlipCurve(refer_curve)
        curve = ghcomp.OffsetCurve(refer_curve, plane = rs.WorldXYPlane(), distance=self.position, corners=1)
        
        # crv = ghcomp.OffsetCurve(curve, plane = ghcomp.XYPlane(), distance=self.position, corners=1)
        crv = refer_curve
        crv_length = ghcomp.Length(crv)   
        pts_num = int(crv_length / self.stepping)
        # offset curve
        pts = None
        t = None
        pts, _, t = ghcomp.DivideCurve(crv, pts_num, False)
        if self.arrange_type == RowArrangeType.CROSS:
            new_t = []
            for i in range(len(t) - 1):
                new_t.append((t[i] + t[i + 1]) / 2)
            t = new_t
        pts, vec, _ = ghcomp.EvaluateCurve(crv, t)
        pts, t, _ = ghcomp.CurveClosestPoint(pts, curve)
        self.dots = list()
        for i in range(len(pts)):
            theta = tgt_angle(vec[i])
            dot = None
            if self.dot_type == FritType.CIRCLE_DOT:
                dot = CircleDot(pts[i].X, pts[i].Y, self.circle_config)
            elif self.dot_type == FritType.ROUND_RECT:
                dot = RoundRectDot(pts[i].X, pts[i].Y, self.round_rect_config, theta)
            elif self.dot_type == FritType.ARC_CIRCLE:
                dot = ArcDot(pts[i].X, pts[i].Y, self.arc_config, theta)
            elif self.dot_type == FritType.TRI_ARC:
                dot = TriArc(pts[i].X, pts[i].Y, self.tri_arc_config, theta)
            self.dots.append(dot)

    def get_bottom_curve(self):
        refer_curve = None
        if self.row_id >= 0:
            refer_curve = self.region.curves[0]
            if self.region.is_flip[0] == True:
                refer_curve, _ = ghcomp.FlipCurve(refer_curve)
            
        else:
            refer_curve = self.region.curves[2]
            if self.region.is_flip[2] == True:
                refer_curve, _ = ghcomp.FlipCurve(refer_curve)
        dis = 0
        if self.dot_type == FritType.CIRCLE_DOT:
            dis = self.circle_config.bottom()
        elif self.dot_type == FritType.ROUND_RECT:
            dis = self.round_rect_config.bottom()
        elif self.dot_type == FritType.ARC_CIRCLE:
            dis = self.arc_config.bottom()
        elif self.dot_type == FritType.TRI_ARC:
            dis = self.tri_arc_config.bottom()
        curve = ghcomp.OffsetCurve(refer_curve, plane = rs.WorldXYPlane(), distance=self.position + dis, corners=1)
        return curve
        
    def get_top_curve(self):
        refer_curve = None
        if self.row_id >= 0:
            refer_curve = self.region.curves[0]
            if self.region.is_flip[0] == True:
                refer_curve, _ = ghcomp.FlipCurve(refer_curve)
            
        else:
            refer_curve = self.region.curves[2]
            if self.region.is_flip[2] == True:
                refer_curve, _ = ghcomp.FlipCurve(refer_curve)
        dis = 0
        if self.dot_type == FritType.CIRCLE_DOT:
            dis = self.circle_config.top()
        elif self.dot_type == FritType.ROUND_RECT:
            dis = self.round_rect_config.top()
        elif self.dot_type == FritType.ARC_CIRCLE:
            dis = self.arc_config.top()
        elif self.dot_type == FritType.TRI_ARC:
            dis = self.tri_arc_config.top()
        curve = ghcomp.OffsetCurve(refer_curve, plane = rs.WorldXYPlane(), distance=self.position - dis, corners=1)
        return curve
        

    @staticmethod
    def load_band_xml(file_path, region, band_type='general'):
        xmldoc = System.Xml.XmlDocument()
        xmldoc.Load(file_path)
        items = None
        if band_type == 'general':
            items = xmldoc.SelectNodes("setting/band/row")
        else:
            items = xmldoc.SelectNodes("setting/bottom/row")
        rows = []
        for item in items:
            nid = int(item.GetAttributeNode('id').Value)
            row = RowFrits(nid, region)
            dot_type = item.GetAttributeNode('type').Value
            row.dot_type = {'circle': FritType.CIRCLE_DOT, 'roundrect': FritType.ROUND_RECT, 'arcdot': FritType.ARC_CIRCLE, 'triarc': FritType.TRI_ARC}[dot_type]
            arrange_type = item.GetAttributeNode('arrange').Value
            row.arrange_type = {'heading': RowArrangeType.HEADING, 'cross': RowArrangeType.CROSS }[arrange_type]
            val = dict()
            for node in item.ChildNodes:
                val[node.Name] = float(node.InnerText)
            row.stepping = val['stepping']
            row.position = val['position']
            if row.dot_type == FritType.CIRCLE_DOT:
                row.circle_config.r = val['r']
            elif row.dot_type == FritType.ROUND_RECT:
                row.round_rect_config.k = val['k']
                row.round_rect_config.r = val['r']
            elif row.dot_type == FritType.ARC_CIRCLE:
                row.arc_config.lr = val['lr']
                row.arc_config.sr = val['sr']
                row.arc_config.angle = val['angle']
            elif row.dot_type == FritType.TRI_ARC:
                row.tri_arc_config.lr = val['lr']
                row.tri_arc_config.sr = val['sr']
                row.tri_arc_config.angle = val['angle']
            if 'transit' in val.keys():
                row.is_transit = True
                row.transit_radius = val['transit']
                if 'transitposition' in val.keys():
                    row.transit_position = val['transitposition']
            rows.append(row)
        return rows

    @staticmethod
    def load_block_xml(file_path, region):
        xmldoc = System.Xml.XmlDocument()
        xmldoc.Load(file_path)
        items = xmldoc.SelectNodes("setting/block/row")
        rows = []
        for item in items:
            nid = int(item.GetAttributeNode('id').Value)
            row = RowFrits(nid, region)
            dot_type = item.GetAttributeNode('type').Value
            row.dot_type = {'circle': FritType.CIRCLE_DOT, 'roundrect': FritType.ROUND_RECT, 'arcdot': FritType.ARC_CIRCLE, 'triarc': FritType.TRI_ARC}[dot_type]
            arrange_type = item.GetAttributeNode('arrange').Value
            row.arrange_type = {'heading': RowArrangeType.HEADING, 'cross': RowArrangeType.CROSS }[arrange_type]
            val = dict()

            for node in item.ChildNodes:
                val[node.Name] = float(node.InnerText)
            row.stepping = val['stepping']
            row.position = val['position']
            if row.dot_type == FritType.CIRCLE_DOT:
                row.circle_config.r = val['r']
            elif row.dot_type == FritType.ROUND_RECT:
                row.round_rect_config.k = val['k']
                row.round_rect_config.r = val['r']
            elif row.dot_type == FritType.ARC_CIRCLE:
                row.arc_config.lr = val['lr']
                row.arc_config.sr = val['sr']
                row.arc_config.angle = val['angle']
            elif row.dot_type == FritType.TRI_ARC:
                row.tri_arc_config.lr = val['lr']
                row.tri_arc_config.sr = val['sr']
                row.tri_arc_config.angle = val['angle']

            if 'transit' in val.keys():
                row.is_transit = True
                row.transit_radius = val['transit']
                if 'transitposition' in val.keys():
                    row.transit_position = val['transitposition']
            rows.append(row)
        return rows
        
    @staticmethod
    def load_dz_block_xml(file_path, region):
        xmldoc = System.Xml.XmlDocument()
        xmldoc.Load(file_path)
        items = xmldoc.SelectNodes("setting/block/row")
        rows = []
        for item in items:
            nid = int(item.GetAttributeNode('id').Value)
            row = RowFrits(nid, region)
            #dot_type = item.GetAttributeNode('type').Value
            #row.dot_type = {'circle': FritType.CIRCLE_DOT, 'roundrect': FritType.ROUND_RECT, 'arcdot': FritType.ARC_CIRCLE, 'triarc': FritType.TRI_ARC}[dot_type]
            #arrange_type = item.GetAttributeNode('arrange').Value
            #row.arrange_type = {'heading': RowArrangeType.HEADING, 'cross': RowArrangeType.CROSS }[arrange_type]
            val = dict()
            for node in item.ChildNodes:
                val[node.Name] = float(node.InnerText)
            row.stepping = val['horizontal']
            row.position = val['vertical']
            #if row.dot_type == FritType.CIRCLE_DOT:
            row.circle_config.cross_k1 = val['cross_k1']
            row.circle_config.cross_position3 = val['cross_position3']
            row.circle_config.cross_position2 = val['cross_position2']
            row.circle_config.cross_position1 = val['cross_position1']
            row.circle_config.cross_k2 = val['cross_k2']
            row.circle_config.cross_round_rect_r = val['cross_round_rect_r']
            row.circle_config.cross_r2 = val['cross_r2']
            row.circle_config.cross_r1 = val['cross_r1']
            row.circle_config.slope_r1 = val['slope_r1']
            row.circle_config.slope_r2 = val['slope_r2']
            row.circle_config.slope_r3 = val['slope_r3']
            row.circle_config.slope_r4 = val['slope_r4']
            rows.append(row)
        return rows
        
    @staticmethod
    def load_New_block_xml(file_path, region):
        xmldoc = System.Xml.XmlDocument()
        xmldoc.Load(file_path)
        items = xmldoc.SelectNodes("setting/block/row")
        rows = []
        for item in items:
            nid = int(item.GetAttributeNode('id').Value)
            row = RowFrits(nid, region)
            #dot_type = item.GetAttributeNode('type').Value
            #row.dot_type = {'circle': FritType.CIRCLE_DOT, 'roundrect': FritType.ROUND_RECT, 'arcdot': FritType.ARC_CIRCLE, 'triarc': FritType.TRI_ARC}[dot_type]
            #arrange_type = item.GetAttributeNode('arrange').Value
            #row.arrange_type = {'heading': RowArrangeType.HEADING, 'cross': RowArrangeType.CROSS }[arrange_type]
            val = dict()
            for node in item.ChildNodes:
                val[node.Name] = float(node.InnerText)
            row.stepping = val['horizontal']
            row.position = val['vertical']
            #if row.dot_type == FritType.CIRCLE_DOT:
            
            row.circle_config.New_cross_position3 = val['New_cross_position3']
            row.circle_config.New_cross_position2 = val['New_cross_position2']
            row.circle_config.New_cross_position1 = val['New_cross_position1']
            row.circle_config.New_cross_r3 = val['New_cross_r3']
            row.circle_config.New_cross_r2 = val['New_cross_r2']
            row.circle_config.New_cross_r1 = val['New_cross_r1']
            
            rows.append(row)
            print(len(rows))
        return rows

#原Separatrix
class Separatrix:
    def __init__(self, grid_direc, white_pts, white_k, white_sr, black_k, black_sr, r, white_base_crv, split_crv, black_base_crv):
        self.grid_direc = grid_direc
        self.white_pts = white_pts
        
        self.white_k = white_k
        self.white_sr = white_sr
        self.black_k = black_k
        self.black_sr = black_sr
        self.r = r
        self.lr = white_k-r-0.05
        
        self.white_base_crv = white_base_crv
        self.split_crv = split_crv
        self.black_base_crv = black_base_crv
        
        self.bound_crv = []
        self.rect_crv = []
        self.bug = []
    
    def separate_pts(self, white_pts):
        #data structure: 类似 dictionary
        #list[0]为当前类型的tag
        """ e.g. 
        [['slope', pts],
        ['transit', pts],
        ['cross', pts],
        ['transit', pts]]
        """
        
        pre_type = None
        cur_seq = []
        pts = []
        
        for i in range(len(white_pts)):
            cur_type = None
            cur_pt = white_pts[i]
            
            vec = ghcomp.VectorXYZ(0,0,0)
            if i != len(white_pts)-1:
                vec = ghcomp.Subtraction(white_pts[i+1], cur_pt)
            else:
                vec = ghcomp.Subtraction(cur_pt, white_pts[i-1])
                
            angle, _ = ghcomp.Angle(vec, ghcomp.UnitX(1))
            if ghcomp.Absolute(angle) > ghcomp.Pi(1/12):
                cur_type = 'slope'
            elif ghcomp.Absolute(angle) < ghcomp.Pi(1/48):
                cur_type = 'cross'
            else:
                cur_type = 'transit'
            
            if pre_type == cur_type:
                cur_seq.append(cur_pt)
                if i == len(white_pts)-1:
                    #if len(cur_seq) > 2:
                    pts.append(cur_seq)
            else:
                if pre_type != None:
                    #if len(cur_seq) > 2:
                    pts.append(cur_seq)
                cur_seq = []
                cur_seq.append(cur_type)
                cur_seq.append(cur_pt)
                pre_type = cur_type
        
        return pts

    def generate_rect(self, center_pts, k, r, n, pattern = None):
        sr = r
        lr = self.lr
        #圆角矩形的边方向为逆时针
        bound_crv = []
        rect_crv = []
        rot_center = []
        #TODO: modify line to nurbscurve
        
        k = k/2
        #ang, _ = ghcomp.Angle(ghcomp.UnitY(-1), n)
        
        for i in range(len(center_pts)):
            cur_rect = {}
            cur_pt = center_pts[i]
            x = cur_pt.X
            y = cur_pt.Y
            z = cur_pt.Z
            cur_n = n[i]
            #cur_ang = ang[i]
            #if n[i].X < 0:
            #    cur_ang = -cur_ang
            
            luarc_ct = ghcomp.ConstructPoint(x-k+r, y+k-r, 0)
            lu_angle = ghcomp.ConstructDomain(ghcomp.Pi(1/2), ghcomp.Pi(1))
            luarc, _ = ghcomp.Arc(ghcomp.XYPlane(luarc_ct), r, lu_angle)
            luarc = rg.NurbsCurve.CreateFromArc(luarc)
            luarc, _ = ghcomp.RotateDirection(luarc, cur_pt, ghcomp.UnitY(-1), cur_n)
            #luarc, _ = ghcomp.Rotate(luarc, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(luarc)
            cur_rect['lu'] = luarc
            
                
            up_l = ghcomp.ConstructPoint(x-k+r, y+k, 0)
            
            if pattern == 'white':
                r = lr
            up_r = ghcomp.ConstructPoint(x+k-r, y+k, 0)
            up_crv = ghcomp.Line(up_r, up_l)
            up_crv = rg.NurbsCurve.CreateFromLine(up_crv)
            up_crv, _ = ghcomp.RotateDirection(up_crv, cur_pt, ghcomp.UnitY(-1), cur_n)
            #up_crv, _ = ghcomp.Rotate(up_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(up_crv)
            cur_rect['up'] = up_crv
            
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(up_crv, luarc), True)
            
            ruarc_ct = ghcomp.ConstructPoint(x+k-r, y+k-r, 0)
            ru_angle = ghcomp.ConstructDomain(ghcomp.Pi(0), ghcomp.Pi(1/2))
            ruarc, _ = ghcomp.Arc(ghcomp.XYPlane(ruarc_ct), r, ru_angle)
            ruarc = rg.NurbsCurve.CreateFromArc(ruarc)
            ruarc, _ = ghcomp.RotateDirection(ruarc, cur_pt, ghcomp.UnitY(-1), cur_n)
            #ruarc, _ = ghcomp.Rotate(ruarc, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(ruarc)
            cur_rect['ru'] = ruarc
            
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(ruarc, rec_crv), True)
            
            right_u = ghcomp.ConstructPoint(x+k, y+k-r, 0)
            r = sr
            right_b = ghcomp.ConstructPoint(x+k, y-k+r, 0)
            right_crv = ghcomp.Line(right_b, right_u)
            right_crv = rg.NurbsCurve.CreateFromLine(right_crv)
            right_crv, _ = ghcomp.RotateDirection(right_crv, cur_pt, ghcomp.UnitY(-1), cur_n)
            #right_crv, _ = ghcomp.Rotate(right_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(right_crv)
            cur_rect['right'] = right_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(right_crv, rec_crv), True)
            
            rbarc_ct = ghcomp.ConstructPoint(x+k-r, y-k+r, 0)
            rb_angle = ghcomp.ConstructDomain(ghcomp.Pi(-1/2), ghcomp.Pi(0))
            rbarc, _ = ghcomp.Arc(ghcomp.XYPlane(rbarc_ct), r, rb_angle)
            rbarc = rg.NurbsCurve.CreateFromArc(rbarc)
            rbarc, _ = ghcomp.RotateDirection(rbarc, cur_pt, ghcomp.UnitY(-1), cur_n)
            #rbarc, _ = ghcomp.Rotate(rbarc, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(rbarc)
            cur_rect['rb'] = rbarc
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(rbarc, rec_crv), True)
            
            bottom_r = ghcomp.ConstructPoint(x+k-r, y-k, 0)
            if pattern == 'black':
                r = lr
            bottom_l = ghcomp.ConstructPoint(x-k+r, y-k, 0)
            bottom_crv = ghcomp.Line(bottom_l, bottom_r)
            bottom_crv = rg.NurbsCurve.CreateFromLine(bottom_crv)
            bottom_crv, _ = ghcomp.RotateDirection(bottom_crv, cur_pt, ghcomp.UnitY(-1), cur_n)
            #bottom_crv, _ = ghcomp.Rotate(bottom_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(bottom_crv)
            cur_rect['bottom'] = bottom_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(bottom_crv, rec_crv), True)
            
            lbarc_ct = ghcomp.ConstructPoint(x-k+r, y-k+r, 0)
            lb_angle = ghcomp.ConstructDomain(ghcomp.Pi(-1), ghcomp.Pi(-1/2))
            lbarc, _ = ghcomp.Arc(ghcomp.XYPlane(lbarc_ct), r, lb_angle)
            lbarc = rg.NurbsCurve.CreateFromArc(lbarc)
            lbarc, _ = ghcomp.RotateDirection(lbarc, cur_pt, ghcomp.UnitY(-1), cur_n)
            #lbarc, _ = ghcomp.Rotate(lbarc, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(lbarc)
            cur_rect['lb'] = lbarc
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(lbarc, rec_crv), True)
            
            left_b = ghcomp.ConstructPoint(x-k, y-k+r, 0)
            r = sr
            left_u = ghcomp.ConstructPoint(x-k, y+k-r, 0)
            left_crv = ghcomp.Line(left_u, left_b)
            left_crv = rg.NurbsCurve.CreateFromLine(left_crv)
            left_crv, _ = ghcomp.RotateDirection(left_crv, cur_pt, ghcomp.UnitY(-1), cur_n)
            #left_crv, _ = ghcomp.Rotate(left_crv, cur_ang, ghcomp.XYPlane(cur_pt))
            bound_crv.append(left_crv)
            cur_rect['left'] = left_crv
            rec_crv = ghcomp.JoinCurves(ghcomp.Merge(left_crv, rec_crv), True)
            
            seampt, _ = ghcomp.EndPoints(bottom_crv)
            _, seamt, _ = ghcomp.CurveClosestPoint(seampt, rec_crv)
            rec_crv = ghcomp.Seam(rec_crv, seamt)
            cur_rect['rect'] = rec_crv
            
            rect_crv.append(cur_rect)
        
        return bound_crv, rect_crv
    
    def _generate_slope_bound(self, white_rect, black_rect):
        bound_crv = []
        #TODO 需要区分左右边界，通过斜率进行选择
        for i in range(len(white_rect)):
            cur_white = white_rect[i]
            white_left = cur_white['left']
            if i==0:
                tail = []
                white_lb = cur_white['lb']
                lb_pt, _= ghcomp.EndPoints(white_lb)
                lb_plane, _ = ghcomp.RotateDirection(ghcomp.YZPlane(lb_pt), lb_pt, ghcomp.UnitY(-1), get_vec(white_left))
                white_lb, _ = ghcomp.Mirror(white_lb, lb_plane)
                tail.append(white_lb)
                tail.append(white_left)
                tail.append(cur_white['lu'])
                tail_crv = ghcomp.JoinCurves(tail, True)
                tail_crv = crv_direc(tail_crv)
                split_crv = self.split_crv
                _, t1, _ = ghcomp.CurveXCurve(tail_crv, split_crv)
                if t1:
                    _, cur_domain = ghcomp.CurveDomain(tail_crv)
                    _, t2 = ghcomp.DeconstructDomain(cur_domain)
                    bound_crv.append(ghcomp.SubCurve(tail_crv, ghcomp.ConstructDomain(t1, t2)))
                else:
                    bound_crv += tail
                
            white_up = cur_white['up']
            bound_crv.append(white_up)
            
            bound_crv.append(cur_white['ru'])
            
            white_right = cur_white['right']
            bound_crv.append(white_right)
            white_bottom = cur_white['bottom']
            
            if i!=0:
                pre_black = black_rect[i-1]
                pre_black_bottom = pre_black['bottom']
                pre_black_right = pre_black['right']
                white_left_flip, _ = ghcomp.FlipCurve(white_left)
                right_left = ghcomp.TweenCurve(pre_black_right, white_left_flip, 0.5)
                bound_crv.append(right_left)
                
                _, pre_link_black = ghcomp.EndPoints(pre_black_bottom)
                pre_link_mid, _ = ghcomp.EndPoints(right_left)
                linkv = ghcomp.Merge(pre_link_black, pre_link_mid)
                linkt = ghcomp.Merge(get_vec(pre_black_bottom), get_vec(right_left))
                pre_link1, _, _ = ghcomp.TangentCurve(linkv, linkt, 0.5, 3)
                bound_crv.append(pre_link1)
                
                _, pre_link_mid= ghcomp.EndPoints(right_left)
                _, pre_link_white = ghcomp.EndPoints(white_up)
                linkv = ghcomp.Merge(pre_link_mid, pre_link_white)
                linkt = ghcomp.Merge(get_vec(right_left), ghcomp.Multiplication(-1, get_vec(white_up)))
                pre_link2, _, _ = ghcomp.TangentCurve(linkv, linkt, 0.5, 3)
                bound_crv.append(pre_link2)
                
            if i!=len(white_rect)-1:
                cur_black = black_rect[i]
                black_up = cur_black['up']
                black_left = cur_black['left']
                white_bottom_flip, _ = ghcomp.FlipCurve(white_bottom)
                up_bottom = ghcomp.TweenCurve(black_up, white_bottom_flip, 0.5)
                bound_crv.append(up_bottom)
                
                bound_crv.append(black_left)
                bound_crv.append(cur_black['lb'])
                bound_crv.append(cur_black['bottom'])
               
                suc_link_white, _ = ghcomp.EndPoints(white_right)
                suc_link_mid, _ = ghcomp.EndPoints(up_bottom)
                linkv = ghcomp.Merge(suc_link_white, suc_link_mid)
                linkt = ghcomp.Merge(ghcomp.Multiplication(-1, get_vec(white_right)), get_vec(up_bottom))
                suc_link1, _, _ = ghcomp.TangentCurve(linkv, linkt, 0.5, 3)
                bound_crv.append(suc_link1)
                
                _, suc_link_mid= ghcomp.EndPoints(up_bottom)
                suc_link_black, _ = ghcomp.EndPoints(black_left)
                linkv = ghcomp.Merge(suc_link_mid, suc_link_black)
                linkt = ghcomp.Merge(get_vec(up_bottom), get_vec(black_left))
                suc_link2, _, _ = ghcomp.TangentCurve(linkv, linkt, 0.5, 3)
                bound_crv.append(suc_link2)
            
            else:
                tail = []
                tail.append(cur_white['rb'])
                white_bottom = cur_white['bottom']
                _, bottom_pt = ghcomp.EndPoints(white_bottom)
                white_k = self.white_k
                bottom_line = ghcomp.LineSDL(bottom_pt, ghcomp.Multiplication(-1, get_vec(white_bottom)), white_k)
                bottom_line = rg.NurbsCurve.CreateFromLine(bottom_line)
                tail.append(bottom_line)
                
                tail_crv = ghcomp.JoinCurves(tail, False)
                tail_crv = crv_direc(tail_crv)
                
                split_crv = self.split_crv
                _, t1, _ = ghcomp.CurveXCurve(tail_crv, split_crv)
                if t1:
                    _, cur_domain = ghcomp.CurveDomain(tail_crv)
                    _, t2 = ghcomp.DeconstructDomain(cur_domain)
                    bottom_crv = ghcomp.SubCurve(tail_crv, ghcomp.ConstructDomain(t1, t2))
                    bound_crv.append(bottom_crv)
                else:
                    bound_crv += tail
        bound_crv = ghcomp.JoinCurves(bound_crv, False)
        bound_crv = crv_direc(bound_crv)
        return bound_crv
    
    def generate_slope_bound(self, white_pts, grid_direc):
        black_pts = []
        black_n = []
        black_x = []
        black_y = []
        
        for i in range(len(white_pts)-1):
            cur_pt = white_pts[i]
            next_pt = white_pts[i+1]
            mid_pt = ghcomp.Division(ghcomp.Addition(cur_pt, next_pt),2)
            deltax = next_pt.X - cur_pt.X
            deltay = next_pt.Y- cur_pt.Y
            deltaz = next_pt.Z - cur_pt.Z
            tgt, _ = ghcomp.VectorXYZ(deltax, deltay, deltaz)
            normal, _ = ghcomp.Rotate(tgt, ghcomp.Pi(-1/2), ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)))
            delta = ghcomp.Line(cur_pt, next_pt)
            length = ghcomp.Length(delta)
            
            #direc = ghcomp.LineSDL(mid_pt, normal, length)
            
            grid_line = ghcomp.LineSDL(cur_pt, ghcomp.Multiplication(grid_direc, -1), length)
            _, end_pt = ghcomp.EndPoints(grid_line)
            diag_vec, y_length = ghcomp.Vector2Pt(end_pt, next_pt, False)
            black_n.append(diag_vec)
            
            diag_line = ghcomp.LineSDL(end_pt, tgt, length)
            _, diag_pt = ghcomp.EndPoints(diag_line)
            _, x_length = ghcomp.Vector2Pt(cur_pt, diag_pt, False)
            
            black_x.append(ghcomp.ConstructDomain(ghcomp.Division(x_length,2), ghcomp.Division(x_length,-2)))
            black_y.append(ghcomp.ConstructDomain(ghcomp.Division(y_length,2), ghcomp.Division(y_length,-2)))
            
            grid_diag = ghcomp.LineSDL(mid_pt, grid_direc, 0.55*length)
            _, black_pt = ghcomp.EndPoints(grid_diag)
            black_pts.append(black_pt)
            
        white_n = []
        for i in range(len(black_n) +1):
            if i==len(black_n):
                white_n.append(black_n[i-1])
                break
            cur_n = black_n[i]
            if i==0:
                white_n.append(cur_n)
            else:
                pre_n = black_n[i-1]
                white_n.append(ghcomp.Division(ghcomp.Addition(cur_n, pre_n), 2))
        
        white_k = self.white_k
        r = self.r
        black_k = self.black_k
        
        white_crv, white_rect = self.generate_rect(white_pts, white_k, r, white_n, 'white')
        black_crv, black_rect = self.generate_rect(black_pts, black_k, r, black_n, 'black')
        bound_crv = []
        bound_crv = self._generate_slope_bound(white_rect, black_rect)
        
        return bound_crv, white_n[-1], black_n[-1]
    
    def generate_horizontal_bound(self, white_base_crv, black_base_crv, white_pts):
        white_k = self.white_k
        white_sr = self.white_sr
        black_k = self.black_k
        black_sr = self.black_sr
        
        white_n = get_n_along_crv(white_pts, white_base_crv)
        black_pts, _, _ = ghcomp.CurveClosestPoint(white_pts, black_base_crv)
        black_n = get_n_along_crv(black_pts, black_base_crv)
        
        _, white_rect = self.generate_rect(white_pts, white_k, white_sr, white_n)
        _, black_rect = self.generate_rect(black_pts, black_k, black_sr, black_n)
        
        bound_crv = []
        for i in range(len(white_rect)):
            cur_white = white_rect[i]
            white_lb = cur_white['lb']
            bound_crv.append(white_lb)
            bound_crv.append(cur_white['left'])
            bound_crv.append(cur_white['lu'])
            bound_crv.append(cur_white['up'])
            bound_crv.append(cur_white['ru'])
            bound_crv.append(cur_white['right'])
            white_rb = cur_white['rb']
            bound_crv.append(white_rb)
            
            white_bottom = cur_white['bottom']
            
            if i!=0:
                pre_white = white_rect[i-1]
                pre_white_rb = pre_white['rb']
                pre_link1, _ = ghcomp.EndPoints(pre_white_rb)
                _, pre_link2 = ghcomp.EndPoints(white_lb)
                
                pre_white_bottom = pre_white['bottom']
                linkv = ghcomp.Merge(pre_link1, pre_link2)
                linkt = ghcomp.Merge(get_vec(pre_white_bottom), get_vec(white_bottom))
                pre_link, _, _ = ghcomp.TangentCurve(linkv, linkt, 0.5, 3)
                bound_crv.append(pre_link)
        bound_crv = ghcomp.JoinCurves(bound_crv, False)
        bound_crv = crv_direc(bound_crv)
        black_crv = []
        for i in range(len(black_rect)):
            black_crv.append(black_rect[i]['rect'])
            
        return bound_crv, black_crv, white_n[-1]

    def generate_black_pts(self, white_pts, white_base_crv, black_base_crv, grid_direc):
        #crv, _, _ = ghcomp.NurbsCurve(white_pts, 3, False)
        pts, _, _ = ghcomp.CurveClosestPoint(white_pts, white_base_crv)
        base_pts = []
        
        for i in range(len(pts)-1):
            cur_pt = ghcomp.Division(ghcomp.Addition(pts[i], pts[i+1]),2)
            base_pts.append(cur_pt)
        
        ray = ghcomp.LineSDL(base_pts, grid_direc, 10)
        
        black_pts, _, _ = ghcomp.CurveXCurve(ray, black_base_crv)
        return black_pts
    
    def _generate_transit_bound(self, white_rect, split_crv):
        bound_crv = []
        
        for i in range(len(white_rect)-1):
            if i==0 and i!=len(white_rect)-2:
                pass
                """
                cur_rect = white_rect[i]
                bottom_crv = cur_rect['bottom']
                rbarc = cur_rect['rb']
                #right_crv = cur_rect['right']
                
                cur_rect = ghcomp.JoinCurves(ghcomp.Merge(bottom_crv, rbarc), True)
                #cur_rect = ghcomp.JoinCurves(ghcomp.Merge(cur_rect, right_crv), True)
                _, cur_domain = ghcomp.CurveDomain(cur_rect)
                _, te = ghcomp.DeconstructDomain(cur_domain)
                
                suc_rect = white_rect[i+1]['rect']
                
                _, ts, tr = ghcomp.CurveXCurve(split_crv, cur_rect)
                rect_domain = ghcomp.ConstructDomain(tr, te)
                #ghcomp.SubCurve()
                rect_crv = ghcomp.SubCurve(cur_rect, rect_domain)
                bound_crv.append(rect_crv)
                
                _, suc_ts, _ = ghcomp.CurveXCurve(split_crv, suc_rect)
                split_domain = ghcomp.ConstructDomain(ts, suc_ts[0])
                #ghcomp.SubCurve()
                sub_split = ghcomp.SubCurve(split_crv, split_domain)
                bound_crv.append(sub_split)
                """
                
            else:
                cur_rect = white_rect[i]['rect']
                suc_rect = white_rect[i+1]['rect']
                
                _, ts, tr = ghcomp.CurveXCurve(split_crv, cur_rect)
                try:
                    rect_domain = ghcomp.ConstructDomain(tr[0], tr[-1])
                    #ghcomp.SubCurve()
                    rect_crv = ghcomp.SubCurve(cur_rect, rect_domain)
                    bound_crv.append(rect_crv)
                except:
                    pass
                
                if i != len(white_rect)-2:
                    _, suc_ts, _ = ghcomp.CurveXCurve(split_crv, suc_rect)
                    split_domain = ghcomp.ConstructDomain(ts[-1], suc_ts[0])
                    #ghcomp.SubCurve()
                    sub_split = ghcomp.SubCurve(split_crv, split_domain)
                    bound_crv.append(sub_split)
        if len(bound_crv)!=0:
            bound_crv = ghcomp.JoinCurves(bound_crv, False)
        else:
            return None
        bound_crv = crv_direc(bound_crv)
        return bound_crv
        
    def generate_transit_bound(self, white_base_crv, split_crv, white_pts, black_pts, white_pre_n, begin = False):
        white_k = self.white_k
        white_sr = self.white_sr
        black_k = self.black_k
        r = self.r
        
        num = len(white_pts)
        crv_n = get_n_along_crv(white_pts, white_base_crv)
        white_n = []
        if begin == True:
            white_n = crv_n
        else:
            white_n = generate_n(white_pre_n, crv_n[-1], num)
        
        white_crv = []
        _, white_rect = self.generate_rect(white_pts, white_k*1.1, (r+white_sr)/2, white_n)
        for i in range(len(white_rect)):
            white_crv.append(white_rect[i]['rect'])
        black_crv = []
        _, black_rect = self.generate_rect(black_pts, black_k, r, white_n[0:-1])
        for i in range(len(black_rect)):
            black_crv.append(black_rect[i]['rect'])
        
        bound_crv = self._generate_transit_bound(white_rect, split_crv)
        
        return white_crv, black_crv, bound_crv
        
    def join_bound(self, bound_crv, split_crv):
        joined_crv = []
        for i in range(len(bound_crv)-1):
            cur_bound = bound_crv[i]
            next_bound = bound_crv[i+1]
            
            _, cur_end = ghcomp.EndPoints(cur_bound)
            next_start, _ = ghcomp.EndPoints(next_bound)
            
            _, t1, _ = ghcomp.CurveClosestPoint(cur_end, split_crv)
            _, tgt1, _ = ghcomp.EvaluateCurve(split_crv, t1)
            _, t2, _ = ghcomp.CurveClosestPoint(next_start, split_crv)
            _, tgt2, _ = ghcomp.EvaluateCurve(split_crv, t2)
            
            v = ghcomp.Merge(cur_end, next_start)
            direc = ghcomp.Merge(tgt1, tgt2)
            crv, _, _ = ghcomp.TangentCurve(v, direc, 0.5, 3)
            joined_crv.append(cur_bound)
            joined_crv.append(crv)
        joined_crv.append(bound_crv[-1])
        #joined_crv = ghcomp.JoinCurves(joined_crv, True)
        return joined_crv
            
    def generate_bound(self):
        #接口处永远是最后一个rect与split_crv相交
        
        pts = self.separate_pts(self.white_pts)
        white_last_n  = None
        bound_crv = []
        rect_crv = []
        
        for i in range(len(pts)):
            cur_seq = pts[i]
            type = cur_seq[0]
            white_pts = cur_seq[1:len(cur_seq)]
            white_pts = construct_safe_pts_list(white_pts)
            print(type)
            print(len(white_pts))
            
            if type == 'slope':
                slope_bound_crv, white_last_n, _ = self.generate_slope_bound(white_pts, self.grid_direc)
                bound_crv.append(slope_bound_crv)
            
            if type == "cross":
                cross_bound_crv, black_rect, white_last_n = self.generate_horizontal_bound(self.white_base_crv, self.black_base_crv, white_pts)
                bound_crv.append(cross_bound_crv)
                rect_crv += black_rect
            
            if type == 'transit':
                if i == 0:
                    next_seq = pts[i+1]
                    next_white_pt = next_seq[1]
                    white_pts.append(next_white_pt)
                    black_pts = self.generate_black_pts(white_pts, self.white_base_crv, self.black_base_crv, self.grid_direc)
                    black_pts = construct_safe_pts_list(black_pts)
                    _, black_rect, transit_bound_crv = self.generate_transit_bound(self.white_base_crv, self.split_crv, white_pts, black_pts, white_last_n, True)
                    if transit_bound_crv!=None:
                        bound_crv.append(transit_bound_crv)
                    rect_crv += black_rect
                else:
                    pre_seq = pts[i-1]
                    pre_white_pt = pre_seq[-1]
                    white_pts.insert(0, pre_white_pt)
                    
                    if i!=len(pts)-1:
                        next_seq = pts[i+1]
                        next_white_pt = next_seq[1]
                        white_pts.append(next_white_pt)
                    
                    black_pts = self.generate_black_pts(white_pts, self.white_base_crv, self.black_base_crv, self.grid_direc)
                    black_pts = construct_safe_pts_list(black_pts)
                    _, black_rect, transit_bound_crv = self.generate_transit_bound(self.white_base_crv, self.split_crv, white_pts, black_pts, white_last_n, False)
                    if bound_crv!=None:
                        bound_crv.append(transit_bound_crv)
                    rect_crv += black_rect
        bound_crv = self.join_bound(bound_crv, self.split_crv)
        self.bound_crv = bound_crv
        self.rect_crv = rect_crv

#原frits——init 定义花点类型
class FritType:
    CIRCLE_DOT=0
    ROUND_RECT=1
    ARC_CIRCLE=2
    TRI_ARC=3
    @staticmethod
    def get_frit_type_strings():
        return ['圆点', '圆角矩形', '弧形', '三段弧形']

#原DOT   
class Dot:
    def __init__(self, x, y, config, theta):
        self.centroid = rc.Geometry.Point3d(x, y, 0)
        self.theta = theta
        self.config = config
        self.curve = None

    def draw(self):
        print("Dot: this function should not be executed!")

#原ArcDot 定义弧形花点参数信息
class ArcDotConfig:
    def __init__(self):
        self.lr = 0#0.2
        self.sr = 0#0.9
        self.angle = 0#180
    
    def top(self):
        return 0
    
    def bottom(self):
        return self.lr
#原ArcDot 绘制弧形花点
class ArcDot(Dot):
    def __init__(self, x, y, config, theta):
        Dot.__init__(self, x, y, config, theta)
    
    def draw(self, display, display_color):
        # draw the large circle
        angle_start = (180 - self.config.angle)  / 2#0
        angle_end = angle_start + self.config.angle#180
        center_angle = ghcomp.ConstructDomain(angle_start * 1.0 / 180  * ghcomp.Pi(), angle_end * 1.0 / 180  * ghcomp.Pi())#ok
        center_arc, _ = ghcomp.Arc(self.centroid, self.config.sr, center_angle)
        center_start_point = center_arc.StartPoint#(0.9,0)
        center_end_point = center_arc.EndPoint#(-0.9,0)
        # left center
        left_x = (self.config.lr / self.config.sr) * (center_end_point.X - self.centroid.X) + center_end_point.X#-1.1
        left_y = (self.config.lr / self.config.sr) * (center_end_point.Y - self.centroid.Y) + center_end_point.Y#0
        # right center
        right_x = (self.config.lr / self.config.sr) * (center_start_point.X - self.centroid.X) + center_start_point.X#1.1
        right_y = (self.config.lr / self.config.sr) * (center_start_point.Y - self.centroid.Y) + center_start_point.Y#0

        left_angle = ghcomp.ConstructDomain(ghcomp.Pi(1.5), ghcomp.Pi(1.5) + self.config.angle * 1.0 / 2 / 180.0 * ghcomp.Pi())#1.5p-2p
        right_angle = ghcomp.ConstructDomain(ghcomp.Pi(1.5) - self.config.angle * 1.0 / 2 / 180.0 * ghcomp.Pi(), ghcomp.Pi(1.5))#p-1.5p
        left_arc, _ = ghcomp.Arc(rg.Point3d(left_x, left_y, 0), self.config.lr, left_angle)
        right_arc, _ = ghcomp.Arc(rg.Point3d(right_x, right_y, 0), self.config.lr, right_angle)

        crv = ghcomp.JoinCurves([left_arc, center_arc, right_arc])
        
        crv, _ = ghcomp.Pufferfish.CloseCurve(crv, 0, 0.5, 0)
        rotate_angle = ghcomp.Addition(self.theta, ghcomp.Pi())
        crv, _ = ghcomp.Rotate(crv, rotate_angle, self.centroid)
        display.AddCurve(crv, display_color, 1)

    def bake(self):
        # draw the large circle
        angle_start = (180 - self.config.angle)  / 2
        angle_end = angle_start + self.config.angle
        center_angle = ghcomp.ConstructDomain(angle_start * 1.0 / 180  * ghcomp.Pi(), angle_end * 1.0 / 180  * ghcomp.Pi())
        center_arc, _ = ghcomp.Arc(self.centroid, self.config.sr, center_angle)
        center_start_point = center_arc.StartPoint
        center_end_point = center_arc.EndPoint
        # left center
        left_x = (self.config.lr / self.config.sr) * (center_end_point.X - self.centroid.X) + center_end_point.X
        left_y = (self.config.lr / self.config.sr) * (center_end_point.Y - self.centroid.Y) + center_end_point.Y
        # right center
        right_x = (self.config.lr / self.config.sr) * (center_start_point.X - self.centroid.X) + center_start_point.X
        right_y = (self.config.lr / self.config.sr) * (center_start_point.Y - self.centroid.Y) + center_start_point.Y

        left_angle = ghcomp.ConstructDomain(ghcomp.Pi(1.5), ghcomp.Pi(1.5) + self.config.angle * 1.0 / 2 / 180.0 * ghcomp.Pi())
        right_angle = ghcomp.ConstructDomain(ghcomp.Pi(1.5) - self.config.angle * 1.0 / 2 / 180.0 * ghcomp.Pi(), ghcomp.Pi(1.5))
        left_arc, _ = ghcomp.Arc(rg.Point3d(left_x, left_y, 0), self.config.lr, left_angle)
        right_arc, _ = ghcomp.Arc(rg.Point3d(right_x, right_y, 0), self.config.lr, right_angle)

        crv = ghcomp.JoinCurves([left_arc, center_arc, right_arc])
        
        crv, _ = ghcomp.Pufferfish.CloseCurve(crv, 0, 0.5, 0)
        rotate_angle = ghcomp.Addition(self.theta, ghcomp.Pi())
        crv, _ = ghcomp.Rotate(crv, rotate_angle, self.centroid)
        # pts, _, _ = ghcomp.ControlPoints(crv)
        rc = scriptcontext.doc.Objects.AddCurve(crv)
        return rc



#原CircleDot 定义圆形花点参数信息（self.r）
class CircleDotConfig:
    def __init__(self):
        self.cross_k1 = 0
        self.cross_position3 = 0
        self.cross_position2 = 0
        self.cross_position1 = 0
        self.cross_k2 = 0
        self.cross_round_rect_r = 0
        self.cross_r2 = 0
        self.cross_r1 = 0
        self.slope_r1 = 0
        self.slope_r2 = 0
        self.slope_r3 = 0
        self.slope_r4 = 0
        
        self.New_cross_position3 = 0
        self.New_cross_position2 = 0
        self.New_cross_position1 = 0
        self.New_cross_r3 = 0
        self.New_cross_r1 = 0
        self.New_cross_r2 = 0
        
        self.r = 0
    
    def top(self):
        return self.r
    
    def bottom(self):
        return self.r
#原CircleDot 绘制圆形花点
class CircleDot(Dot):
    def __init__(self, x, y, config, theta=0):
        Dot.__init__(self, x, y, config, theta)
    
    def draw(self, display, display_color):
        self.curve = rc.Geometry.Circle(self.centroid, self.config.r)
        display.AddCircle(self.curve, display_color, 1)
    
    def bake(self):
        if self.curve:
            rc = scriptcontext.doc.Objects.AddCircle(self.curve)
            return rc
        return None

#原RoundRectDot 定义圆角矩形花点参数信息
class RoundRectConfig:
    def __init__(self):
        self.k = 0
        self.r = 0
    
    def top(self):
        return self.k / 2
    
    def bottom(self):
        return self.k / 2
#原RoundRectDot 绘制圆角矩形花点
class RoundRectDot(Dot):
    def __init__(self, x, y, config, theta):
        Dot.__init__(self, x, y, config, theta)#初始化点坐标的x、y值以及圆角矩形的K、r值以及偏移角
    
    def draw(self, display, display_color):
        x = self.centroid.X#圆角矩形中心坐标X值
        y = self.centroid.Y#圆角矩形中心坐标Y值
        x_domain = ghcomp.ConstructDomain(ghcomp.Subtraction(x, self.config.k / 2), ghcomp.Addition(x, self.config.k / 2))
        y_domain = ghcomp.ConstructDomain(ghcomp.Subtraction(y, self.config.k / 2), ghcomp.Addition(y, self.config.k / 2))
        rec, _ = ghcomp.Rectangle(rs.WorldXYPlane(), x_domain, y_domain, self.config.r)
        rec, _ = ghcomp.Rotate(rec, self.theta, self.centroid)
        self.curve = rec
        display.AddCurve(rec, display_color, 1)
    
    def bake(self):
        if self.curve:
            rc = scriptcontext.doc.Objects.AddCurve(self.curve)
            return rc
        return None


#TriArc 定义三段弧形花点参数信息
class TriArcConfig:
    def __init__(self):
        self.lr = 0
        self.sr = 0
        self.angle = 0
    
    def top(self):
        return 0
    
    def bottom(self):
        return self.lr
#TriArc 绘制三段弧形花点
class TriArc(Dot):
    def __init__(self, x, y, config, theta):
        Dot.__init__(self, x, y, config, theta)
    
    def draw(self, display, display_color):
        # draw the large circle
        angle1 = 34.256
        angle2 = 72.872
        angle_start = (180 - angle1)  / 2
        angle_end = angle_start + angle1
        center_angle = ghcomp.ConstructDomain(angle_start * 1.0 / 180  * ghcomp.Pi(), angle_end * 1.0 / 180  * ghcomp.Pi())
        center_arc, _ = ghcomp.Arc(self.centroid, self.config.lr, center_angle)
        center_start_point = center_arc.StartPoint
        center_end_point = center_arc.EndPoint
        # left center
        left_x = -(self.config.sr / self.config.lr) * (center_end_point.X - self.centroid.X) + center_end_point.X
        left_y = -(self.config.sr / self.config.lr) * (center_end_point.Y - self.centroid.Y) + center_end_point.Y
        # right center
        right_x = -(self.config.sr / self.config.lr) * (center_start_point.X - self.centroid.X) + center_start_point.X
        right_y = -(self.config.sr / self.config.lr) * (center_start_point.Y - self.centroid.Y) + center_start_point.Y
       
      
        left_angle = ghcomp.ConstructDomain( angle_end * 1.0 / 180  * ghcomp.Pi(), ghcomp.Pi())
        right_angle = ghcomp.ConstructDomain(0, angle_start * 1.0 / 180  * ghcomp.Pi())
        left_arc, _ = ghcomp.Arc(rg.Point3d(left_x, left_y, 0), self.config.sr, left_angle)
        right_arc, _ = ghcomp.Arc(rg.Point3d(right_x, right_y, 0), self.config.sr, right_angle)
        right_start_point = right_arc.StartPoint
        left_end_point = left_arc.EndPoint
        # left center
        left_x2 = (0.7 / self.config.sr) * (left_end_point.X - left_x) + left_end_point.X
        left_y2 = (0.7 / self.config.sr) * (left_end_point.Y - left_y) + left_end_point.Y
        # right center
        right_x2 = (0.7 / self.config.sr) * (right_start_point.X - right_x) + right_start_point.X
        right_y2 = (0.7 / self.config.sr) * (right_start_point.Y - right_y) + right_start_point.Y

        left_angle2 = ghcomp.ConstructDomain(ghcomp.Pi(1.5), ghcomp.Pi(2))
        right_angle2 = ghcomp.ConstructDomain(ghcomp.Pi(), ghcomp.Pi(1.5))
        left_arc2, _ = ghcomp.Arc(rg.Point3d(left_x2, left_y2, 0), 0.7, left_angle2)
        right_arc2, _ = ghcomp.Arc(rg.Point3d(right_x2, right_y2, 0), 0.7, right_angle2)


        crv = ghcomp.JoinCurves([left_arc2, left_arc, center_arc, right_arc, right_arc2])
        
        crv, _ = ghcomp.Pufferfish.CloseCurve(crv, 0, 0.5, 0)
        rotate_angle = ghcomp.Addition(self.theta, ghcomp.Pi())
        crv, _ = ghcomp.Rotate(crv, rotate_angle, self.centroid)
        display.AddCurve(crv, display_color, 1)

    def bake(self):
        # draw the large circle
        angle1 = 34.256
        angle2 = 72.872
        angle_start = (180 - angle1)  / 2
        angle_end = angle_start + angle1
        center_angle = ghcomp.ConstructDomain(angle_start * 1.0 / 180  * ghcomp.Pi(), angle_end * 1.0 / 180  * ghcomp.Pi())
        center_arc, _ = ghcomp.Arc(self.centroid, self.config.lr, center_angle)
        center_start_point = center_arc.StartPoint
        center_end_point = center_arc.EndPoint
        # left center
        left_x = -(self.config.sr / self.config.lr) * (center_end_point.X - self.centroid.X) + center_end_point.X
        left_y = -(self.config.sr / self.config.lr) * (center_end_point.Y - self.centroid.Y) + center_end_point.Y
        # right center
        right_x = -(self.config.sr / self.config.lr) * (center_start_point.X - self.centroid.X) + center_start_point.X
        right_y = -(self.config.sr / self.config.lr) * (center_start_point.Y - self.centroid.Y) + center_start_point.Y
        left_angle = ghcomp.ConstructDomain( angle_end * 1.0 / 180  * ghcomp.Pi(), ghcomp.Pi())
        right_angle = ghcomp.ConstructDomain(0, angle_start * 1.0 / 180  * ghcomp.Pi())
        left_arc, _ = ghcomp.Arc(rg.Point3d(left_x, left_y, 0), self.config.sr, left_angle)
        right_arc, _ = ghcomp.Arc(rg.Point3d(right_x, right_y, 0), self.config.sr, right_angle)
        right_start_point = right_arc.StartPoint
        left_end_point = left_arc.EndPoint
        # left center
        left_x2 = (0.7 / self.config.sr) * (left_end_point.X - left_x) + left_end_point.X
        left_y2 = (0.7 / self.config.sr) * (left_end_point.Y - left_y) + left_end_point.Y
        # right center
        right_x2 = (0.7 / self.config.sr) * (right_start_point.X - right_x) + right_start_point.X
        right_y2 = (0.7 / self.config.sr) * (right_start_point.Y - right_y) + right_start_point.Y

        left_angle2 = ghcomp.ConstructDomain(ghcomp.Pi(1.5), ghcomp.Pi(2))
        right_angle2 = ghcomp.ConstructDomain(ghcomp.Pi(), ghcomp.Pi(1.5))
        left_arc2, _ = ghcomp.Arc(rg.Point3d(left_x2, left_y2, 0), 0.7, left_angle2)
        right_arc2, _ = ghcomp.Arc(rg.Point3d(right_x2, right_y2, 0), 0.7, right_angle2)


        crv = ghcomp.JoinCurves([left_arc2, left_arc, center_arc, right_arc, right_arc2])
        
        crv, _ = ghcomp.Pufferfish.CloseCurve(crv, 0, 0.5, 0)
        rotate_angle = ghcomp.Addition(self.theta, ghcomp.Pi())
        crv, _ = ghcomp.Rotate(crv, rotate_angle, self.centroid)
        # pts, _, _ = ghcomp.ControlPoints(crv)
        rc = scriptcontext.doc.Objects.AddCurve(crv)
        return rc

#原utils 
def safe_list_access(arr, i):
    arr_len = len(arr)
    if i < 0:
        return 0
    elif i < arr_len:
        return arr[i]
    else:
        return arr[arr_len - 1]

def tgt_angle(tgt):
    angle, _ = ghcomp.Angle(tgt, ghcomp.UnitX(1))
    _, y, _ = ghcomp.Deconstruct(tgt)
    larger_pattern, _ = ghcomp.LargerThan(y,0)
    factor = ghcomp.Subtraction(ghcomp.Multiplication(larger_pattern,2),1)
    rotate_angle = ghcomp.Multiplication(angle, factor)
    
    return rotate_angle

def remove_verbose(list):
    count = len(list)
    loop = []
    i = 0
    flag = False
    while i < count:
        for j in range(count-i-1):
            if list[i] == list[i+j+1]:
                print("**hit**")
                print(i)
                print(i+j+1)
                for k in range(j+1):
                    loop.append(list[i])
                    list.pop(i)
                i -= 1
                count -= j+1
                flag = True
                break
        if flag == True:
            break
        i += 1
   
    return list, loop, flag

def get_vec(line):
    start, end = ghcomp.EndPoints(line)
    deltax = end.X-start.X
    deltay = end.Y-start.Y
    deltaz = end.Z-start.Z
    vec, _ = ghcomp.VectorXYZ(deltax, deltay, deltaz)
    return vec

def generate_n(pre_n, last_n, num):
    start_x, start_y, start_z = ghcomp.DeconstructVector(pre_n)
    end_x, end_y, end_z = ghcomp.DeconstructVector(last_n)
    deltax = end_x - start_x
    deltay = end_y - start_y
    deltaz = end_z - start_z
    n = []
    for i in range(num):
        x = start_x + deltax*(i+1)/num
        y = start_y + deltay*(i+1)/num
        z = start_z + deltaz*(i+1)/num
        cur_n, _ = ghcomp.VectorXYZ(x, y, z)
        n.append(cur_n)
    return n

def get_n_along_crv(pts, crv):
    n=[]
    
    _, t, _ = ghcomp.CurveClosestPoint(pts, crv)
    _, tgt, _ = ghcomp.EvaluateCurve(crv, t)
    
    angle, _ = ghcomp.Angle(tgt, ghcomp.UnitX(1))
    _, y, _ = ghcomp.Deconstruct(tgt)
    larger_pattern, _ = ghcomp.LargerThan(y,0)
    factor = ghcomp.Subtraction(ghcomp.Multiplication(larger_pattern,2),1)
    rotate_angle = ghcomp.Multiplication(angle, factor)
    
    n, _ = ghcomp.Rotate(ghcomp.UnitY(-1), rotate_angle, ghcomp.XYPlane(ghcomp.ConstructPoint(0,0,0)))
    
    return n
    
def crv_direc(crv):
    start,end = ghcomp.EndPoints(crv)
    startx, starty, _ = ghcomp.Deconstruct(start)
    endx, endy, _ = ghcomp.Deconstruct(end)
    if startx>endx:
        crv, _ = ghcomp.FlipCurve(crv)
    return crv
    
def construct_safe_pts_list(pts):
    #[x,y,z]to[pt]
    if len(pts)==3:
        try:
            if pts[2]==0:
                new_pts = []
                pt = ghcomp.ConstructPoint(pts[0], pts[1], pts[2])
                new_pts.append(pt)
                return new_pts
        except:
            return pts
    return pts

def get_color(id):
    colors = [Color.AntiqueWhite, Color.Aqua, Color.BlueViolet, Color.Chartreuse, Color.Coral, Color.DarkTurquoise,  Color.DeepPink, Color.Gold, Color.LawnGreen, Color.Turquoise]
    return colors[id % len(colors)]

#原HoleConfigPanel 孔状区域参数定义界面
class HoleConfigPanel(forms.GroupBox):
    def __init__(self, parent, hole_config):
        self.parent = parent
        self.model = hole_config
        self.Text = '第{}排'.format(hole_config.hole_id)
        self.setup_view()
        self.display = rc.Display.CustomDisplay(True)
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)

    def setup_view(self):
        self.RemoveAll()
        self.basic_setting_label = forms.Label(Text='基础设置:', Font = Font('Microsoft YaHei', 12.))
        self.dot_type_label = forms.Label(Text = '花点类型：')
        self.dot_type_combo = forms.ComboBox()
        # self.dot_type_combo.Padding = drawing.Padding(20, 0, 0, 0)
        self.dot_type_combo.DataStore = FritType.get_frit_type_strings()
        self.dot_type_combo.SelectedIndex = self.model.dot_type
        self.dot_type_combo.SelectedIndexChanged += self.change_dot_type 
        # self.dot_type_combo.ReadOnly = True
        # for circle dot
        self.circle_dot_radius_label = forms.Label(Text='圆点半径：')
        self.circle_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.r))
        self.circle_dot_radius.Size = drawing.Size(60, -1)
        self.circle_dot_radius.TextChanged += self.circle_dot_radius_changed
        
        self.round_rect_edge_label = forms.Label(Text='圆角矩形边长：')
        self.round_rect_edge = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.k))
        self.round_rect_edge.Size = drawing.Size(60, -1)
        self.round_rect_edge.TextChanged += self.round_rect_edge_changed

        self.round_rect_radius_label = forms.Label(Text='圆角矩形半径：')
        self.round_rect_radius = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.r))
        self.round_rect_radius.Size = drawing.Size(60, -1)
        self.round_rect_radius.TextChanged += self.round_rect_radius_changed

        self.stepping_label = forms.Label(Text='水平间距：')
        self.stepping_input = forms.TextBox(Text='{0}'.format(self.model.stepping))
        self.stepping_input.Size = drawing.Size(60, -1)
        self.stepping_input.TextChanged += self.stepping_input_changed

        self.position_label = forms.Label(Text='垂直间距：')
        self.position_input = forms.TextBox(Text='{0}'.format(self.model.vspace))
        self.position_input.Size = drawing.Size(60, -1)
        self.position_input.TextChanged += self.position_input_changed

        self.arrange_setting_label = forms.Label(Text='排布方式:', Font = Font('Microsoft YaHei', 12.))
        
        self.arrage_type_label = forms.Label(Text='类型：')
        self.arrage_type_combo = forms.ComboBox()
        self.arrage_type_combo.DataStore = HoleArrangeType.get_hole_arrange_type()  
        self.arrage_type_combo.SelectedIndex = self.model.arrange_type
        self.arrage_type_combo.SelectedIndexChanged += self.change_row_arrange_type

        self.config_panel = forms.Panel()
        self.update_btn = forms.Button(Text='填充花点')
        self.update_btn.Size = drawing.Size(100, 30)
        self.update_btn.Click += self.fill_row_frits

        self.layout = forms.DynamicLayout()
        self.layout.DefaultSpacing = drawing.Size(10, 10)
       
        # default is circle dot
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.basic_setting_label, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        if self.model.dot_type == FritType.CIRCLE_DOT:
            self.layout.AddRow(self.dot_type_label, self.dot_type_combo, self.circle_dot_radius_label, self.circle_dot_radius, self.stepping_label,
                self.stepping_input, self.position_label, self.position_input, None)
            
        elif self.model.dot_type == FritType.ROUND_RECT:
            self.layout.AddRow(self.dot_type_label, self.dot_type_combo, self.round_rect_edge_label, self.round_rect_edge, self.round_rect_radius_label,
                self.round_rect_radius, self.stepping_label, self.stepping_input, self.position_label, self.position_input, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.arrange_setting_label, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.arrage_type_label, self.arrage_type_combo, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.update_btn, None)
        self.layout.EndVertical()
        self.Content = self.layout
    
    def change_dot_type(self, sender, e):
        if self.dot_type_combo.SelectedIndex == 0:
            self.model.dot_type = FritType.CIRCLE_DOT
        elif self.dot_type_combo.SelectedIndex == 1:
            self.model.dot_type = FritType.ROUND_RECT
        self.setup_view()

    def change_row_arrange_type(self, sender, e):
        self.model.arrange_type = self.arrage_type_combo.SelectedIndex

    def change_row_choice(self, sender, e):
        pass
    
    def circle_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.r = float(self.circle_dot_radius.Text)
        except:
            pass
    
    def round_rect_edge_changed(self, sender, e):
        try:
            self.model.round_rect_config.k = float(self.round_rect_edge.Text)
        except:
            pass
    
    def round_rect_radius_changed(self, sender, e):
        try:
            self.model.round_rect_config.r = float(self.round_rect_radius.Text)
        except:
            pass
    
    def stepping_input_changed(self, sender, e):
        try:
            self.model.stepping = float(self.stepping_input.Text)
        except:
            pass
    
    def position_input_changed(self, sender, e):
        try:
            self.model.vspace = float(self.position_input.Text)
        except:
            pass

    def fill_row_frits(self, sender, e):
        self.clear_dots()
        self.model.fill_dots()
        # self.display.AddCurve(self.model.border_curve)
        for d in self.model.dots:
            d.draw(self.display, self.display_color)
    
    def clear_dots(self):
        self.display.Clear()
    
    def bake(self):
        layer_name = 'page_{0}_hole_{1}'.format(self.parent.page_id, self.model.hole_id)
        rs.AddLayer(layer_name, get_color(self.model.hole_id), parent='fuyao_frits')
        for d in self.model.dots:
            obj = d.bake()
            rs.ObjectLayer(obj, layer_name)

#原RowConfigPanel 带状区域参数定义界面
class RowConfigPanel(forms.GroupBox):
    def __init__(self, parent, row_config):
        self.parent = parent
        self.model = row_config
        self.Text = '第{}排'.format(row_config.row_id)
        self.setup_view()
        self.display = rc.Display.CustomDisplay(True)
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)

    def setup_view(self):
        self.RemoveAll()
        self.basic_setting_label = forms.Label(Text='基础设置:', Font = Font('Microsoft YaHei', 12.))
        self.dot_type_label = forms.Label(Text = '花点类型：')
        self.dot_type_combo = forms.ComboBox()
        # self.dot_type_combo.Padding = drawing.Padding(20, 0, 0, 0)
        self.dot_type_combo.DataStore = FritType.get_frit_type_strings()
        self.dot_type_combo.SelectedIndex = self.model.dot_type
        self.dot_type_combo.SelectedIndexChanged += self.change_dot_type 
        # self.dot_type_combo.ReadOnly = True
        # for circle dot
        self.circle_dot_radius_label = forms.Label(Text='圆点半径：')
        self.circle_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.r))
        self.circle_dot_radius.Size = drawing.Size(60, -1)
        self.circle_dot_radius.TextChanged += self.circle_dot_radius_changed

        self.arc_dot_large_radius_label = forms.Label(Text='大弧半径：')
        self.arc_dot_large_radius = forms.TextBox(Text='{0}'.format(self.model.arc_config.lr))
        self.arc_dot_large_radius.Size = drawing.Size(60, -1)
        self.arc_dot_large_radius.TextChanged += self.arc_dot_large_radius_changed

        self.arc_dot_small_radius_label = forms.Label(Text='小弧半径：')
        self.arc_dot_small_radius = forms.TextBox(Text='{0}'.format(self.model.arc_config.sr))
        self.arc_dot_small_radius.Size = drawing.Size(60, -1)
        self.arc_dot_small_radius.TextChanged += self.arc_dot_small_radius_changed

        self.arc_dot_angle_label = forms.Label(Text='弧度：')
        self.arc_dot_angle = forms.TextBox(Text='{0}'.format(self.model.arc_config.angle))
        self.arc_dot_angle.Size = drawing.Size(60, -1)
        self.arc_dot_angle.TextChanged += self.arc_dot_angle_changed
        
        self.tri_arc_dot_large_radius_label = forms.Label(Text='大弧半径：')
        self.tri_arc_dot_large_radius = forms.TextBox(Text='{0}'.format(self.model.tri_arc_config.lr))
        self.tri_arc_dot_large_radius.Size = drawing.Size(60, -1)
        self.tri_arc_dot_large_radius.TextChanged += self.tri_arc_dot_large_radius_changed

        self.tri_arc_dot_small_radius_label = forms.Label(Text='小弧半径：')
        self.tri_arc_dot_small_radius = forms.TextBox(Text='{0}'.format(self.model.tri_arc_config.sr))
        self.tri_arc_dot_small_radius.Size = drawing.Size(60, -1)
        self.tri_arc_dot_small_radius.TextChanged += self.tri_arc_dot_small_radius_changed

        self.tri_arc_dot_angle_label = forms.Label(Text='弧度：')
        self.tri_arc_dot_angle = forms.TextBox(Text='{0}'.format(self.model.tri_arc_config.angle))
        self.tri_arc_dot_angle.Size = drawing.Size(60, -1)
        self.tri_arc_dot_angle.TextChanged += self.tri_arc_dot_angle_changed

        
        self.round_rect_edge_label = forms.Label(Text='圆角矩形边长：')
        self.round_rect_edge = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.k))
        self.round_rect_edge.Size = drawing.Size(60, -1)
        self.round_rect_edge.TextChanged += self.round_rect_edge_changed

        self.round_rect_radius_label = forms.Label(Text='圆角矩形半径：')
        self.round_rect_radius = forms.TextBox(Text='{0}'.format(self.model.round_rect_config.r))
        self.round_rect_radius.Size = drawing.Size(60, -1)
        self.round_rect_radius.TextChanged += self.round_rect_radius_changed

        self.stepping_label = forms.Label(Text='水平间距：')
        self.stepping_input = forms.TextBox(Text='{0}'.format(self.model.stepping))
        self.stepping_input.Size = drawing.Size(60, -1)
        self.stepping_input.TextChanged += self.stepping_input_changed

        self.position_label = forms.Label(Text='相对参考线距离：')
        self.position_input = forms.TextBox(Text='{0}'.format(self.model.position))
        self.position_input.Size = drawing.Size(60, -1)
        self.position_input.TextChanged += self.position_input_changed

        self.arrange_setting_label = forms.Label(Text='排布方式:', Font = Font('Microsoft YaHei', 12.))
        
        self.arrage_type_label = forms.Label(Text='类型：')
        self.arrage_type_combo = forms.ComboBox()
        self.arrage_type_combo.DataStore = RowArrangeType.get_row_arrange_type()  
        self.arrage_type_combo.SelectedIndex = self.model.arrange_type
        self.arrage_type_combo.SelectedIndexChanged += self.change_row_arrange_type

        self.transit_check = forms.CheckBox(Text='是否过渡半径')
        self.transit_check.Checked = self.model.is_transit
        self.transit_check.CheckedChanged += self.transit_check_changed
        self.transit_label = forms.Label(Text='过渡初始半径：')
        self.transit_input = forms.TextBox(Text='{0}'.format(self.model.transit_radius))
        self.transit_input.Size = drawing.Size(60, -1)
        self.transit_input.TextChanged += self.transit_input_changed

        self.transit_label2 = forms.Label(Text='过渡初始位置：')
        self.transit_position_input = forms.TextBox(Text='{0}'.format(self.model.transit_position))
        self.transit_position_input.Size = drawing.Size(60, -1)
        self.transit_position_input.TextChanged += self.transit_position_input_changed

        self.config_panel = forms.Panel()
        self.update_btn = forms.Button(Text='填充花点')
        self.update_btn.Size = drawing.Size(100, 30)
        self.update_btn.Click += self.fill_row_frits
        
        self.undo_panel = forms.Panel()
        self.undo_btn = forms.Button(Text='清除花点')
        self.undo_btn.Size = drawing.Size(100, 30)
        self.undo_btn.Click += self.undo_fill_row_frits

        self.layout = forms.DynamicLayout()
        self.layout.DefaultSpacing = drawing.Size(10, 10)
       
        # default is circle dot
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.basic_setting_label, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        if self.model.dot_type == FritType.CIRCLE_DOT:
            self.layout.AddRow(self.dot_type_label, self.dot_type_combo, self.circle_dot_radius_label, self.circle_dot_radius, self.stepping_label,
                self.stepping_input, self.position_label, self.position_input, None)
            
        elif self.model.dot_type == FritType.ROUND_RECT:
            self.layout.AddRow(self.dot_type_label, self.dot_type_combo, self.round_rect_edge_label, self.round_rect_edge, self.round_rect_radius_label,
                self.round_rect_radius, self.stepping_label, self.stepping_input, self.position_label, self.position_input, None)
        elif self.model.dot_type == FritType.ARC_CIRCLE:
            self.layout.AddRow(self.dot_type_label, self.dot_type_combo, self.arc_dot_large_radius_label, self.arc_dot_large_radius,
                self.arc_dot_small_radius_label, self.arc_dot_small_radius, self.arc_dot_angle_label, self.arc_dot_angle)
        elif self.model.dot_type == FritType.TRI_ARC:
            self.layout.AddRow(self.dot_type_label, self.dot_type_combo, self.tri_arc_dot_large_radius_label, self.tri_arc_dot_large_radius,
                self.tri_arc_dot_small_radius_label, self.tri_arc_dot_small_radius, self.tri_arc_dot_angle_label, self.tri_arc_dot_angle)

        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.arrange_setting_label, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.arrage_type_label, self.arrage_type_combo, self.transit_check, self.transit_label, self.transit_input, self.transit_label2, self.transit_position_input, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.update_btn,self.undo_btn, None)
        self.layout.EndVertical()
        self.Content = self.layout
    
    def change_dot_type(self, sender, e):
        if self.dot_type_combo.SelectedIndex == 0:
            self.model.dot_type = FritType.CIRCLE_DOT
        elif self.dot_type_combo.SelectedIndex == 1:
            self.model.dot_type = FritType.ROUND_RECT
        elif self.dot_type_combo.SelectedIndex == 2:
            self.model.dot_type = FritType.ARC_CIRCLE
        elif self.dot_type_combo.SelectedIndex == 3:
            self.model.dot_type = FritType.TRI_ARC
        self.setup_view()

    def change_row_arrange_type(self, sender, e):
        self.model.arrange_type = self.arrage_type_combo.SelectedIndex

    def change_row_choice(self, sender, e):
        pass
    
    def circle_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.r = float(self.circle_dot_radius.Text)
        except:
            pass
    
    def arc_dot_large_radius_changed(self, sender, e):
        try:
            self.model.arc_config.lr = float(self.arc_dot_large_radius.Text)
        except:
            pass
    
    def arc_dot_small_radius_changed(self, sender, e):
        try:
            self.model.arc_config.sr = float(self.arc_dot_small_radius.Text)
        except:
            pass
    
    def arc_dot_angle_changed(self, sender, e):
        try:
            self.model.arc_config.angle = float(self.arc_dot_angle.Text)
        except:
            pass
    
    def tri_arc_dot_large_radius_changed(self, sender, e):
        try:
            self.model.tri_arc_config.lr = float(self.tri_arc_dot_large_radius.Text)
        except:
            pass
    
    def tri_arc_dot_small_radius_changed(self, sender, e):
        try:
            self.model.tri_arc_config.sr = float(self.tri_arc_dot_small_radius.Text)
        except:
            pass
    
    def tri_arc_dot_angle_changed(self, sender, e):
        try:
            self.model.tri_arc_config.angle = float(self.tri_arc_dot_angle.Text)
        except:
            pass
    
    def round_rect_edge_changed(self, sender, e):
        try:
            self.model.round_rect_config.k = float(self.round_rect_edge.Text)
        except:
            pass
    
    def round_rect_radius_changed(self, sender, e):
        try:
            self.model.round_rect_config.r = float(self.round_rect_radius.Text)
        except:
            pass
    
    def stepping_input_changed(self, sender, e):
        try:
            self.model.stepping = float(self.stepping_input.Text)
        except:
            pass
    
    def position_input_changed(self, sender, e):
        try:
            self.model.position = float(self.position_input.Text)
        except:
            pass
    
    def transit_check_changed(self, sender, e):
        self.model.is_transit = self.transit_check.Checked
    
    def transit_input_changed(self, sender, e):
        try:
            self.model.transit_radius = float(self.transit_input.Text)
        except:
            pass
    
    def transit_position_input_changed(self, sender, e):
        try:
            self.model.transit_position = float(self.transit_position_input.Text)
        except:
            pass

    def fill_row_frits(self, sender, e):
        self.clear_dots()
        self.model.fill_dots()
        for d in self.model.dots:
            d.draw(self.display, self.display_color)
    
    def undo_fill_row_frits(self, sender, e):
        self.clear_dots()
        del self.model.dots[:]
    
    def clear_dots(self):
        self.display.Clear()
        
    
    def bake(self):
        layer_name = 'page_{0}_row_{1}'.format(self.parent.page_id, self.model.row_id)
        rs.AddLayer(layer_name,get_color(self.model.row_id), parent='fuyao_frits')
        for d in self.model.dots:
            obj = d.bake()
            rs.ObjectLayer(obj, layer_name)
    
#大众ConfigPanel   大众孔状区域参数定义界面
class DZ_ConfigPanel(forms.GroupBox):
    def __init__(self, parent, row_config):
        self.parent = parent
        self.model = row_config
        self.Text = '第{}排'.format(row_config.row_id)
        self.setup_view()
        self.display = rc.Display.CustomDisplay(True)
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)

    def setup_view(self):
        self.RemoveAll()
        self.basic_setting_label = forms.Label(Text='基础设置:', Font = Font('Microsoft YaHei', 12.))
        self.circle1_dot_radius_label = forms.Label(Text='矩形边长1：')
        self.circle1_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.cross_k1))
        self.circle1_dot_radius.Size = drawing.Size(60, -1)
        self.circle1_dot_radius.TextChanged += self.circle1_dot_radius_changed
        
        self.circle2_dot_radius_label = forms.Label(Text='3排相对参考线距离：')
        self.circle2_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.cross_position3))
        self.circle2_dot_radius.Size = drawing.Size(60, -1)
        self.circle2_dot_radius.TextChanged += self.circle2_dot_radius_changed
        
        self.circle3_dot_radius_label = forms.Label(Text='2排相对参考线距离：')
        self.circle3_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.cross_position2))
        self.circle3_dot_radius.Size = drawing.Size(60, -1)
        self.circle3_dot_radius.TextChanged += self.circle3_dot_radius_changed
        
        self.circle4_dot_radius_label = forms.Label(Text='1排相对参考线距离：')
        self.circle4_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.cross_position1))
        self.circle4_dot_radius.Size = drawing.Size(60, -1)
        self.circle4_dot_radius.TextChanged += self.circle4_dot_radius_changed
        
        self.circle5_dot_radius_label = forms.Label(Text='矩形边长2：')
        self.circle5_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.cross_k2))
        self.circle5_dot_radius.Size = drawing.Size(60, -1)
        self.circle5_dot_radius.TextChanged += self.circle5_dot_radius_changed
        
        self.circle6_dot_radius_label = forms.Label(Text='矩形圆角半径：')
        self.circle6_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.cross_round_rect_r))
        self.circle6_dot_radius.Size = drawing.Size(60, -1)
        self.circle6_dot_radius.TextChanged += self.circle6_dot_radius_changed
        
        self.circle7_dot_radius_label = forms.Label(Text='2排直径：')
        self.circle7_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.cross_r2))
        self.circle7_dot_radius.Size = drawing.Size(60, -1)
        self.circle7_dot_radius.TextChanged += self.circle7_dot_radius_changed
        
        self.circle8_dot_radius_label = forms.Label(Text='1排直径：')
        self.circle8_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.cross_r1))
        self.circle8_dot_radius.Size = drawing.Size(60, -1)
        self.circle8_dot_radius.TextChanged += self.circle8_dot_radius_changed
        
        self.circle9_dot_radius_label = forms.Label(Text='圆点直径1：')
        self.circle9_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.slope_r1))
        self.circle9_dot_radius.Size = drawing.Size(60, -1)
        self.circle9_dot_radius.TextChanged += self.circle9_dot_radius_changed
        
        self.circle10_dot_radius_label = forms.Label(Text='圆点直径2：')
        self.circle10_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.slope_r2))
        self.circle10_dot_radius.Size = drawing.Size(60, -1)
        self.circle10_dot_radius.TextChanged += self.circle10_dot_radius_changed
        
        self.circle11_dot_radius_label = forms.Label(Text='圆点直径3：')
        self.circle11_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.slope_r3))
        self.circle11_dot_radius.Size = drawing.Size(60, -1)
        self.circle11_dot_radius.TextChanged += self.circle11_dot_radius_changed
        
        self.circle12_dot_radius_label = forms.Label(Text='圆点直径4：')
        self.circle12_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.slope_r4))
        self.circle12_dot_radius.Size = drawing.Size(60, -1)
        self.circle12_dot_radius.TextChanged += self.circle12_dot_radius_changed
        
        
        self.stepping_label = forms.Label(Text='花点水平间距：')
        self.stepping_input = forms.TextBox(Text='{0}'.format(self.model.stepping))
        self.stepping_input.Size = drawing.Size(60, -1)
        self.stepping_input.TextChanged += self.stepping_input_changed
        
        self.position_label = forms.Label(Text='花点垂直间距：')
        self.position_input = forms.TextBox(Text='{0}'.format(self.model.position))
        self.position_input.Size = drawing.Size(60, -1)
        self.position_input.TextChanged += self.position_input_changed
        
        self.layout = forms.DynamicLayout()
        self.layout.DefaultSpacing = drawing.Size(10, 10)
       
        # default is circle dot
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.basic_setting_label, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        ##self.layout.AddRow(self.circle1_dot_radius_label,self.circle1_dot_radius,self.circle5_dot_radius_label,self.circle5_dot_radius,self.circle2_dot_radius_label,self.circle2_dot_radius, self.circle3_dot_radius_label,self.circle3_dot_radius,self.circle4_dot_radius_label,self.circle4_dot_radius,self.circle6_dot_radius_label,self.circle6_dot_radius,self.circle9_dot_radius_label,self.circle9_dot_radius,self.circle10_dot_radius_label,self.circle10_dot_radius,self.circle11_dot_radius_label,self.circle11_dot_radius,self.circle12_dot_radius_label,self.circle12_dot_radius,self.stepping_label,self.stepping_input,self.position_label,self.position_input None)
        self.layout.AddRow(self.circle1_dot_radius_label,self.circle1_dot_radius,self.circle5_dot_radius_label,self.circle5_dot_radius,None)
        self.layout.AddRow(self.circle2_dot_radius_label,self.circle2_dot_radius, self.circle3_dot_radius_label,self.circle3_dot_radius,self.circle4_dot_radius_label,self.circle4_dot_radius,None)
        self.layout.AddRow(self.circle6_dot_radius_label,self.circle6_dot_radius,self.circle7_dot_radius_label,self.circle7_dot_radius,self.circle8_dot_radius_label,self.circle8_dot_radius,None)
        self.layout.AddRow(self.circle9_dot_radius_label,self.circle9_dot_radius,self.circle10_dot_radius_label,self.circle10_dot_radius,self.circle11_dot_radius_label,self.circle11_dot_radius,self.circle12_dot_radius_label,self.circle12_dot_radius,None)
        self.layout.AddRow(self.stepping_label,self.stepping_input,self.position_label,self.position_input,None)
        self.layout.EndVertical()
        self.Content = self.layout
        
        
    def circle1_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.cross_k1 = float(self.circle1_dot_radius.Text)
        except:
            pass
    def circle2_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.cross_position3 = float(self.circle2_dot_radius.Text)
        except:
            pass
    def circle3_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.cross_position2 = float(self.circle3_dot_radius.Text)
        except:
            pass
    def circle4_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.cross_position1 = float(self.circle4_dot_radius.Text)
        except:
            pass
    def circle5_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.cross_k2 = float(self.circle5_dot_radius.Text)
        except:
            pass
    def circle6_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.cross_round_rect_r = float(self.circle6_dot_radius.Text)
        except:
            pass
    def circle7_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.cross_r2 = float(self.circle7_dot_radius.Text)
        except:
            pass
    def circle8_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.cross_r1 = float(self.circle8_dot_radius.Text)
        except:
            pass
    def circle9_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.slope_r1 = float(self.circle9_dot_radius.Text)
        except:
            pass
    def circle10_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.slope_r2 = float(self.circle10_dot_radius.Text)
        except:
            pass
    def circle11_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.slope_r3 = float(self.circle11_dot_radius.Text)
        except:
            pass
    def circle12_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.slope_r4 = float(self.circle12_dot_radius.Text)
        except:
            pass
    
    def stepping_input_changed(self, sender, e):
        try:
            self.model.stepping = float(self.stepping_input.Text)
        except:
            pass
    
    def position_input_changed(self, sender, e):
        try:
            self.model.position = float(self.position_input.Text)
        except:
            pass
    
    def fill_row_frits(self, sender, e):
        self.clear_dots()
        self.model.fill_dots()
        for d in self.model.dots:
            d.draw(self.display, self.display_color)
    
    def clear_dots(self):
        self.display.Clear()
        #print(self.model.row_id)
        #del self.model.dots[self.model.row_id]
    
    def bake(self):
        layer_name = 'page_{0}_row_{1}'.format(self.parent.page_id, self.model.row_id)
        rs.AddLayer(layer_name,get_color(self.model.row_id), parent='fuyao_frits')
        for d in self.model.dots:
            obj = d.bake()
            rs.ObjectLayer(obj, layer_name)

#New165 UI
class NewConfigPanel(forms.GroupBox):
    def __init__(self, parent, row_config):
        self.parent = parent
        self.model = row_config
        self.Text = '第{}排'.format(row_config.row_id)
        self.setup_view()
        self.display = rc.Display.CustomDisplay(True)
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)

    def setup_view(self):
        self.RemoveAll()
        self.basic_setting_label = forms.Label(Text='基础设置:', Font = Font('Microsoft YaHei', 12.))
        
        self.circle1_dot_radius_label = forms.Label(Text='3排相对参考线距离：')
        self.circle1_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_position3))
        self.circle1_dot_radius.Size = drawing.Size(60, -1)
        self.circle1_dot_radius.TextChanged += self.circle1_dot_radius_changed
        
        self.circle2_dot_radius_label = forms.Label(Text='2排相对参考线距离：')
        self.circle2_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_position2))
        self.circle2_dot_radius.Size = drawing.Size(60, -1)
        self.circle2_dot_radius.TextChanged += self.circle2_dot_radius_changed
        
        self.circle3_dot_radius_label = forms.Label(Text='1排相对参考线距离：')
        self.circle3_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_position1))
        self.circle3_dot_radius.Size = drawing.Size(60, -1)
        self.circle3_dot_radius.TextChanged += self.circle3_dot_radius_changed
        
        self.circle4_dot_radius_label = forms.Label(Text='1排半径：')
        self.circle4_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_r1))
        self.circle4_dot_radius.Size = drawing.Size(60, -1)
        self.circle4_dot_radius.TextChanged += self.circle4_dot_radius_changed
        
        self.circle5_dot_radius_label = forms.Label(Text='2排半径：')
        self.circle5_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_r2))
        self.circle5_dot_radius.Size = drawing.Size(60, -1)
        self.circle5_dot_radius.TextChanged += self.circle5_dot_radius_changed
        
        self.circle6_dot_radius_label = forms.Label(Text='3排半径：')
        self.circle6_dot_radius = forms.TextBox(Text='{0}'.format(self.model.circle_config.New_cross_r3))
        self.circle6_dot_radius.Size = drawing.Size(60, -1)
        self.circle6_dot_radius.TextChanged += self.circle6_dot_radius_changed
        
        
        
        
        self.stepping_label = forms.Label(Text='花点水平间距：')
        self.stepping_input = forms.TextBox(Text='{0}'.format(self.model.stepping))
        self.stepping_input.Size = drawing.Size(60, -1)
        self.stepping_input.TextChanged += self.stepping_input_changed
        
        self.position_label = forms.Label(Text='花点垂直间距：')
        self.position_input = forms.TextBox(Text='{0}'.format(self.model.position))
        self.position_input.Size = drawing.Size(60, -1)
        self.position_input.TextChanged += self.position_input_changed
        
        self.layout = forms.DynamicLayout()
        self.layout.DefaultSpacing = drawing.Size(10, 10)
       
        # default is circle dot
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.basic_setting_label, None)
        self.layout.EndVertical()
        self.layout.BeginVertical(padding=drawing.Padding(10, 0, 0, 0), spacing=drawing.Size(10, 0))
        self.layout.AddRow(self.circle1_dot_radius_label,self.circle1_dot_radius,self.circle2_dot_radius_label,self.circle2_dot_radius,None)
        self.layout.AddRow(self.circle3_dot_radius_label,self.circle3_dot_radius,self.circle4_dot_radius_label,self.circle4_dot_radius,None)
        self.layout.AddRow(self.circle5_dot_radius_label,self.circle5_dot_radius,self.circle6_dot_radius_label,self.circle6_dot_radius,None)
        self.layout.AddRow(self.stepping_label,self.stepping_input,self.position_label,self.position_input,None)
        self.layout.EndVertical()
        self.Content = self.layout
        
        
    def circle1_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_position3 = float(self.circle1_dot_radius.Text)
        except:
            pass
    def circle2_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_position2 = float(self.circle2_dot_radius.Text)
        except:
            pass
    def circle3_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_position1 = float(self.circle3_dot_radius.Text)
        except:
            pass
    def circle4_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_r1 = float(self.circle4_dot_radius.Text)
        except:
            pass
    def circle5_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_r2 = float(self.circle5_dot_radius.Text)
        except:
            pass
            
    def circle6_dot_radius_changed(self, sender, e):
        try:
            self.model.circle_config.New_cross_r3 = float(self.circle6_dot_radius.Text)
        except:
            pass
    
    def stepping_input_changed(self, sender, e):
        try:
            self.model.stepping = float(self.stepping_input.Text)
        except:
            pass
    
    def position_input_changed(self, sender, e):
        try:
            self.model.position = float(self.position_input.Text)
        except:
            pass
    
    def fill_row_frits(self, sender, e):
        self.clear_dots()
        self.model.fill_dots()
        for d in self.model.dots:
            d.draw(self.display, self.display_color)
    
    def clear_dots(self):
        self.display.Clear()
        #print(self.model.row_id)
        #del self.model.dots[self.model.row_id]
    
    def bake(self):
        layer_name = 'page_{0}_row_{1}'.format(self.parent.page_id, self.model.row_id)
        rs.AddLayer(layer_name,get_color(self.model.row_id), parent='fuyao_frits')
        for d in self.model.dots:
            obj = d.bake()
            rs.ObjectLayer(obj, layer_name)

#原Bandpage 带状&底部区域填充界面
class BandPage(forms.TabPage):
    
    # .net 必须使用__new__显示调用构造函数！！！
    def __new__(cls, *args):
        return forms.TabPage.__new__(cls)    

    def __init__(self, page_id, band_type='general'):
        self.page_id = page_id
        self.band_type = band_type
        self.Text = '黑花边区域'
        if self.band_type == 'bottom':
            self.Text = '底部黑花边区域'
        print(self.band_type)
        self.row_num = 1
        self.model = BandZone()
        self.row_panels = list()
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


    def FillButtonClick(self, sender, e):
        # self.row_num += 1
        # row_frits = RowFrits(len(self.model.rows), self.model)
       
        # self.model.rows.append(row_frits)
        # # row_frits.band_model = self.model  # type: ignore
        # self.create_interface()
        for row_panel in self.row_panels:
            row_panel.fill_row_frits(None, None)
            
    def XMLButtonClick(self, sender, e):
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
        #xml.Save("E:\\XML\\Test.xml")
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

#原BlockPage 块状区域填充界面
class BlockPage(forms.TabPage):
    
    # .net 必须使用__new__显示调用构造函数！！！
    def __new__(cls, *args):
        return forms.TabPage.__new__(cls)    

    def __init__(self, page_id):
        self.page_id = page_id
        self.Text = '第三遮阳区域'
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
        self.layout.AddSeparateRow(padding=drawing.Padding(20, 0, 0, 0), controls=[self.fill_btn1,self.fill_btn2,self.xml_btn, None])
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

#原dzBlockPage 大众块状区域填充界面
class dzBlockPage(forms.TabPage):
    
    # .net 必须使用__new__显示调用构造函数！！！
    def __new__(cls, *args):
        return forms.TabPage.__new__(cls)    

    def __init__(self, page_id):
        self.page_id = page_id
        self.Text = '第三遮阳区域-大众'
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

#获取电脑CPU_ID
def Get_CPUID():
    MC = SM.ManagementClass("Win32_Processor")
    MOC = MC.GetInstances()
    for mo in MOC:
        print(mo.Properties['ProcessorId'].Value)
    return str(mo.Properties['ProcessorId'].Value)

#字符串加密&解密
def ProcessDES(data,is_Encrypt):
    dcsp = ct.DESCryptoServiceProvider()
    #key_data = Md5(key)
    rgb_key = txt.Encoding.Unicode.GetBytes('yyyy')
    rgb_iv = txt.Encoding.Unicode.GetBytes('nnnn')
    if is_Encrypt:
        dcsp_key = dcsp.CreateEncryptor(rgb_key, rgb_iv)
    else:
        dcsp_key = dcsp.CreateDecryptor(rgb_key, rgb_iv)
    
    memory = io.MemoryStream()
    c_stream = ct.CryptoStream(memory, dcsp_key, ct.CryptoStreamMode.Write)
    c_stream.Write(data, 0, data.Length)
    c_stream.FlushFinalBlock()
    return memory.ToArray()
    


#解析许可文件
def Parse_License_file():
    license_dic = []
    input = []
    license_file = 'C:\license\License.dat'
    try:
        with open(license_file, 'r') as LF:
            for line in LF.readlines():
                #print(line)
                secret = decode(line)
                if re.match('^\s*(\S+)\s*$', secret):
                        my_match = re.match('^\s*(\S+)\s*$', secret)
                        license_dic.append(my_match.group(1))
                        #print(license_dic)
    except:
        print('error1')
        sys.exit(1)
    code2 = ''.join(reversed(license_dic[0]))
    code3 = code2.split(('#'))
    decrypt_code = {}
    decrypt_code['CPU_ID'] = code3[0]
    decrypt_code['Date'] = code3[1]
    #print(decrypt_code)
    return(decrypt_code)


#解密字符串
def decode(code):
    decode_text = ''
    Code_convert = code.replace('@','/')
    decode_text = st.Convert.FromBase64String(Code_convert)
    output_data1 = ProcessDES(decode_text,False)
    decode = txt.Encoding.UTF8.GetString(output_data1)
    #print(decode)
    return(decode)

#许可验证
def License_Check():
    date_now = datetime.datetime.now().strftime('%Y%m%d')
    CPU_ID = Get_CPUID()
    license = Parse_License_file()
    #print(license['Date'])
    if (CPU_ID != license['CPU_ID']) or (date_now >  license['Date']):
        print("许可验证失败！")
        print('error2')
        sys.exit(1)
    elif (CPU_ID == license['CPU_ID']) and (date_now <  license['Date']):
        print("许可验证通过！")



if __name__ == "__main__":
    Parse_License_file()
    License_Check()
    dialog = FritDialog();
    # rc = dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    Rhino.UI.EtoExtensions.ShowSemiModal(dialog, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)