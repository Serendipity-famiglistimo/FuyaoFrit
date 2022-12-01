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
clr.AddReference("System")
import System as st
import System.Management as SM
import System.Text as txt
import System.Security.Cryptography as ct
import System.IO as io

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
    
def decode(code):
    decode_text = ''
    Code_convert = code.replace('@','/')
    decode_text = st.Convert.FromBase64String(Code_convert)
    output_data1 = ProcessDES(decode_text,False)
    decode = txt.Encoding.UTF8.GetString(output_data1)
    print(decode)
    return(decode)
    
def Parse_License_file():
    license_dic = []
    input = []
    license_file = 'C:\license_m\License_test1.dat'
    try:
        with open(license_file, 'r') as LF:
            for line in LF.readlines():
                print(line)
                secret = decode(line)
                if re.match('^\s*(\S+)\s*$', secret):
                        my_match = re.match('^\s*(\S+)\s*$', secret)
                        license_dic.append(my_match.group(1))
                        print(license_dic)
    except:
        sys.exit(1)
    code2 = ''.join(reversed(license_dic[0]))
    code3 = code2.split(('#'))
    decrypt_code = {}
    decrypt_code['CPU_ID'] = code3[0]
    decrypt_code['Date'] = code3[1]
    print(decrypt_code)
    return(decrypt_code)

def License_Check():
    date_now = datetime.datetime.now().strftime('%Y%m%d')
    CPU_ID = Get_CPUID()
    license = Parse_License_file()
    print(license['Date'])
    if (CPU_ID != license['CPU_ID']) or (date_now >  license['Date']):
        print("许可验证失败！")
        sys.exit(1)
    elif (CPU_ID == license['CPU_ID']) and (date_now <  license['Date']):
        print("许可验证通过！")
class SimpleEtoDialog(forms.Dialog):

    def __init__(self):
        self.Title = "Sample Eto Dialog"
        self.ClientSize = drawing.Size(200, 200)
        self.Padding = drawing.Padding(5)
        self.Resizable = False

        label = forms.Label()
        label.Text = "Hello Rhino.Python!"
        self.Content = label


def TestSampleEtoDialog():
    dialog = SimpleEtoDialog()
    dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)


if __name__ == "__main__":
    Parse_License_file()
    License_Check()
    #print('成功进入系统')
    TestSampleEtoDialog()
