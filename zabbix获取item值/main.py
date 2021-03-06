# coding=utf-8
import requests, json, csv, codecs, datetime, time
import pandas as pd

ApiUrl = 'http://172.22.254.8/zabbix/api_jsonrpc.php'
header = {"Content-Type": "application/json"}
user = "Admin"
password = "zabbix"
x = (datetime.datetime.now() - datetime.timedelta(minutes=120)).strftime("%Y-%m-%d %H:%M:%S")
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
                "host": hostname
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
    try:
        hostid = result[0]['hostid']
    except:
        hostid = ''
    try:
        name = result[0]['name']

    except:
        name = ''
    try:
        ip = result[0]['interfaces'][0]['ip']
    except:
        ip = ''
    return hostid,name,ip



def gethist_net(hostid, auth, timestamp):
    list_itemid = []
    item1 = []
    for j in ['net.if.in','net.if.in','system.cpu.util','icmppingsec']:
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
        if len(trend) > 0:
            item1.append(trend)
    list_max = []
    list_min = []
    list_avg = []
    for i in item1:
        list_max.append(i[0]['value_max'])
        list_min.append(i[0]['value_min'])
        list_avg.append(i[0]['value_avg'])

    return list_max,list_min,list_avg




def writeexcel(name,ip,list_min,list_avg,list_max):
    df = pd.DataFrame()
    df['?????????'] = [str(n) for n in name]
    df['IP??????'] = [str(i) for i in ip]

    try:
        df['in????????????'] = [min[0] for min in list_min]
    except:
        df['in????????????'] = ['???']
    try:
        df['in????????????'] = [max[0] for max in list_max]
    except:
        df['in????????????'] = ['???']
    try:
        df['in?????????'] = [avg[0] for avg in list_avg]
    except:
        df['in?????????'] = ['???']
    try:
        df['out????????????'] = [min[1] for min in list_min]
    except:
        df['out????????????'] = ['???']
    try:
        df['out????????????'] = [max[1] for max in list_max]
    except:
        df['out????????????'] = ['???']
    try:
        df['out?????????'] = [avg[1] for avg in list_avg]
    except:
        df['out?????????'] = ['???']
    try:
        df['cpu?????????????????????'] = ['{}%'.format(min[2]) for min in list_min]
    except:
        df['cpu?????????????????????'] = ['???']
    try:
        df['cpu?????????????????????'] = ['{}%'.format(max[2]) for max in list_max]
    except:
        df['cpu?????????????????????'] = ['???']
    try:
        df['cpu??????????????????'] = ['{}%'.format(avg[2]) for avg in list_avg]
    except:
        df['cpu??????????????????'] = ['???']
    try:
        df['ping????????????????????????'] = ['{:.3}??????'.format(eval(min[3]) * 60 * 60) for min in list_min]
    except:
        df['ping????????????????????????'] = ['???']
    try:
        df['ping????????????????????????'] = ['{:.3}??????'.format(eval(max[3]) * 60 * 60) for max in list_max]
    except:
        df['ping????????????????????????'] = ['???']
    try:
        df['ping?????????????????????'] = ['{:.3}??????'.format(eval(avg[3]) * 60 * 60) for avg in list_avg]
    except:
        df['ping?????????????????????'] = ['???']
    cols = ['?????????','IP??????','in????????????','in????????????','in?????????','out????????????','out????????????','out?????????','cpu?????????????????????','cpu?????????????????????','cpu??????????????????','ping????????????????????????','ping????????????????????????','ping?????????????????????']
    try:
        df.to_csv("zabbix???????????????.csv", mode="w", header=True,index=False, encoding="gbk")
        print("????????????")
    except Exception as e:
        print(e)
        print('????????????')




if __name__ == '__main__':
    token = gettoken()
    timestamp = timestamp(x, y)
    # gethost = get_group_hosts(20, token)
    # name = ['G39092-04217-ShH','G39092-10096-ShH','20105_38721-02_GuZ']
    name = ['G39092-04217-ShH']
    sum_list_min = []
    sum_list_avg = []
    sum_list_max = []
    sum_name = []
    sum_ip = []
    for n in name:
        hostid,name,ip = get_hosts(n, token)
        sum_name.append(name)
        sum_ip.append(ip)
        list_max, list_min, list_avg = gethist_net(hostid, token, timestamp)
    #     sum_list_min.append(list_min)
    #     sum_list_avg.append(list_avg)
    #     sum_list_max.append(list_max)
    #
    # writeexcel(sum_name,sum_ip,sum_list_min,sum_list_avg,sum_list_max)
    # logout(token)
