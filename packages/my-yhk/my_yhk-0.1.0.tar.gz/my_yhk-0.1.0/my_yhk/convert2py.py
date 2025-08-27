#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   convert2py.py
@Time    :   2025/08/27 15:05:03
@Author  :   yhk
'''


from pypinyin import lazy_pinyin
import jieba

def convertopy(text):
    words = jieba.lcut(text)  # 分词: ['重阳', '节']
    pinyin_list = [lazy_pinyin(word) for word in words]
    return pinyin_list



