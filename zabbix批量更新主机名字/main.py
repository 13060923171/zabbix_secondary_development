
# /usr/bin/env python3
# -*- coding:utf-8 -*-
## user config here
## user config end

import requests
import json
import os
import pandas as pd
import openpyxl
from openpyxl import load_workbook

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

    def host_get(self, hostip):
        '''
        获取主机。不输入hostname 则获取所有
        :param hostName: zabbix主机名不允许重复。（IP允许重复）。#host_get(hostname='gateway1')
        :return: {'jsonrpc': '2.0', 'result': [], 'id': 21}
        :return: {'jsonrpc': '2.0', 'result': [{'hostid': '10277', ... , 'host': 'gateway', ...}], 'id': 21}
        '''
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {"output": "extend",
                       "filter": {"ip": hostip},
                       },
            "id": 21,
            "auth": self.auth
        })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
            return response.json()   # len(ret.get('result'))为1时获取到，否则未获取到。
        except Exception as e:
            print("\033[0;31;0m HOST GET ERROR\033[0m")
            raise Exception

    def host_update(self,hostid,newname):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid":hostid,
                "host":newname,
                "name":newname
            },
            "id": 21,
            "auth": self.auth
        })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
            return response.json()   # len(ret.get('result'))为1时获取到，否则未获取到。
        except Exception as e:
            print("\033[0;31;0m HOST GET ERROR\033[0m")
            raise Exception

    def write_excel(self):
        df = pd.read_excel('LF月浦AP IP地址表.xlsx').loc[:, ['IP', 'AP']]
        list_ip = [str(i) for i in df['IP']]
        list_ap = [str(a) for a in df['AP']]

        return list_ip, list_ap

if __name__ == '__main__':
    try:
        zabbix = ZabbixApi(ip, user, password)
        print("...login success...")
        list_ip, list_ap = zabbix.write_excel()
        for l in range(len(list_ip)):

            hostid = zabbix.host_get(list_ip[l])['result']
            if len(hostid) >0:
                hostid = hostid[0]['hostid']
                updata = zabbix.host_update(hostid, list_ap[l])
                print(l, updata)

        print('更新完毕')



    except Exception as e:
        print(e)
