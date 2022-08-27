#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, August 24th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
from frits import FritType
from frits.CircleDot import CircleDot, CircleDotConfig
from frits.RoundRectDot import RoundRectConfig, RoundRectDot
import ghpythonlib.components as ghcomp
import utils
import math
import Rhino.Geometry as rg
import Rhino as rc
import Grasshopper as gh
import scriptcontext
import clr

clr.AddReference("System.Xml")
import System.Xml

class HoleArrangeType:
    HEADING=0
    CROSS=1
    @staticmethod
    def get_hole_arrange_type():
        return ['顶头', '交错']

class HoleFrits:
    def __init__(self, hole_id, region):
        self.hole_id = hole_id
        self.dot_type = FritType.CIRCLE_DOT
        self.dot_config = CircleDotConfig()
        self.stepping = 0
        self.vspace = 0

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
    
    def fill_dots(self):
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
        
        self.border_curve = self.construct_border(top_curve, bottom_curve)
        
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
        
        return blockborder

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
        #To do: get outer_anchor and hspace from border rows
        
        outer_anchor = ghcomp.Merge(top_outer_anchor, bottom_outer_anchor)
        hspace = (horizontal+vertical)/2
        
        #outer_anchor_num = int(ghcomp.Length(outer_border)/hspace)
        #outer_anchor, _, _ = ghcomp.DivideCurve(outer_border, outer_anchor_num, False)
        
        offset = horizontal
        if aligned == True:
            offset = math.sqrt(horizontal*horizontal + vertical*vertical)
        else:
            offset = math.sqrt(0.25*horizontal*horizontal + vertical*vertical)
        
        inner_aux_border = ghcomp.OffsetCurve(outer_border, 3*offset, plane=ghcomp.XYPlane(), corners = 1)
        aux_num = int(2 * ghcomp.Length(inner_aux_border) / hspace)
        aux_pts, _, _ = ghcomp.DivideCurve(inner_aux_border, aux_num, False)
        verbose_pts, _, _ = ghcomp.ClosestPoint(aux_pts, inner_pts)
        inner_anchor, _ = ghcomp.DeleteConsecutive(verbose_pts, False)
        inner_border = ghcomp.PolyLine(inner_anchor, True)
        
        relationship, _ = ghcomp.PointInCurve(inner_pts, inner_border)
        outside_pattern, _ = ghcomp.Equality(relationship, 0)
        iter_pts, _ = ghcomp.Dispatch(inner_pts, outside_pattern)
        inside_pattern, _ = ghcomp.Equality(relationship, 2)
        fix_pts, _ = ghcomp.Dispatch(inner_pts, inside_pattern)
        
        anchor_pts = ghcomp.Merge(outer_anchor, inner_anchor)
        all_pts = ghcomp.Merge(anchor_pts, iter_pts)
        
        top_crv = ghcomp.PolyLine(top_outer_anchor, False)
        bottom_crv = ghcomp.PolyLine(bottom_outer_anchor, False)
        print("*******construct anchor crv*******")
        print(len(top_outer_anchor))
        print(len(bottom_outer_anchor))
        print(top_crv)
        print(bottom_crv)
        
        outer_anchor_border = self.construct_border(top_crv, bottom_crv)
        
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
        
        print("***********get border line**********")
        
        """
        self.display_color = rc.Display.ColorHSL(0.83,1.0,0.5)
        self.display = rc.Display.CustomDisplay(True)
        self.display.Clear()
        
        for i in range(len(border_line)):
            crv = rg.NurbsCurve.CreateFromLine(border_line[i])
            self.display.AddCurve(crv, self.display_color, 1)
        
        scriptcontext.doc.Views.Redraw()
        """
        
        threshold = horizontal
        if vertical < threshold:
            threshold = vertical
        if offset < threshold:
            threshold = offset
        threshold = (offset + threshold)/2
        
        link = horizontal
        if vertical > link:
            link = vertical
        if offset > link:
            link = offset

        goal_anchor = ghcomp.Kangaroo2Component.Anchor(point = anchor_pts, strength = 10000)
        goal_zfix = ghcomp.Kangaroo2Component.AnchorXYZ(point = all_pts, x = False, y = False, z = True, strength = 1000)
        goal_cpcin = ghcomp.Kangaroo2Component.CurvePointCollide(points = iter_pts, curve = outer_border, plane = ghcomp.XYPlane(), interior = True, strength = 1)
        goal_cpcout = ghcomp.Kangaroo2Component.CurvePointCollide(points = iter_pts, curve = inner_border, plane = ghcomp.XYPlane(), interior = False, strength = 1)
        goal_cpcin = [goal_cpcin]
        goal_cpcout = [goal_cpcout]
        goal_inner_length = ghcomp.Kangaroo2Component.LengthLine(line = inner_line, strength = 0.1)
        goal_inner_threshold = ghcomp.Kangaroo2Component.ClampLength(line = inner_line, lowerlimit = threshold, upperlimit = link, strength = 1)
        goal_border_length = ghcomp.Kangaroo2Component.LengthLine(line = border_line, length = threshold, strength = 0.2)
        
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
            if row.dot_type == FritType.CIRCLE_DOT:
                row.circle_config.r = val['r']
            elif row.dot_type == FritType.ROUND_RECT:
                row.round_rect_config.k = val['k']
                row.round_rect_config.r = val['r']
            rows.append(row)
        return rows
       

    