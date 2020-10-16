import re
import json
import configparser


class StringContent(object):
    @classmethod
    def de_noise_by_character(cls, content, removes=None, retains=None):
        """
        文本去除指定符号
        :param content:待处理的文本:
        :param removes:需要删除的符号
        :param retains: 需要保留的符号
        :return: 处理完成的文本
        """
        if not content:
            return ''
        patterns = {' ', '\r\n', '<', '>', '!', '\t', '\n', '·'}
        if isinstance(removes, str):
            removes = [removes]
        patterns.update(set(removes)) if removes else ''
        if isinstance(retains, str):
            retains = [retains]
        patterns.difference_update(set(retains)) if retains else ''
        if not patterns:
            return content
        pattern = ''.join(list(patterns))
        pattern = '[%s]' % pattern
        return re.sub(r'%s' % pattern, '', content.strip())


class NumberContent(object):
    @classmethod
    def string2number(cls, content, num_default=0.0, return_type='float'):
        """
        将一段文本中提取出数字
        :param content: 要提取的文本
        :param num_default: 默认数字
        :param return_type: 返回类型
        :return: 返回一个数字
        """
        num = num_default
        if isinstance(content, int) or isinstance(content, float):
            num = content
        if isinstance(content, str):
            content = re.sub(r'[（）\(\),]', '', content).strip()
            if '万' in content:
                num = float(content.split('万')[0]) * 10000
            if '亿' in content:
                num = float(content.split('亿')[0]) * 100000000
        if return_type == 'int':
            return int(num)
        elif return_type == 'float':
            return float(num)

    @classmethod
    def zh2arabic(cls, content):
        config = configparser.ConfigParser()
        config.read('conf/num.ini', encoding='utf-8')
        zh_arabic_nums = eval(config.get('ZH_ARABIC_NUM', 'ZH_ARABIC_NUM'))
        for zh_arabic_num in zh_arabic_nums:
            content = re.sub(r'%s' % zh_arabic_num[1], str(zh_arabic_num[0]), content)
        return content


class JsonContent(object):
    @classmethod
    def string_dumps(cls, content, start='', end='', **kwargs):
        """
        解析出一段文本含有json格式的字符串
        :param content: 要解析的文本
        :param start: json字符串前方无用的文本
        :param end: json字符串后方无用的文本
        :param kwargs: json模块的dumps函数参数
        :return: 返回json字符串形式的内容
        """
        regx = re.compile(r"""%s(.*?)%s""" % (start, end), re.S | re.M | re.I)
        result = re.search(regx, content).group(1)
        if kwargs:
            return json.dumps(json.loads(result), **kwargs)
        return result

    @classmethod
    def string_loads(cls, content, start='', end='', **kwargs):
        """
        解析出一段文本含有json格式的字符串
        :param content: 要解析的文本
        :param start: json字符串前方无用的文本
        :param end: json字符串后方无用的文本
        :param kwargs: json模块的loads函数参数
        :return: 返回Python形式的内容
        """
        result = cls.string_dumps(content, start, end)
        return json.loads(result, **kwargs)


class DateContent(object):
    @classmethod
    def zh_month_parse(cls, content, suffix=''):
        """
        将带有中文的月份的文本进行数字化
        :param content: 要处理的文本
        :param suffix: 后缀，默认只保留数字，可指定如:月
        :return: 处理完的文本
        """
        config = configparser.ConfigParser()
        config.read('conf/time.ini', encoding='utf-8')
        zh_months = eval(config.get('ZH_MONTH', 'ZH_MONTH'))
        for zh_month in zh_months:
            content = re.sub(r'%s' % zh_month[1], '%s%s' % (str(zh_month[0]), suffix), content)
        return content

    @classmethod
    def en_month_parse(cls, content, suffix=''):
        """
        将带有中文的月份的文本进行数字化
        :param content: 要处理的文本
        :param suffix: 后缀，默认只保留数字，可指定如:月
        :return: 处理完的文本
        """
        config = configparser.ConfigParser()
        config.read('conf/time.ini', encoding='utf-8')
        en_months = eval(config.get('EN_MONTH', 'EN_MONTH'))
        for en_month in en_months:
            content = re.sub(r'%s' % en_month[1], '%s%s' % (str(en_month[0]), suffix), content)
        return content


if __name__ == '__main__':
    res = NumberContent.zh2arabic('十一')
    print(res)
