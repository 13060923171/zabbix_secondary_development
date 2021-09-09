import requests
import json
import os
import re

ip = '172.22.254.8'
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
            "id": 1,
        })
        try:
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=2)
            auth = response.json().get('result', '')
            return auth
        except Exception as e:
            print("\033[0;31;0m Login error check: IP,USER,PASSWORD\033[0m")
            raise Exception

    def host_get(self, hostname=''):
        if hostname == '':
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
            list_ids = []
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
            counts = len(response.json().get('result', ''))
            for c in range(counts):
                h = response.json().get('result', '')
                ids = h[c]['hostid']
                list_ids.append(ids)
            return list_ids  # len(ret.get('result'))为1时获取到，否则未获取到。
        except Exception as e:
            print("\033[0;31;0m HOST GET ERROR\033[0m")
            raise Exception

    def item_get(self):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": "extend",
                "countOutput": True,
                "monitored": True,
                # "filter": {
                #     "type": "12"
                # },
                # "active":'',
                # "searchWildcardsEnabled":True,
                # "searchByAny": True,
                # "search": {
                #     "status_codes": "*"
                # },
                "selectTriggers":"extend",
                # "templated":False,
                "webitems":'',
            },
            "auth": self.auth,
            "id": 1
        })
        try:
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=2)
            item = response.json()
            print(item)
        except Exception as e:
            print("\033[0;31;0m Login error check: IP,USER,PASSWORD\033[0m")
            raise Exception




if __name__ == '__main__':
    zabbix = ZabbixApi(ip,user,password)
    z = zabbix.item_get()
