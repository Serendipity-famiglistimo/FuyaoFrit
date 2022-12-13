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
#import view.RowConfigPanel as RowConfigPanel
#import view.DefaultPage as DefaultPage
#import view.BandPage
#import view.BlockPage
#import view.dzBlockPage
#import model.RowFrits
#import model.HoleFrits
#import view.HoleConfigPanel
#import model.BlockZone
#reload(model.BlockZone)
#reload(model.HoleFrits)
#reload(view.HoleConfigPanel)
#reload(view.BlockPage)
#reload(model.RowFrits)
#reload(view.BandPage)
#reload(RowConfigPanel)
#reload(DefaultPage)
import os
import clr
#from RowControl import RowControl
from System.Drawing import Color
clr.AddReference("System.Xml")
import System.Xml as XML



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
        add_region_menu.MenuText = "添加带状区域"
        add_region_menu.Image = drawing.Bitmap('C:\\ico\\line.png')
        edit_menu.Items.Add(add_region_menu,0)
        
        add_region_menu1 = forms.Command(self.AddBlockRegionCommand)
        add_region_menu1.MenuText = "添加块状区域"
        add_region_menu1.Image = drawing.Bitmap('C:\\ico\\rect.png')
        edit_menu.Items.Add(add_region_menu1,1)

        add_region_menu2 = forms.Command(self.AddBottomRegionCommand)
        add_region_menu2.MenuText = "添加底部区域"
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
        if con.type == '大众算法':
            page = dzBlockPage(len(self.regions))
            self.regions.append(page)
            self.tab.Pages.Add(page)
        else:
            page = BlockPage(len(self.regions))
            self.regions.append(page)
            self.tab.Pages.Add(page)

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
            
            
#原loaddata
class Data():
    def __init__(self):
        self.path_data = None
        
Save = Data()

#原defaultpage
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

#原Zone
class Zone:
    def __init__(self):
        pass
        
#原BandZone
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

#原BlockZone
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

#原dzBlockZone
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

#原HoleFrits
class HoleArrangeType:
    HEADING=0
    CROSS=1
    @staticmethod
    def get_hole_arrange_type():
        return ['顶头', '交错']


class Dazhong_fill_holes:
    def __init__(self, upline, midline, downline, boundary, split_crv, edge_crv, horizontal, vertical, aligned = False):
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
        
        self.display_color = rc.Display.ColorHSL(0, 1, 0)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
    
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
        k0 = 1.15
        h1 = 0.595 + k0/2
        h2 = 1.725 + k0/2
        h3 = 3.165 + k0/2
        k1 = 1.13
        sr1 = 0.2
        r2 = 1.11/2
        r3 = 1.03/2
        
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
        
        r0 = 0.55/2 #装饰性圆点
        r1 = 0.825/2
        r2 = 1.11/2
        r3 = 1.15/2
        
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
    
    def bake(self):
        pass
    
    def dazhong_fill_dots(self):
        self.outer_crv = self.region.curves[0]
        if self.region.is_flip[0] == True:
            self.outer_crv, _ = ghcomp.FlipCurve(self.outer_crv)
            
        self.inner_crv = self.region.curves[1]
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
        self.display.AddCurve(boundary_crv, self.display_color, 1)
        upline_crv = ghcomp.OffsetCurve(self.top_crv, plane = rs.WorldXYPlane(), distance=0.5, corners=1)
        
        dazhong_frit_generator = Dazhong_fill_holes(\
                                    upline = upline_crv, midline = self.bottom_crv, downline = self.bottom1_crv, \
                                    boundary = boundary_crv, split_crv = self.refer_crv, edge_crv = self.inner_crv, \
                                    horizontal = 2.4, vertical = 1.2, aligned = False)
        dazhong_frit_generator.run()
        
        
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



#原RowFrits
class RowArrangeType:
    HEADING=0
    CROSS=1
    @staticmethod
    def get_row_arrange_type():
        return ['顶头', '交错']

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

