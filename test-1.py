from langconv import *
import pandas as pd
import pypinyin
from getfirstp import getPinyin
from Radical import getRadical

#偏旁部首
def radical(text):
    return getRadical(text)

# 文本转拼音
def pinyin(text):
    """
    :param text: 文本
    :return: 文本转拼音
    """
    gap = ' '
    piny = gap.join(pypinyin.lazy_pinyin(text))
    return piny

#获取首字母
def firstpinyin(text):
    gap = ''
    piny=gap.join(getPinyin(text))
    return piny

# 繁体转简体
def tradition2simple(text):
    """
    :param text: 要过滤的文本
    :return: 繁体转简体函数
    """
    line = Converter('zh-hans').convert(text)
    return line

#敏感词整合，构建敏感词库


def main():
    """
    with open(word_path, "r", encoding='utf-8') as file:
            original_sensitive_word = file.readlines()  # 读入文本

original_sensitive_word = sorted([i.split('\n')[0] for i in original_sensitive_word])  # 按照换行符区分不同敏感词
"""
    text='這是我的地盤'
    simpcode=tradition2simple(text)
    piny=pinyin(simpcode)       #拼音
    fpiny=firstpinyin(simpcode)  #首字母
    radcode=radical(simpcode[3])  #偏旁部首

if __name__ == '__main__':
    main()