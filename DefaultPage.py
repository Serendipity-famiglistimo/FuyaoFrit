#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
# @Author: Xu Wang
# @Date: Thursday, August 18th 2022
# @Email: wangxu.93@hotmail.com
# @Copyright (c) 2022 Institute of Trustworthy Network and System, Tsinghua University
'''
import Eto.Forms as forms
from Eto.Drawing import Size, Font, FontStyle

class DefaultPage(forms.TabPage):
    def __init__(self):
        forms.TabPage.__init__(self)

        # 标题
        self.heading_label = forms.Label(Text= '福耀印刷花点排布工具', Font = Font('Microsoft YaHei', 14., FontStyle.Bold))
        # self.m_headding.Color = drawing.Color.FromArgb(255, 0, 0)
        self.heading_label.TextAlignment = forms.TextAlignment.Center 
