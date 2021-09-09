
# /usr/bin/env python3
# -*- coding:utf-8 -*-
## user config here
## user config end

import requests
import json
import os
import pandas as pd
from tqdm import tqdm

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

    def host_create(self,hostname,address,hostip,hostGroupName,templateName):
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
        if  len(find_hostname.get('result')):
            print("###recheck### hostname[%s] exists and return"%hostname)
            return 1

        # 判断template是否存才，不存在退出。 否则初始化备用
        template_list = []
        for t in templateName.split(','):
            find_template = self.template_get(t)
            if not len(find_template.get('result')):
                # template不存在退出 # 一般因为输错关系
                print("###recheck### template[%s] not find and return " %t)
                return 1

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
                "description":address,
                "interfaces": [
                    {
                        "type": 2,  # 1：表示IP；2表示SNMP
                        "main": 1,
                        "useip": 1,
                        "ip": hostip,
                        "dns": "",
                        "port": "161",  # IP端口10051；SNMP端口161
                        "details": {
                            "version": 2,
                            "bulk":1,
                            "community": "{$SNMP_COMMUNITY}",
                        }
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




def comment():
    df = pd.read_excel('LFL China DC List ver4.xlsx', sheet_name='DC Name').loc[1:35,['Unnamed: 1','Unnamed: 2','Unnamed: 3','Unnamed: 4','TCP','Unnamed: 6']]
    df.dropna(axis=0,how='any',inplace=True)
    df1 = pd.read_excel('LFL China DC List ver4.xlsx', sheet_name='DC Name').loc[1:35,['Unnamed: 1', 'Unnamed: 2','Unnamed: 3','Unnamed: 4','TCE', 'Unnamed: 11']]
    df1.dropna(axis=0, how='any', inplace=True)
    list_hostname = []
    list_hostip = []
    list_groupname = []
    list_template = []
    list_address = []
    list_tcp = [t for t in df['TCP']]
    list_tce = [t for t in df1['TCE']]
    list_tcp_ip = [t for t in df['Unnamed: 6']]
    list_tce_ip = [t for t in df1['Unnamed: 11']]
    list_1 = [t for t in df['Unnamed: 1']]
    list_2 = [t for t in df1['Unnamed: 1']]
    list_addrees_1 = [t for t in df['Unnamed: 2']]
    list_addrees_2 = [t for t in df1['Unnamed: 2']]
    list_contact_1 = [c for c in df['Unnamed: 3']]
    list_contact_2 = [c for c in df1['Unnamed: 3']]
    list_phone_1 = [p for p in df['Unnamed: 4']]
    list_phone_2 = [p for p in df1['Unnamed: 4']]
    for i in range(len(list_tcp)):
        list_1[i] = list_1[i].replace('LFL',' ').replace('LFT',' ').replace('BLP',' ').replace('拆除',' ').replace('CCL',' ')\
            .replace('Baoshan DC-ITX/Baoshan DC','Baoshan DC-ITX').replace(' - ','-').strip(' ')
        hostname = 'SHA-MAN-CPCN-{}-TCP-{}'.format(list_1[i],list_tcp[i])
        template = 'Templates-LFL-CPCNet-L3 SNMP'
        gruopname = 'DC CPCNet Group'
        address = '{}\n {}\n {}\n'.format(list_addrees_1[i],list_contact_1[i],list_phone_1[i])
        list_hostname.append(hostname)
        list_hostip.append(list_tcp_ip[i])
        list_groupname.append(gruopname)
        list_template.append(template)
        list_address.append(address)


    df2 = pd.DataFrame()
    df2['name'] = list_hostname
    df2['address'] = list_address
    df2['ip'] = list_hostip
    df2['group'] = list_groupname
    df2['template'] = list_template


    list_hostname1 = []
    list_hostip1 = []
    list_groupname1 = []
    list_template1 = []
    list_address1 = []
    for i in range(len(list_tce)):
        list_2[i] = list_2[i].replace('LFL',' ').replace('LFT',' ').replace('BLP',' ').replace('拆除',' ').replace('CCL',' ')\
            .replace('Baoshan DC-ITX/Baoshan DC','Baoshan DC-ITX').replace(' - ','-').strip(' ')
        hostname = 'SHA-MAN-CPCN-{}-TCE-{}'.format(list_2[i],list_tce[i])
        template = 'Templates-LFL-CPCNet-L3 SNMP'
        gruopname = 'DC CPCNet Group'
        address = '{}\n {}\n {}\n'.format(list_addrees_2[i], list_contact_2[i], list_phone_2[i])
        list_hostname1.append(hostname)
        list_hostip1.append(list_tce_ip[i])
        list_groupname1.append(gruopname)
        list_template1.append(template)
        list_address1.append(address)

    df3 = pd.DataFrame()
    df3['name'] = list_hostname1
    df3['address'] = list_address1
    df3['ip'] = list_hostip1
    df3['group'] = list_groupname1
    df3['template'] = list_template1
    return df2,df3

if __name__ == '__main__':

        comment()
        zabbix = ZabbixApi(ip, user, password)
        print("...login success...")
        # # 添加主机单台
        zabbix.host_create('host16','','10.80.5.150','Cus_A.S.W - ASWI-DG','Templates-ASWI-GZ-Cisco L3 SNMP')
        # #批量添加主机，从表格中读取数据再对数据进行处理，使得数据可以正确读取
        # df1,df2 = comment()
        # for i in tqdm(range(len(df1['name']))):
        #     zabbix.host_create(df1['name'][i],df1['address'][i],df1['ip'][i],df1['group'][i],df1['template'][i])
        # for i in tqdm(range(len(df2['name']))):
        #     zabbix.host_create(df2['name'][i],df2['address'][i],df2['ip'][i],df2['group'][i],df2['template'][i])
        # print('添加完毕')