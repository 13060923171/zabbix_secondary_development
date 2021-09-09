# coding=utf-8
import requests, json, csv, codecs, datetime, time
import pandas as pd

ApiUrl = 'http://172.22.254.50:8123/zabbix/api_jsonrpc.php'
header = {"Content-Type": "application/json"}
user = "Admin"
password = "zabbix"
x = (datetime.datetime.now() - datetime.timedelta(minutes=43200)).strftime("%Y-%m-%d %H:%M:%S")
y = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")


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


def timestamp(x, y):
    p = time.strptime(x, "%Y-%m-%d %H:%M:%S")
    starttime = str(int(time.mktime(p)))
    q = time.strptime(y, "%Y-%m-%d %H:%M:%S")
    endtime = str(int(time.mktime(q)))
    return starttime, endtime


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


def get_group_hosts(groupids,auth):
    data ={
            "jsonrpc": "2.0",
             "method": "host.get",
             "params": {
             "output": ["name"],
             "groupids": groupids,
             "filter":{
                 "status": "0"
             },
             "selectInterfaces": [
                        "ip"
                    ],
            },
            "auth": auth,  # theauth id is what auth script returns, remeber it is string
            "id": 1
        }
    gethost=requests.post(url=ApiUrl,headers=header,json=data)
    result = json.loads(gethost.content)["result"]
    host_name = []
    for r in result:
        name = r['name']
        host_name.append(name)
    return host_name

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
    hostid = result[0]['hostid']
    name = result[0]['name']
    ip = result[0]['interfaces'][0]['ip']

    return hostid,name,ip



def gethist_net(hostid, auth, timestamp,host,ip):
    list_itemid = []
    list_max = []
    list_min = []
    list_avg = []
    for j in ['icmppingloss','icmpping','icmppingsec']:
        data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": [
                    "extend",
                ],
                "search": {
                    "key_": j
                },
                "hostids": hostid
            },
            "auth": auth,
            "id": 1
        }
        getitem = requests.post(url=ApiUrl, headers=header, json=data)
        item = json.loads(getitem.content)['result']
        if len(item) > 0:
            list_itemid.append(item[0]['itemid'])

    for itemid in list_itemid:
        trendata = {
            "jsonrpc": "2.0",
            "method": "trend.get",
            "params": {
                "output": [
                    "itemid",
                    'value',
                    "clock",
                    "num",
                    "value_max",
                    "value_avg",
                    "value_min",
                ],
                "time_from": timestamp[0],
                "time_till": timestamp[1],
                "itemids": '%s' %(itemid),
                "limit": 1
            },
            "auth": auth,
            "id": 1
        }
        gettrend = requests.post(url=ApiUrl, headers=header, json=trendata)
        trend = json.loads(gettrend.content)['result']
        for i in trend:
            list_max.append(i['value_max'])
            list_min.append(i['value_min'])
            list_avg.append(i['value_avg'])
    if len(list_max) != 0 and len(list_avg) != 0 and len(list_min) != 0:
        writeexcel(host,ip,list_min,list_avg,list_max)




def writeexcel(name,ip,list_min,list_avg,list_max):
    print(name,ip,list_min,list_avg,list_max)
    df = pd.DataFrame()
    df['主机名'] = [name]
    df['IP地址'] = [ip]
    df['ICMP loss的最小值'] = ["{:.4}%".format(list_min[0])]
    df['ICMP loss的平均值'] = ["{:.4}%".format(list_avg[0])]
    df['ICMP loss的最大值'] = ["{:.4}%".format(list_max[0])]
    df['ICMP ping的最小值'] = ["{:.4}%".format(list_min[1])]
    df['ICMP ping的平均值'] = ["{:.4}%".format(list_avg[1])]
    df['ICMP ping的最大值'] = ["{:.4}%".format(list_max[1])]
    df['ICMP response time的最小值'] = ["{}".format(list_min[2])]
    df['ICMP response time的平均值'] = ["{}".format(list_avg[2])]
    df['ICMP response time的最大值'] = ["{}".format(list_max[2])]
    try:
        df.to_csv("zabbix监控项内容.csv", mode="a+", header=False,index=False, encoding="gbk")
        print("写入成功")
    except Exception as e:
        print(e)
        print('写入失败')




if __name__ == '__main__':
    token = gettoken()
    timestamp = timestamp(x, y)
    # df1 = pd.read_excel('LFL IDC-Equipment List v5 20210809.xlsx',sheet_name='IDC Device').loc[:,['Hostname']]
    # list_name = [name for name in df1['Hostname']]
    list_name = ['10.80.9.73']
    sum_list_min = []
    sum_list_avg = []
    sum_list_max = []
    sum_name = []
    sum_ip = []
    for n in list_name:
        hostid,name,ip = get_hosts(n, token)
        gethist_net(hostid, token, timestamp,name,ip)
        # sum_list_min.append(list_min)
        # sum_list_avg.append(list_avg)
        # sum_list_max.append(list_max)
        # sum_name.append(host1)
        # sum_ip.append(ip1)
    # print(sum_list_min,sum_list_avg,sum_list_max,sum_name,sum_ip)
    # # writeexcel(sum_name,sum_ip,sum_list_min,sum_list_avg,sum_list_max)
    logout(token)
