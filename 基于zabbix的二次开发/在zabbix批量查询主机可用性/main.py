import requests
import json
import os
import pandas as pd
from tqdm import tqdm
import re

ip = '172.16.242.13'
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

    def host_get(self, hostname=''):
        '''
        获取主机。不输入hostname 则获取所有
        :param hostName: zabbix主机名不允许重复。（IP允许重复）。#host_get(hostname='gateway1')
        :return: {'jsonrpc': '2.0', 'result': [], 'id': 21}
        :return: {'jsonrpc': '2.0', 'result': [{'hostid': '10277', ... , 'host': 'gateway', ...}], 'id': 21}
        '''
        if hostname == '':
            # print("no hostname and find all host")
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": [
                        "hostid",
                        "host"
                    ],
                    "selectInterfaces": [
                        "interfaceid",
                        "ip"
                    ]
                },
                "id": 20,
                "auth": self.auth
            })
        else:
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {"output": "extend",
                           "filter": {"host": hostname},
                           },
                "id": 21,
                "auth": self.auth
            })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
            # hosts_count=len(response.json().get('result',''))
            # print('l',hosts)
            return response.text  # len(ret.get('result'))为1时获取到，否则未获取到。
        except Exception as e:
            print("\033[0;31;0m HOST GET ERROR\033[0m")
            raise Exception

    def host_error(self, hostname,ip):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "filter": {
                        "host": [
                            hostname,
                        ]
                    }
                },
                "auth": self.auth,
                "id": 1
            }
        )
        list_name = []
        list_ip = []
        list_error = []
        try:
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=2)
            coment = response.json()
            error = coment['result'][0]['snmp_error']
            # if len(error) > 0:
            list_error.append(error)
            list_name.append(hostname)
            list_ip.append(ip)
            return list_name, list_error,list_ip
        except Exception as e:
            raise Exception


if __name__ == '__main__':
    zabbix = ZabbixApi(ip, user, password)
    print("...login success...")
    # df1 = pd.read_excel('LFL China Equipment List.20210423 - 副本.xls', sheet_name='Network List').loc[:,
    #       ['City', 'DC Name', 'Device Type', 'Hostname', 'IP']]
    df1 = pd.read_excel('没有Hostname AP.xlsx').loc[:,['Hostname','IP']]
    list_hostname = [h for h in df1['Hostname']]
    list_ip = [i for i in df1['IP']]
    list_name = []
    list_host_ip = []
    list_error = []
    for i in range(len(list_hostname)):
        # a, b = zabbix.host_error(i.strip(' ').replace('#', '').replace('(', '-').replace(')', '').replace(' ', ''))
        a, b,c = zabbix.host_error(list_hostname[i],list_ip[i])
        # if len(a) > 0 and len(b) > 0:
        list_name.append(a[0])
        list_error.append(b[0])
        list_host_ip.append(c[0])
    df = pd.DataFrame()
    df['设备名'] = list_name
    df['ip'] = list_host_ip
    df['报错信息'] = list_error

    df.to_excel('设备列表.xlsx')
