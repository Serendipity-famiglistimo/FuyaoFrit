#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Monday, August 15th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import os
import clr
import Eto.Forms as forms
#from RowControl import RowControl
from System.Drawing import Color
clr.AddReference("System.Xml")
import System.Xml as XML
from scriptcontext import doc
from System.Windows.Forms import *
import Rhino.UI
from System import Environment

def XMLPATH():
    file_name = "";
    
    save_file_dialog = forms.SaveFileDialog()
    filter = forms.FileFilter('.xml',".xml")
    save_file_dialog.Filters.Add(filter)
    #save_file_dialog.FileName = ".xml"
    save_file_dialog.Filters = "(*.xml)"
    #save_file_dialog.InitialDirectory = \
    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)
    save_file_dialog.ShowDialog(Rhino.UI.RhinoEtoApp.MainWindow)
    file_name = save_file_dialog.FileName
    print(file_name)
    return file_name