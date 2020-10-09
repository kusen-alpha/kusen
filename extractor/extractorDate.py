import re
import time
import conf
from datetime import datetime
from datetime import timedelta
from lxml.html import fromstring
from lxml.etree import ParserError


def cutSymbol(s: str, re_remove='', re_retain=''):
    """
    去除指定符号
    :param 待处理的文本:
    :param re_remove:需要删除的符号
    :param re_retain: 需要保留的符号
    :return: 处理完成的文本
    """
    if re_remove != '' and isinstance(re_remove, str):
        re_remove = [re_remove]
    if re_retain != '' and isinstance(re_retain, str):
        re_retain = [re_retain]
    re_default = [' ', '\r\n', '<', '>', '!', '\t', '\n', '·']
    re_parrent = set(re_remove) or set(re_default).difference(set(re_retain))
    re_parrent = ''.join(list(re_parrent))
    re_parrent = '[%s]' % re_parrent
    return re.sub(r'%s' % re_parrent, '', s.strip())


def special2ArabicNumber(text):
    """
    将非阿拉伯数字转为阿拉伯数字
    :param text: 待处理的文本
    :return: 处理完成的文本
    """
    for i in conf.SPECIAL_NUMBERS:  # 默认的数字对照表
        for j in i[1:]:
            text = re.sub(r'%s' % j, str(i[0]), text)
    return text


def dateEn2DateCn(text):
    """
    将英文日期转为中文日期
    :param text: 待处理的文本
    :return: 处理完的文本
    """
    for i in conf.DATE_EN:
        for j in i[1:]:
            text = re.sub(r'%s' % j, str(i[0]), text)
    return text


def processText(text):
    text = cutSymbol(text, re_retain=' ')
    text = special2ArabicNumber(text)
    text = dateEn2DateCn(text)
    return text


