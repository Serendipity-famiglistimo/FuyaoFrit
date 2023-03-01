#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Wednesday, August 17th 2022
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
from model.XML_Output import X_Choose

class Warning(forms.Dialog):
    def __init__(self,type):
        self.Title = "提醒"
        self.ClientSize = drawing.Size(350, 65)
        self.Padding = drawing.Padding(5)
        self.Resizable = False
        #self.text = 
        self.type = type
        X_Choose.Band_xml = False
        X_Choose.Block_xml = False
        X_Choose.DZblock_xml = False
        X_Choose.NewBlock_xml = False
        self.Topmost = True
        self.warn_label = forms.Label(Text='您还未保存XML文件,是否保存?', Font=Font('Microsoft YaHei', 12.))
        self.CommitButton = forms.Button(Text = '确认')
        self.CommitButton.Click += self.OnCommitButtonClick
        self.CancelButton = forms.Button(Text = '取消')
        self.CancelButton.Click += self.OnCancelButtonClick
        
        layout = forms.DynamicLayout()
        layout.Spacing = drawing.Size(5, 5)
        layout.AddSeparateRow(None,self.warn_label,None)
        layout.AddSeparateRow(None,self.CommitButton,None,self.CancelButton,None)
        self.Content = layout
        
    
    def OnCancelButtonClick(self,sender,e):
        self.Close()
    
    
    def OnCommitButtonClick(self,sender,e):
        if self.type == 'band':
            X_Choose.Band_xml = True
        elif self.type == 'block':
            X_Choose.Block_xml = True
        elif self.type == 'dzblock':
            X_Choose.DZblock_xml = True
        elif self.type == 'newblock':
            X_Choose.NewBlock_xml = True
        self.Close()