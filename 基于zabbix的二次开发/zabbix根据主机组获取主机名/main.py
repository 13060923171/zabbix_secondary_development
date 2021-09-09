
# /usr/bin/env python3
# -*- coding:utf-8 -*-
## user config here
## user config end

import requests
import json
import pandas as pd


ip = '172.22.254.8:8123'
user = "Admin"
password = "zabbix"


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

    def host_get(self,groupname):
        '''
        获取主机。不输入hostname 则获取所有
        :param hostName: zabbix主机名不允许重复。（IP允许重复）。#host_get(hostname='gateway1')
        :return: {'jsonrpc': '2.0', 'result': [], 'id': 21}
        :return: {'jsonrpc': '2.0', 'result': [{'hostid': '10277', ... , 'host': 'gateway', ...}], 'id': 21}
        '''
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "filter": {
                    "host": [
                        groupname,
                    ]
                }
            },
            "id": 21,
            "auth": self.auth
        })

        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
            result = response.json()['result']
            for r in result:
                host = r['name']

                return host,groupname
        except Exception as e:
            print("\033[0;31;0m HOST GET ERROR\033[0m")
            raise Exception



if __name__ == '__main__':
    try:
        zabbix = ZabbixApi(ip, user, password)
        print("...login success...")
        name = ['LFL_DC-SH-BaoShan-Network-RT','LFL_DC-GD-Huizhou-Network-RT','LFL_DC-GD-Yantian-Network-RT','LFL_DC-GD-Mast-Network-RT','LFL_DC-HB-WuHan HB03-Network-RT','CPCNet_DC-Hub-CPCN WAN-RT']
        list_name = []
        list_group_name = []
        for n in name:
            host,groupname = zabbix.host_get(n)
            list_name.append(host)
            list_group_name.append(groupname)
        df1 = pd.DataFrame()
        df1['主机组'] = list_group_name
        df1['主机名'] = list_name
        df1.to_csv('主机群组列表.csv',encoding='gbk')


    except Exception as e:
        print(e)
