# -*- coding:utf-8 -*-

import requests
import json
import os
import pandas as pd

ip = '172.22.254.50:8123'
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
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.user,
                "password": self.password
            },
            "id": 10,
        })
        try:
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=2)
            auth = response.json().get('result', '')
            return auth
        except Exception as e:
            print("\033[0;31;0m Login error check: IP,USER,PASSWORD\033[0m")
            raise Exception

    def hostgroup_get(self,group):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": [
                        group,
                    ]
                }
            },
            "auth": self.auth,
            "id": 1
        })
        try:
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=2)
            response = response.json()
            groupid = response['result']
            if len(groupid) != 0:
                groupid = groupid[0]['groupid']
                return groupid
        except Exception as e:
            print("\033[0;31;0m Login error check: IP,USER,PASSWORD\033[0m")
            raise Exception

    def host_get(self,groupids):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": "extend",
                "groupids": groupids
            },
            "auth": self.auth,
            "id": 1
        })
        try:
            list_id = []
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=2)
            response = response.json()
            hostids = response['result']
            if len(hostids) != 0:
                for h in hostids:
                    id = h['hostid']
                    list_id.append(id)
            return list_id

        except Exception as e:
            print("\033[0;31;0m Login error check: IP,USER,PASSWORD\033[0m")
            raise Exception


    def host_updata(self,ids,list_data):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": ids,
                "inventory_mode": 0,
                "inventory": {
                    "location": "{}".format(list_data[0]),
                    "contract_number":"{}".format(list_data[-1]),
                    "contact":"{}{}".format(list_data[1].replace('-',''),list_data[2].replace('-','')),
                }
            },
            "auth": self.auth,
            "id": 1
        })
        try:
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=2)
            response = response.json()
            response = response['result']
            if len(response) != 0:
                return 'hostid:{}资产记录更新完毕'.format(response['hostids'])
        except Exception as e:
            print("\033[0;31;0m Login error check: IP,USER,PASSWORD\033[0m")
            raise Exception

if __name__ == '__main__':
    try:
        zabbix = ZabbixApi(ip, user, password)
        print("...login success...")
        df = pd.read_excel('LFL China DC List ver9.xlsx',sheet_name='DC_address_contact').loc[:,["DC Name","DC Address","Onsite support","Remote support","Phone"]]
        list_address = [str(a) for a in df['DC Address']]
        list_onsite = [str(o) for o in df['Onsite support']]
        list_remote = [str(r) for r in df['Remote support']]
        list_phone = [str(p) for p in df['Phone']]
        list_data = []
        for j in range(len(list_address)):
            list_data1 = [list_address[j],list_onsite[j],list_remote[j],list_phone[j]]
            list_data.append(list_data1)

        a = zabbix.hostgroup_get('Cus_A.S.W - WTCCN-Core-BJIDC')
        b = zabbix.host_get(a)
        for i in b:
            c = zabbix.host_updata(i, list_data[0])
            print(c)


    except Exception as e:
        print(e)
