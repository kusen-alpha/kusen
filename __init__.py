#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2020/10/15

from tools.content import *
from extractor.extractorDate import DateTextExtract,DateHtmlExtract

if __name__ == '__main__':
    # res = DateContent.zh_month_parse('十一月， 十二月',suffix='月')
    # print(res)

    text = '注册时间：2019年十一月11日'
    # text = processText(text)
    # print('text:', text)
    #
    test = DateTextExtract(text)
    print(test.extract())

    print('-' * 50)

    html = """dd
    """
    test1 = DateHtmlExtract(html)
    res = test1.extract()
    print(res)


