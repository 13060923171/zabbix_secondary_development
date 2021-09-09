
# /usr/bin/env python3
# -*- coding:utf-8 -*-
## user config here
## user config end

import requests
import json
import os
import pandas as pd
from tqdm import tqdm

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
            return response.json()   # len(ret.get('result'))为1时获取到，否则未获取到。
        except Exception as e:
            print("\033[0;31;0m HOST GET ERROR\033[0m")
            raise Exception

    def hostgroup_get(self,hostGroupName=''):
        '''
        获取主机组
        :param hostGroupName:
        :return: {'jsonrpc': '2.0', 'result': [{'groupid': '15', 'name': 'linux group 1', 'internal': '0', 'flags': '0'}], 'id': 1}
        '''
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": hostGroupName
                }
            },
            "auth": self.auth,
            "id": 1,
            })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
            # hosts_count=len(response.json().get('result',''))
            # print('l',hosts)
            return response.json()   # len(ret.get('result'))为1时获取到，否则未获取到。

        except Exception as e:
            print("\033[0;31;0m HOSTGROUP GET ERROR\033[0m")
            raise Exception

    def hostgroup_create(self,hostGroupName=''):
        if len(self.hostgroup_get(hostGroupName).get('result'))==1:
            print("无需创建，hostgroup存在")
            return 100
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "hostgroup.create",
            "params": {
                "name": hostGroupName
            },
            "auth": self.auth,
            "id": 1
            })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
            # hosts_count=len(response.json().get('result',''))
            # print('l',hosts)
            return response.json()   # len(ret.get('result'))为1时获取到，否则未获取到。

        except Exception as e:
            print("\033[0;31;0m HOSTGROUP CREATE ERROR\033[0m")
            raise Exception

    def template_get(self,templateName=''):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": templateName
                }
            },
            "auth": self.auth,
            "id": 50,
            })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
            # hosts_count=len(response.json().get('result',''))
            # print('l',hosts)
            return response.json()   # len(ret.get('result'))为1时获取到，否则未获取到。

        except Exception as e:
            print("\033[0;31;0m Template GET ERROR\033[0m")
            raise Exception

    def host_create(self,hostname,hostip,hostGroupName,templateName,tag_key,tag_value):
        '''
        创建host，并分配分组，关联模版
        host_create('host3','1.1.1.1','gp1 test,gp2 test','Template App FTP Service,Template App HTTP Service')
        :param hostname: 'host3'
        :param hostip: '1.1.1.1'
        :param hostGroupName: 多个组逗号分割'gp1 test,gp2 test'
        :param templateName: 多个模版都逗号分割'Template App FTP Service,Template App HTTP Service'
        :return:
        '''
        # 判断主机名是否重复。 zabbix不允许主机名重复
        find_hostname=self.host_get(hostname)
        if len(find_hostname.get('result')):
            print("###recheck### hostname[%s] exists and return"%hostname)

        # 判断template是否存才，不存在退出。 否则初始化备用
        template_list = []
        for t in templateName.split(','):
            find_template = self.template_get(t)
            if not len(find_template.get('result')):
                # template不存在退出 # 一般因为输错关系
                print("###recheck### template[%s] not find and return " %t)

            tid=self.template_get(t).get('result')[0]['templateid']
            template_list.append({'templateid':tid})

        # 判断hostgroup是否存在。 不存在则创建。 并初始化hostgroup_list备用
        hostgroup_list=[]
        for g in hostGroupName.split(','):
            find_hostgroupname = self.hostgroup_get(g)
            if not len(find_hostgroupname.get('result')):
                self.hostgroup_create(g)
            gid = self.hostgroup_get(g).get('result')[0]['groupid']
            hostgroup_list.append({'groupid':gid})
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": hostname,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": hostip,
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "tags": [
                    {
                        "tag":tag_key,
                        "value":tag_value,
                    }
                ],
                "groups": hostgroup_list,
                "templates": template_list,
            },
            "auth": self.auth,
            "id": 1
        })
        try:
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=2)
            coment = response.json()
            id = coment['result']['hostids']
            if len(id) > 0:
                print("执行返回信息： 添加HOST[%s,%s]完成"%(hostname,hostip))
            else:
                print("执行返回信息： 添加HOST[%s,%s]失败" % (hostname, hostip))


        except Exception as e:
            print("\033[0;31;0m HOST CREATE ERROR\033[0m")
            print("执行返回信息： 添加HOST[%s,%s]失败" % (hostname, hostip))
            raise Exception






if __name__ == '__main__':
    try:
        zabbix = ZabbixApi(ip, user, password)
        print("...login success...")
        df = pd.read_excel('写入文档.xlsx').loc[:,['name','ip','group','templates','tags_key','tags_value']]
        print(df)
        # for i in tqdm(range(len(df['name']))):
        #     zabbix.host_create(df['name'][i],df['ip'][i],df['group'][i],df['template'][i],df['tags_key'][i],df['tags_value'][i])

    except Exception as e:
        print(e)
