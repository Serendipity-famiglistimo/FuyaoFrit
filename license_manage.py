#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms
import clr
import re
import datetime
import sys
clr.AddReference("System.Management")
import System.Management as SM



class SimpleEtoDialog(forms.Dialog):

    def __init__(self):
        self.Title = "花点使用授权管理"
        self.ClientSize = drawing.Size(800, 100)
        self.Padding = drawing.Padding(5)
        self.Resizable = False
        self.CPUID_label = forms.Label(Text = '请输入CPU序列码:')
        self.CPUID_textbox = forms.TextBox(Text = None)
        self.Date_label = forms.Label(Text = '请输入软件使用截止日期（例如：20250101）:')
        self.Date_textbox = forms.TextBox(Text = None)
        self.warning_label = forms.Label(Text = None)
        
        self.CommitButton = forms.Button(Text = '确认')
        self.CommitButton.Click += self.OnCommitButtonClick
        self.AbortButton = forms.Button(Text = '取消')
        self.AbortButton.Click += self.OnCloseButtonClick
        
        layout = forms.DynamicLayout()
        layout.Spacing = drawing.Size(5, 5)
        layout.AddRow(self.CPUID_label, self.CPUID_textbox)
        layout.AddRow(self.Date_label, self.Date_textbox)
        layout.AddRow(None) # spacer
        layout.AddRow(None,self.CommitButton, self.AbortButton)
        layout.AddRow(self.warning_label)
        
        
        self.Content = layout
        
        
    def Get_License_File(self,id,date):
        license_file = 'C:\license_m\License.dat'
        code1 = id+"#"+date
        encrypt_code = ''.join(reversed(code1))
        #print(encrypt_code)
        #print(len(encrypt_code))
        with open(license_file, 'w') as LF:
            LF.write('Encrypt_Code : %s\n'%encrypt_code)
        
    def OnCommitButtonClick(self,sender,e):
        print(self.CPUID_textbox.Text)
        print(type(self.CPUID_textbox.Text))
        print(self.Date_textbox.Text)
        print(type(self.Date_textbox.Text))
        if (self.CPUID_textbox.Text == "") or (self.Date_textbox.Text == ""):
            WarningtoDialog()
        elif (len(self.Date_textbox.Text) != 8) or (re.match('^\D+$', self.Date_textbox.Text)):
            WarningtoDialog() 
        else:
            self.Get_License_File(self.CPUID_textbox.Text,self.Date_textbox.Text)
            self.Close()
    def OnCloseButtonClick(self,sender,e):
        self.Close()

class WarningDialog(forms.Dialog):

    def __init__(self):
        self.Title = "警示信息"
        self.ClientSize = drawing.Size(500, 60)
        self.Padding = drawing.Padding(5)
        self.Resizable = False

        self.warning_label = forms.Label()
        self.warning_label.Text = "信息输入有误，请核对输入!"
        self.warning_label.TextColor = drawing.Color.FromArgb(255, 0, 0)
        self.YesButton = forms.Button(Text = '确认')
        self.YesButton.Click += self.OnYesButtonClick
        
        
        layout = forms.DynamicLayout()
        layout.Spacing = drawing.Size(5, 5)
        layout.AddRow(self.warning_label,None)
        layout.AddRow(None, self.YesButton)
        self.Content = layout
        
        
        
        
    def OnYesButtonClick(self,sender,e):
        self.Close()
    


def WarningtoDialog():
    dialog1 = WarningDialog()
    dialog1.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)



def TestSampleEtoDialog():
    dialog2 = SimpleEtoDialog()
    dialog2.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)



if __name__ == "__main__":
    TestSampleEtoDialog()