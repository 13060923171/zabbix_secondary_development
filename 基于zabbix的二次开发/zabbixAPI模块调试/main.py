
# /usr/bin/env python2
# -*- coding:utf-8 -*-
## user config here
## user config end

import requests
import json
from lxml import etree
import time
from main1 import Zabbixdata


ip = '172.22.254.50:8123'
user = "Admin"
password = "zabbix"
host = '172.22.254.50'


class ZabbixApi:
    def __init__(self, ip, user, password):
        self.url = 'http://' + ip + '/zabbix/api_jsonrpc.php'  # 'http://192.168.1.20/zabbix/api_jsonrpc.php'
        self.headers = {"Content-Type": "application/json",
                        }
        self.user = user
        self.password = password
        self.auth = self.__login()

    def __login(self):
        '''
        zabbix登陆获取auth
        :return: auth  #  样例bdc64373690ab9660982e0bafe1967dd
        '''
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.user,
                "password": self.password
            },
            "id": 10,
            # "auth": 'none'
        })
        try:
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=2)
            # {"jsonrpc":"2.0","result":"bdc64373690ab9660982e0bafe1967dd","id":10}
            auth = response.json().get('result', '')
            return auth
        except Exception as e:
            print("\033[0;31;0m Login error check: IP,USER,PASSWORD\033[0m")
            raise Exception

    def get_host_group(self,itemid):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "trigger.get",
            "params": {
                "triggerids": itemid,
                 "output": "extend",
                "sortfield":'status',
                "sortorder": 'DESC',
                "selectDependencies":"extend",
                # "only_true": '1',  # 仅返回最近处于故障状态的触发器
                # "active": '1',  # 仅返回所属被监控主机的已启用触发器
                "withUnacknowledgedEvents": '1',
                "expandDescription": '1',
                "selectFunctions": "extend",
                "selectHosts": ['name'],  # 返回所属主机信息
                "selectGroups":['name']

            },
            "auth":self.auth,
            "id": 1
        })


        response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
        result = response.json()
        result = result['result']
        if len(result) >=0:
            host = result[0]['hosts'][0]['name']
            group = result[0]['groups'][0]['name']
            return host,group



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




if __name__ == '__main__':
    try:
        zabbix = ZabbixApi(ip, user, password)
        zabbix2 = Zabbixdata(ip, user, password)
        print("...login success...")
        list_riggerids = [19304]
        for l in list_riggerids:
            host, group = zabbix.get_host_group(l)
            time, information = zabbix2.get_time(l)
            print('主机:{} \n主机组:{} \n持续时间:{} \n跟进情况:{}\n'.format(host,group,time,information))



    except Exception as e:
        print(e)