#原frits——init
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

#原ArcDot
class ArcDotConfig:
    def __init__(self):
        self.lr = 0
        self.sr = 0
        self.angle = 0
    
    def top(self):
        return 0
    
    def bottom(self):
        return self.lr

class ArcDot(Dot):
    def __init__(self, x, y, config, theta):
        Dot.__init__(self, x, y, config, theta)
    
    def draw(self, display, display_color):
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
#原CircleDot
class CircleDotConfig:
    def __init__(self):
        self.r = 0
    
    def top(self):
        return self.r
    
    def bottom(self):
        return self.r

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

#原RoundRectDot
class RoundRectConfig:
    def __init__(self):
        self.k = 0
        self.r = 0
    
    def top(self):
        return self.k / 2
    
    def bottom(self):
        return self.k / 2

class RoundRectDot(Dot):
    def __init__(self, x, y, config, theta):
        Dot.__init__(self, x, y, config, theta)
    
    def draw(self, display, display_color):
        x = self.centroid.X
        y = self.centroid.Y
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
#TriArc
class TriArcConfig:
    def __init__(self):
        self.lr = 0
        self.sr = 0
        self.angle = 0
    
    def top(self):
        return 0
    
    def bottom(self):
        return self.lr

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

#原HoleConfigPanel
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

#原RowConfigPanel
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
        self.layout.AddRow(self.update_btn, None)
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
    
    def clear_dots(self):
        self.display.Clear()
    
    def bake(self):
        layer_name = 'page_{0}_row_{1}'.format(self.parent.page_id, self.model.row_id)
        rs.AddLayer(layer_name,get_color(self.model.row_id), parent='fuyao_frits')
        for d in self.model.dots:
            obj = d.bake()
            rs.ObjectLayer(obj, layer_name)
    


#原Bandpage
class BandPage(forms.TabPage):
    
    # .net 必须使用__new__显示调用构造函数！！！
    def __new__(cls, *args):
        return forms.TabPage.__new__(cls)    

    def __init__(self, page_id, band_type='general'):
        self.page_id = page_id
        self.band_type = band_type
        self.Text = '带状区域'
        if self.band_type == 'bottom':
            self.Text = '底部区域'
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
            xml.Save("E:\\XML\\band\\band.xml")
            
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
            xml.Save("E:\\XML\\bottom\\bottom.xml")
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

#原BlockPage
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
        self.img.Image = Bitmap("C:\\ico\\block.png")
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

#原dzBlockPage
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
        self.insert_btn = forms.Button(Text='填充')
        self.insert_btn.Size = Size(100, 30)
        self.insert_btn.Click += self.InsertButtonClick
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
        self.layout.AddRow(self.insert_btn, None)
        self.layout.EndVertical()
        self.layout.AddSeparateRow(self.fill_label, None)
        self.layout.AddSeparateRow(padding=drawing.Padding(20, 0, 0, 0), controls=[self.fill_btn,  None])
        if len(self.model.rows) == 0:
            try:
                file_name = Save.path_data
                rows = RowFrits.load_block_xml(file_name, self.model)
                holes = HoleFrits.load_block_xml(file_name, self.model)
                self.model.holes = holes
                self.model.rows = rows
            except:
                pass
            
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

def Get_CPUID():
    MC = SM.ManagementClass("Win32_Processor")
    MOC = MC.GetInstances()
    for mo in MOC:
        print(mo.Properties['ProcessorId'].Value)
    return str(mo.Properties['ProcessorId'].Value)

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

def decode(code):
    decode_text = ''
    Code_convert = code.replace('@','/')
    decode_text = st.Convert.FromBase64String(Code_convert)
    output_data1 = ProcessDES(decode_text,False)
    decode = txt.Encoding.UTF8.GetString(output_data1)
    #print(decode)
    return(decode)


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