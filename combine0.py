#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import pandas as pd
import glob
import re
outFileName = 'out_merged_result.py'
outFileName1 = 'out_merged_result1.py'

def merge():
    file_list = glob.glob('./files/*.py')       #合并./files/下所有文件
    print(u'共发现%s个py文件！' % len(file_list))
    print(u'开始合并：')
    for file in file_list:
        fr = open(file, 'r', encoding='utf-8', errors='ignore').read()          #合并
        with open(outFileName, 'a') as f:
            f.write(fr)
    print(u'合并完毕！')
    dropline()
        #file_contents = file.readlines()  # 按行读取全部内容
        #outFileName = open(r'./out_merged_result.py', 'w', encoding='utf-8')  # 打开要写入数据的目标文件
        #for content in file_contents:  # 逐行读取
            # if '#' or 'from' or 'import' in content:
            #     break
            # else:
            #     outFileName.write(content)  # 将符合要求的内容写入文件
        # fr = open(file, 'r',encoding='utf-8', errors='ignore').read()
        # with open(outFileName, 'a') as f:
        #     if '#'or'from'or'import' in fr:
        #         break
        #     else:
        #         f.write(fr)
        #file_contents = file.readlines()
    # print(u'合并完毕！')

def dropline():
    lineList = []
    matchPattern = re.compile(r'import')
    matchPattern1 = re.compile(r'@')
    matchPattern2 = re.compile(r'#!/')
    matchPattern3 = re.compile(r'-*-')
    file = open(outFileName, 'r', encoding='utf-8', errors='ignore')
    while 1:
        line = file.readline()
        if not line:
            #print("Read file End or Error")
            break
        elif matchPattern.search(line):
            pass
        elif matchPattern1.search(line):
            pass
        elif matchPattern2.search(line):
            pass
        elif matchPattern3.search(line):
            pass
        else:
            lineList.append(line)
    file.close()
    file = open(outFileName1, 'w', encoding='utf-8', errors='ignore')
    for i in lineList:
        file.write(i)
    file.close()


def readFileAsLine():
    file=open(r'D:\projects\PycharmProjects\FuyaoFrit-new_version\Frit.py','r',encoding='utf-8')    #打开目标文件
    file_contents=file.readlines()                    #按行读取全部内容
    outFileName=open(r'./out_merged_result1.py','w',encoding='utf-8')   #打开要写入数据的目标文件

    for content in file_contents:     #逐行读取

        print(content)
        outFileName.write(content)  # 将符合要求的内容写入文件
        # until
        if 'class' in content:
            break


def unique(file):
    df = pd.read_csv(file, encoding='utf-8',header=None, on_bad_lines='skip', quotechar=None, quoting=3)
    dataList = df.drop_duplicates()
    dataList.to_csv(file)


if __name__ == '__main__':
#    readFileAsLine()
    print(u'查找当前目录下的py文件：')
    merge()

#    print(u'开始去重：')
#    unique(outFileName)
#    print(u'去重完成！')