class extractDateFromText(object):
    def __init__(self, dateStr=None):
        """

        :param dateStr: 含有时间的文本
        """
        self.dateStr = dateStr
        self.time_pattern = conf.DATETIME_PATTERN
        if dateStr:
            self.extract(self.dateStr)

    def extract(self, dateStr=None, type='s', isfloat=False, notfind=None):
        """
        解析文本中的时间
        :param dateStr: 含有时间的文本
        :param type: 获取时间的类型，s为秒，ms为毫秒
        :param isfloat: 是否保留小数
        :param notfind: 当没匹配到时间时返回的时间类型
        :return: 返回一个(datetime对象,时间戳)
        """
        if dateStr:
            self.dateStr = dateStr
        self.date = self._extract(self.dateStr, notfind=notfind)
        self.time_stamp = self._date2timestamp(self.date)
        return self.date, self.getTimeStamp(type=type, isfloat=isfloat)

    def getDdate(self):
        return self.date

    def getTimeStamp(self, type='s', isfloat=True):
        """
        获取时间戳
        :param type: 获取时间的类型，s为秒，ms为毫秒
        :param isfloat: 是否保留小数
        :return: 时间戳
        """
        if not self.time_stamp:
            return ""
        if not isfloat:
            self.time_stamp = int(self.time_stamp)
        if type == 'ms':
            self.time_stamp = int(self.time_stamp * 1000)
        return self.time_stamp

    def _date2timestamp(self, date: datetime):
        """
        datetime结构化时间转时间戳
        :param date: datetime格式的时间
        :return: 时间戳
        """
        if not date:
            return ""
        return date.timestamp()

    def _extract(self, dateStr, notfind):
        """
        解析文本中的时间
        :param dateStr:待处理的时间文本
        :param notfind:当没匹配到时间时返回的时间类型
        :return: 结构化时间或''
        """
        my_datetime = datetime.today()  # 当前时间
        for pattern in self.time_pattern:
            try:
                dt_obj = re.search(pattern, dateStr, re.M | re.I)
            except:
                print('error pattern is :', pattern)
                continue
            if dt_obj:
                print(pattern)
                my_struct_time = self._set_struct_time(my_datetime, dt_obj.groupdict())
                return my_struct_time
        else:
            if notfind == 'now':
                return my_datetime
            return ''

    def _set_struct_time(self, base_time, dt_obj_groupdict):
        """
        计算处理时间
        :param base_time: 初始时间
        :param dt_obj_groupdict: 正则匹配到的时间分组字典
        :return: 结构化时间
        """
        print(dt_obj_groupdict)

        # 抽取到的标准时间
        year = self._get_data_from_group_data(dt_obj_groupdict, 'year', base_time.year, base_time.year)
        if isinstance(year, str) and len(year) == 2:
            year = '20' + year
        year = int(year)
        month = int(self._get_data_from_group_data(dt_obj_groupdict, 'month', base_time.month, base_time.month))
        day = int(self._get_data_from_group_data(dt_obj_groupdict, 'day', base_time.day, base_time.day))
        hour = int(self._get_data_from_group_data(dt_obj_groupdict, 'hour', base_time.hour, base_time.hour))
        minute = int(self._get_data_from_group_data(dt_obj_groupdict, 'minute', base_time.minute, base_time.minute))
        second = int(self._get_data_from_group_data(dt_obj_groupdict, 'second', base_time.minute, base_time.minute))
        timestamp = self._get_data_from_group_data(dt_obj_groupdict, 'timestamp', 0, 0)
        if timestamp:
            timestamp = int(timestamp) if len(timestamp) == 10 else int(timestamp) // 1000
            if timestamp > int(time.time()):
                timestamp = 0

        # 抽取到的具有变化含义的时间
        change_year = int(self._get_data_from_group_data(dt_obj_groupdict, 'change_year', 0, 0))
        change_month = int(self._get_data_from_group_data(dt_obj_groupdict, 'change_month', 0, 0))
        change_week = int(self._get_data_from_group_data(dt_obj_groupdict, 'change_week', 0, 0))
        change_day = int(self._get_data_from_group_data(dt_obj_groupdict, 'change_day', 0, 0))
        change_hour = int(self._get_data_from_group_data(dt_obj_groupdict, 'change_hour', 0, 0))
        change_minute = int(self._get_data_from_group_data(dt_obj_groupdict, 'change_minute', 0, 0))
        change_second = int(self._get_data_from_group_data(dt_obj_groupdict, 'change_second', 0, 0))
        if change_year > 0:
            change_day += change_year * 365
        if change_month > 0:
            change_day += change_month * 30
        if change_week > 0:
            change_day += change_week * 7

        # 抽取到具有特殊含义的时间
        name_day = self._get_data_from_group_data(dt_obj_groupdict, 'name_day', "", "")
        name_other = self._get_data_from_group_data(dt_obj_groupdict, 'name_other', "", "")
        if name_day:
            if name_day == "今天":
                change_day += 0
            elif name_day == "昨天":
                change_day += 1
            elif name_day == "前天":
                change_day += 2
        if name_other:
            if name_other == '刚刚':
                change_second = 10

        try:  # 时间计算
            change_date = timedelta(weeks=change_week, days=change_day, hours=change_hour, minutes=change_minute,
                                    seconds=change_second)
            if timestamp:
                my_datetime = datetime.fromtimestamp(timestamp)
            else:
                my_datetime = base_time.replace(year=year, month=month, day=day, hour=hour, minute=minute,
                                                second=second)
            last_datetime = my_datetime - change_date
            if last_datetime > base_time:  # 不能大于当前时间
                return base_time
            return last_datetime
        except Exception:
            print('error')
            return base_time

    def _get_data_from_group_data(self, group_data, group_type, group_donthave, group_none):
        """
        从分组字典中取值
        :param group_data: 分组字典
        :param group_type: 获取的类型,字典的key
        :param group_donthave: 当分组字典中没有时赋予的值
        :param group_none: 当分组字典获取为''时赋予的值
        :return: 获取的值
        """
        data = group_data.get(group_type, group_donthave)
        if not data:
            data = group_none
        return data


def strhtml2element(strhtml):
    try:
        html = re.sub('</?br.*?>', '', strhtml)
        element = fromstring(html)
        return element
    except ParserError:
        return


class extractDateFromHtmlMeta(object):
    def __init__(self, html=None):
        """

        :param html: HtmlElement or strHtml
        """
        self.publish_time_meta = conf.PUBLISH_TIME_META
        self.html = html
        if self.html:
            self.extract(self.html)

    def extract(self, html=None):
        if html:
            self.html = html
        if isinstance(self.html, str):
            self.html = strhtml2element(self.html)
        if not self.html:
            return
        self.date = self._extract()
        return self.date

    def _extract(self):
        for xpath in self.publish_time_meta:
            publish_time = self.html.xpath(xpath)
            if publish_time:
                return ''.join(publish_time)
        return ''


if __name__ == '__main__':
    text = '注册时间：2019年9月11日'
    text = processText(text)
    print('text:', text)
    #
    test = extractDateFromText(text)
    print(test.extract(type='s', notfind='now'))

    print('-' * 50)

    # html="""
    # """
    # test2 = extractDateFromHtmlMeta(html)
    # date_text = test2.extract()
    # test.extract(date_text)
