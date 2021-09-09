
# /usr/bin/env python2
# -*- coding:utf-8 -*-
## user config here
## user config end

import requests
import json
from lxml import etree
import time

ip = '172.22.254.50:8123'
user = "Admin"
password = "zabbix"
host = '172.22.254.50'


class Zabbixdata:
    def __init__(self, ip, user, password):
        self.url = 'http://' + ip + '/zabbix/api_jsonrpc.php'  # 'http://192.168.1.20/zabbix/api_jsonrpc.php'
        self.headers = {"Content-Type": "application/json",
                        }
        self.user = user
        self.password = password

    def get_time(self,itemid):
        headers = {
            "Host": host,
            "Origin": "https://" + host,
            "Referer": "https://{}/zabbix/index.php".format(host),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        }
        session = requests.session()
        session.headers = headers
        url = 'https://{}/zabbix/index.php?'.format(host)
        data = {
            "name": "Admin",
            "password": "zabbix",
            "autologin": "1",
            "enter": "登录",
        }
        list_information =[]
        list_time = []
        html = session.post(url=url, headers=headers, data=data, verify=False)
        if html.status_code == 200:
            url = "https://{}/zabbix/zabbix.php?show=1&application=&name=&inventory%5B0%5D%5Bfield%5D=type&inventory%5B0%5D%5Bvalue%5D=&evaltype=0&tags%5B0%5D%5Btag%5D=&tags%5B0%5D%5Boperator%5D=0&tags%5B0%5D%5Bvalue%5D=&show_tags=3&tag_name_format=0&tag_priority=&show_opdata=0&show_timeline=1&filter_name=&filter_show_counter=0&filter_custom_time=0&sort=clock&sortorder=DESC&age_state=0&show_suppressed=0&unacknowledged=0&compact_view=0&details=0&highlight_row=0&action=problem.view&triggerids%5B%5D={}".format(host,itemid)
            graph_req = session.get(url=url,verify=False)
            content = graph_req.text
            soup = etree.HTML(content)
            last_time = soup.xpath("//table[@class='list-table']/tbody/tr/td/text()")
            for l in range(len(last_time)):
                if 'd' and 'h' in last_time[l] or 'm' and 's' in last_time[l]:
                    if '1' in last_time[l] or '2' in last_time[l] or '3' in last_time[l] or '4' in last_time[l] or '5' in last_time[l] or '6' in last_time[l] or '7' in last_time[l] or '8' in last_time[l] or '9' in last_time[l]:
                        list_time.append(last_time[l])
            information = soup.xpath("//table[@class='list-table']/tbody/tr/td/text()")
            for i in range(len(information)):
                if "Admin (Zabbix Administrator)" in information[i]:
                    list_information.append(information[i+1])
                else:
                    list_information.append('无')
            return list_time[0],list_information[0]



