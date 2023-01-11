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
    save_file_dialog = Rhino.UI.SaveFileDialog()
    save_file_dialog.FileName = ".xml"
    save_file_dialog.Filter = "(*.xml)"
    #save_file_dialog.InitialDirectory = \
    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)
    if save_file_dialog.ShowDialog() == DialogResult.OK:
        file_name = save_file_dialog.FileName
    print(file_name)
    return file_name