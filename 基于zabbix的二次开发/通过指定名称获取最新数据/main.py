# coding=utf-8
import requests, json, csv, codecs, datetime, time
import pandas as pd
from tqdm import tqdm
ApiUrl = 'http://172.22.254.50:8123/zabbix/api_jsonrpc.php'
header = {"Content-Type": "application/json"}
user = "Admin"
password = "zabbix"


def gettoken():
    data = {"jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": user,
                "password": password
            },
            "id": 1,
            "auth": None
            }
    auth = requests.post(url=ApiUrl, headers=header, json=data)
    return json.loads(auth.content)['result']


# 时间戳转换为日期
def timestamp_to_normal_time(timestamp, format="%Y-%m-%d"):
    timestamp = str(timestamp)
    if len(timestamp) == 13:
        timestamp_10 = int(timestamp) / 1000
    elif len(timestamp) == 10:
        timestamp_10 = int(timestamp)
    else:
        return None
    dateArray = datetime.datetime.fromtimestamp(timestamp_10)
    otherStyleTime = dateArray.strftime(format)
    return otherStyleTime

def logout(auth):
    data = {
        "jsonrpc": "2.0",
        "method": "user.logout",
        "params": [],
        "id": 1,
        "auth": auth
    }
    auth = requests.post(url=ApiUrl, headers=header, json=data)
    return json.loads(auth.content)


def get_hosts(hostname,auth):
    data = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["name"],
            "filter": {
                "ip": hostname
            },
            "selectInterfaces": [
                "ip"
            ],
        },
        "auth": auth,  # theauth id is what auth script returns, remeber it is string
        "id": 1
    }
    gethost = requests.post(url=ApiUrl, headers=header, json=data)
    result = json.loads(gethost.content)['result']
    for r in result:
        hostid = r['hostid']
        name = r['name']
        ip = r['interfaces'][0]['ip']
        return hostid,name,ip



def item_get(auth,key,hostid,name1):
    data = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": "extend",
            "hostids": hostid,
            "search": {
                "key_":key
            },
        },
        "auth": auth,  # theauth id is what auth script returns, remeber it is string
        "id": 1
    }
    list_sum = []
    gethost = requests.post(url=ApiUrl, headers=header, json=data)
    result = json.loads(gethost.content)['result']
    if len(result) != 0:
        for r in result:
            d = {}
            name = r['name']
            lastclock = r['lastclock']
            lastclock = timestamp_to_normal_time(lastclock, format='%Y-%m-%d %H:%M:%S')
            lastvalue = r['lastvalue']
            units = r['units']
            value = lastvalue + units
            d['host_name'] = name1
            d['name'] = name
            d['last_time'] = lastclock
            d['value'] = value
            list_sum.append(d)
        return list_sum



if __name__ == '__main__':
    token = gettoken()
    # list_name = ['10.80.9.73','10.80.9.73']
    host_name = []
    list_name1 = []
    last_time = []
    list_value = []
    df2 = pd.read_excel('LFL IDC-Equipment List v5 20210809.xlsx',sheet_name='IDC Device')
    list_name = [str(ip) for ip in df2['Device Mgmt IP']]
    del list_name[24]

    n =0
    for l in list_name:
        n += 1
        print(l)
        print(n)
    # for n in tqdm(list_name):
    #     hostid,name,ip = get_hosts(n, token)
    #     list_sum = item_get(token,'ICMP',hostid,name)
    #     for l in list_sum:
    #         host_name.append(l['host_name'])
    #         list_name1.append(l['name'])
    #         last_time.append(l['last_time'])
    #         list_value.append(l['value'])
    # df1 = pd.DataFrame()
    # df1['主机'] = host_name
    # df1['名称'] = list_name1
    # df1['最新时间'] = last_time
    # df1['最新数据'] = list_value
    # df1.to_csv('ICMP最新数据获取.csv',encoding='gbk')

    logout(token)
