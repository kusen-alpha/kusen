
# class ProxyInfo(object):
#     def __init__(self):
#         pass
#
#     def get_proxy_info(self):
#         pass
#
#
# if __name__ == '__main__':
#     pass


# -*- coding: utf-8 -*-
import re
import requests
from lxml import etree


class DownLoad(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
        }

    def down(self, *args, **kwargs):
        response = requests.get(headers=self.headers, *args, **kwargs)
        self.response = response

    def get_response(self, *args, **kwargs):
        self.down(*args, **kwargs)
        return self.response

    def parse_response(self,response, parse_type,parse_info):
        if parse_type == 're':
            pattern = r'{}'.format(parse_info)
            return re.findall(pattern,response.text)
        elif parse_type == 'xpath':
            tree = etree.HTML(response.text)
            return tree.xpath(parse_info)




class OutIp(object):
    def __init__(self, ip_port):
        self.ip_port = ip_port
        self.url_list = [
            {
                'url':'http://members.3322.org/dyndns/getip',
                'parse_type':'re',
                'parse_info':'\d+\.\d+\.\d+\.\d+'
            }
        ]

    def set_proxies(self,method):
        method = 'http' if method is None or method != 'https' else 'https'
        ip_port = self.ip_port.split(':')
        ip = ip_port[0]
        port = ip_port[1]
        proxyMeta = "%(method)s://%(ip)s:%(port)s" % {
            'method': method,
            "ip": ip,
            "port": port
        }
        proxies = {
            method: proxyMeta,
        }
        self.proxies = proxies

    def get_out_ip(self):
        downLoad = DownLoad()
        for url_dict in self.url_list:
            url = url_dict['url']
            method = url.split(':')[0]
            parse_type = url_dict['parse_type']
            parse_info = url_dict['parse_info']
            self.set_proxies(method)
            self.response = downLoad.get_response(url, proxies=self.proxies, timeout=10)
            return downLoad.parse_response(self.response,parse_type=parse_type, parse_info=parse_info)


if __name__ == '__main__':
    outIp = OutIp('10.20.18.100:8119')
    print(outIp.get_out_ip())



