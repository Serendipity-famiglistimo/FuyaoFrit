#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, August 17th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import Rhino
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
import Eto.Forms as forms
import Eto.Drawing as drawing
from Eto.Drawing import Size, Font, FontStyle
import view.RowConfigPanel as RowConfigPanel
import view.DefaultPage as DefaultPage
import view.BandPage
from view.BlockPage import BlockPage
import model.RowFrits
import model.HoleFrits
import view.HoleConfigPanel
from view.dzBlockPage import dzBlockPage
from view.NewPage import NewBlockPage
import model.BlockZone
reload(model.BlockZone)
reload(model.HoleFrits)
reload(view.HoleConfigPanel)
reload(view.BlockPage)
reload(model.RowFrits)
reload(view.BandPage)
reload(RowConfigPanel)
reload(DefaultPage)
import os
import clr
# from RowControl import RowControl
from System.Drawing import Color
from model.ChooseZone import con

#class control():
#    def __init__(self):
#        self.type = '大众图纸'
#        self.choose = 'false'
#con = control()

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
        self.list.DataStore = ['大众图纸', '88LF', '76720LFW00027','00841LFW00001','00399LFW00012','00792LFW000023','New_165']
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

class FritDialog(forms.Dialog[bool]):
    def __init__(self):
        current_path1 = os.getcwd()
        self.Title = '福耀印刷花点排布工具'
        self.Icon = drawing.Icon(current_path1+"\\ico\\FY.ico")
        self.Padding = drawing.Padding(10)
        self.Resizable = False
        self.Closing += self.OnFormClosed
        self.MinimumSize = Size(900, 600)
        # 菜单
        self.create_menu()
        self.create_toolbar()
        self.tab = forms.TabControl()
        self.tab.TabPosition = forms.DockPosition.Top
        default_page = DefaultPage.DefaultPage()
        # default_page.create()
        self.tab.Pages.Add(default_page)
        
        self.regions = []

 
        # 标题
        # self.heading_label = forms.Label(Text= '带状区域', Font = Font('Microsoft YaHei', 14., FontStyle.Bold))
        # # self.m_headding.Color = drawing.Color.FromArgb(255, 0, 0)
        # self.heading_label.TextAlignment = forms.TextAlignment.Center
        # self.addButton = forms.Button(Text='添加行')
        # self.addButton.Click += self.AddButtonClick
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
        open_menu.Image = drawing.Bitmap(current_path + '\\ico\\file-open.png')
        file_menu.Items.Add(open_menu, 0)
        
        add_region_menu = forms.Command(self.AddBandRegionCommand)
        add_region_menu.MenuText = "添加黑花边"
        add_region_menu.Image = drawing.Bitmap(current_path + '\\ico\\line.png')
        edit_menu.Items.Add(add_region_menu,0)
        
        add_region_menu1 = forms.Command(self.AddBlockRegionCommand)
        add_region_menu1.MenuText = "添加第三遮阳区"
        add_region_menu1.Image = drawing.Bitmap(current_path + '\\ico\\rect.png')
        edit_menu.Items.Add(add_region_menu1,1)

        add_region_menu2 = forms.Command(self.AddBottomRegionCommand)
        add_region_menu2.MenuText = "添加底部黑花边"
        add_region_menu2.Image = drawing.Bitmap(current_path + '\\ico\\rect.png')
        edit_menu.Items.Add(add_region_menu2,1)
    
    def create_toolbar(self):
        current_path = os.getcwd()
        self.ToolBar = forms.ToolBar()
        # cmdButton = new Command { MenuText = "Click Me!", ToolBarText = "Click Me!" };
        
        transit_curve = forms.Command(self.TransitCurveCommand)
        transit_curve.MenuText = '过渡曲线'
        transit_curve.Image = drawing.Bitmap(current_path + '\\ico\\cross.png')
        self.ToolBar.Items.Add(transit_curve)

        bake_dots = forms.Command(self.BakeDotsCommand)
        bake_dots.MenuText = '导出花点'
        bake_dots.Image = drawing.Bitmap(current_path + '\\ico\\bake.png')
        self.ToolBar.Items.Add(bake_dots)

        # self.ToolBar.Items.Add(bake_dots)



    # Start of the class functions
    def OnFormClosed(self, sender, e):
        for region in self.regions:
            region.clear_dots()
        # self.display.Clear()
    

    def AddBandRegionCommand(self, sender, e):
        page = view.BandPage.BandPage(len(self.regions))
        self.regions.append(page)
        self.tab.Pages.Add(page)
    
    def AddBottomRegionCommand(self, sender, e):
        page = view.BandPage.BandPage(len(self.regions), 'bottom')
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
        

if __name__ == "__main__":
    dialog = FritDialog();
    # rc = dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    Rhino.UI.EtoExtensions.ShowSemiModal(dialog, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)