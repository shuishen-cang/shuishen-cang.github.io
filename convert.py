'''
Author: your name
Date: 2021-02-01 16:52:13
LastEditTime: 2021-02-01 23:39:05
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /mydoc/python/convert.py
'''

import sys,os,shutil,re

python_path = os.getcwd()
md_path = os.path.abspath(os.path.join(python_path,'./mydoc'))
blog_path = os.path.abspath(os.path.join(python_path,'./content/post'))
image_path = os.path.abspath(os.path.join(python_path,'./content/post/images'))

def find_allmd():
    for (root, dirs, files) in os.walk(md_path):
        for file in files:
            if file.endswith('.md'):
                file_txt = process_picture(os.path.join(root,file))
                file_txt = process_mermaid(file_txt)
                create_newfile(file_txt, file)

def process_picture(file_path):
    with open(file_path,'r') as f:
        txt = f.read()
        f.close()

    pic_paths = re.findall( r'\[image(.*?)\]\((.*?)\)', txt)
    for pic in pic_paths:
        pic_filepath = os.path.split(pic[1])[0]
        pic_filename = os.path.split(pic[1])[1]
        print(pic_filepath)
        print(pic_filename)
        txt = txt.replace(pic_filepath, '../images')
        try:
            shutil.copyfile(pic[1],os.path.join(image_path,pic_filename))
        except:
            pass
    return txt

def process_mermaid(txt):
    mermaid_codes = re.findall( r'```mermaid\n(.*?)```', txt, re.S)
    for mermaid_code in mermaid_codes:
        old_txt = '```mermaid\n' + mermaid_code + '```'
        new_txt = '<div class=\"mermaid\">\n' + mermaid_code + '</div>'
        txt = txt.replace(old_txt, new_txt)

    txt += '\n<script src=\"../js/mermaid.min.js\"></script>'
    return txt

def create_newfile(file_txt,file):
    file_path = os.path.join(blog_path,file)
    with open(file_path,'w') as f:
        f.write(file_txt)
        f.close()


def main():
    find_allmd()

main()