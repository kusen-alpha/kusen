import re
import time
import configparser
from datetime import datetime
from datetime import timedelta
from lxml.html import fromstring, tostring, HtmlElement
from tools.content import StringContent, NumberContent, DateContent


class DateTextExtract(object):
    def __init__(self, text=None, is_de_noise_by_character=True, characters_removes=None, characters_retains=None,
                 is_zh2arabic=True, is_zh_month_parse=True, zh_month_suffix='月', is_en_month_parse=True,
                 en_month_suffix=''):

        self.is_de_noise_by_character = is_de_noise_by_character
        self.characters_removes = characters_removes
        self.characters_retains = characters_retains
        self.is_zh2arabic = is_zh2arabic
        self.is_zh_month_parse = is_zh_month_parse
        self.zh_month_suffix = zh_month_suffix
        self.is_en_month_parse = is_en_month_parse
        self.en_month_suffix = en_month_suffix

        self.result_struct_time = None

        self.config = self.get_config('datetime_pattern.ini')
        self.time_pattern = eval(self.config.get('DATETIME', 'DATETIME_PATTERN'))
        if not text:
            raise ValueError('文本不能为空！')
        self.text = text

    @staticmethod
    def get_config(file_name):
        config = configparser.ConfigParser()
        config.read('conf/%s' % file_name, encoding='utf-8')
        return config

    def extract(self, *args, **kwargs):
        return self._extract_text(self.text, *args, **kwargs)

    def _extract_text(self, text, is_struct=False, mode='s', is_float=False, default_date='now'):
        self._extract_from_text(text, default_date=default_date)
        if is_struct:
            return self.result_struct_time
        time_stamp = self.result_struct_time.timestamp()
        if mode == 's':
            return int(time_stamp)
        elif mode == 'ms':
            if is_float:
                return int(time_stamp * 1000)
            return int(time_stamp) * 1000

    def _extract_from_text(self, text, default_date):
        now = datetime.today()  # 当前时间
        self.text = text
        if self.is_de_noise_by_character:
            self.text = StringContent.de_noise_by_character(self.text, self.characters_removes,
                                                            self.characters_retains)
        if self.is_zh2arabic:
            self.text = NumberContent.zh2arabic(self.text)
        if self.is_zh_month_parse:
            self.text = DateContent.zh_month_parse(self.text, suffix=self.zh_month_suffix)
        if self.is_en_month_parse:
            self.text = DateContent.en_month_parse(self.text, suffix=self.en_month_suffix)
        for pattern in self.time_pattern:
            try:
                dt_obj = re.search(pattern, self.text, re.M | re.I)
            except Exception as e:
                # print('error pattern is :', pattern, e)
                continue
            if dt_obj:
                # print(pattern)
                self._set_struct_time(now, dt_obj.groupdict())
                break
        else:
            if default_date == 'now':
                self.result_struct_time = now
            else:
                self.result_struct_time = default_date

    def _set_struct_time(self, base_time, dt_obj_groupdict):
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
                now = datetime.fromtimestamp(timestamp)
            else:
                now = base_time.replace(year=year, month=month, day=day, hour=hour, minute=minute,
                                        second=second)
            last_datetime = now - change_date
            if last_datetime > base_time:  # 不能大于当前时间
                self.result_struct_time = base_time
            else:
                self.result_struct_time = last_datetime
        except Exception as e:
            # print('error', e)
            self.result_struct_time = base_time

    def _get_data_from_group_data(self, group_data, group_type, group_donthave, group_none):
        data = group_data.get(group_type, group_donthave)
        if not data:
            data = group_none
        return data


class DateHtmlExtract(DateTextExtract):
    def __init__(self, text_or_html, *args, **kwargs):
        if not text_or_html:
            raise ValueError('请输入有意义的内容！')
        if isinstance(text_or_html, str):
            self.html = fromstring(text_or_html)
            text = text_or_html
        elif isinstance(text_or_html, HtmlElement):
            self.html = text_or_html
            text = tostring(text_or_html)
        else:
            raise ValueError('内容不合规范！')
        super(DateHtmlExtract, self).__init__(text, *args, **kwargs)
        self.publish_datetime = None
        self.__datetime_tag = {}

    def extract(self, *args, **kwargs):
        self._extract_html(*args, **kwargs)
        return self.publish_datetime

    def _extract_html(self, check_meta=True, whole_page=True, check_tags={}, restrict_xpath=None, restrict_re=None,
                      *args, **kwargs):
        if restrict_xpath or restrict_re:
            self._extract_from_xpath_or_re(restrict_xpath, restrict_re)
        if check_meta and not self.publish_datetime:
            self._extract_from_meta()
        if check_tags and not self.publish_datetime:
            self._extract_from_tag(check_tags)
        if whole_page and not self.publish_datetime:
            self._extract_whole_page(*args, **kwargs)

    def _extract_from_tag(self, tags):
        self.__datetime_tag.update(tags)
        # TODO 找出符合条件的tag

    def _extract_from_xpath_or_re(self, xpath, _re):
        result = self.text
        if xpath:
            xpath_result = self.html.xpath(xpath)
            if xpath_result:
                result = ''.join(xpath_result)
        if _re:
            result = re.search(_re, result).group(1)
        if result:
            self.publish_datetime = self._extract_text(result)

    def _extract_whole_page(self):
        self.publish_datetime = self._extract_text(self.text)

    def _extract_from_meta(self):
        html_time_meta = eval(self.get_config('datetime_pattern.ini').get('DATETIME', 'HTML_TIME_META'))
        _html = self.html.xpath('//head')
        if not len(_html):
            return
        for xpath in html_time_meta:
            if xpath[:2] == '//':
                xpath = xpath.replace('//', './', 1)
            publish_time = _html[0].xpath(xpath)
            if publish_time:
                self.publish_datetime = publish_time[0]
                break


if __name__ == '__main__':
    pass
