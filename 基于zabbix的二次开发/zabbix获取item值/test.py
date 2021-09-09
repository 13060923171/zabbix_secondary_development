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

def gethist(hostid,name, auth, timestamp):
    list_itemid = []
    item1 = []
    data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": [
                    "extend",
                ],
                "search": {
                    "name":name
                },

                "hostids": hostid
            },
            "auth": auth,
            "id": 1
        }
    getitem = requests.post(url=ApiUrl, headers=header, json=data)
    item = json.loads(getitem.content)['result']
    if len(item) > 0:
        for i in item:
            list_itemid.append(i['itemid'])
    list_max = []
    list_min = []
    list_avg = []
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
            max1 = trend[0]['value_max']
            list_max.append(max1)
            min1 = trend[0]['value_min']
            list_min.append(min1)
            avg = trend[0]['value_avg']
            list_avg.append(avg)
    return list_max, list_min, list_avg




def writeexcel_net(name,ip,list_max,list_min,list_avg):
    df = pd.DataFrame()
    df['主机名'] = [str(n) for n in name]
    df['IP地址'] = [str(i) for i in ip]
    try:
        df['in的最小值'] = ['{:.3}MB'.format(eval(min[0]) / 1024 / 1024) for min in list_min]
    except:
        df['in的最小值'] = ['无']
    try:
        df['in的均值'] = ['{:.3}MB'.format(eval(avg[0]) / 1024 / 1024) for avg in list_avg]
    except:
        df['in的均值'] = ['无']
    try:
        df['in的最大值'] = ['{:.3}MB'.format(eval(max[0]) / 1024 / 1024) for max in list_max]
    except:
        df['in的最大值'] = ['无']
    try:
        df['out的最小值'] = ['{:.3}MB'.format(eval(min[1]) / 1024 / 1024) for min in list_min]
    except:
        df['out的最小值'] = ['无']
    try:
        df['out的均值'] = ['{:.3}MB'.format(eval(avg[1]) / 1024 / 1024) for avg in list_avg]
    except:
        df['out的均值'] = ['无']
    try:
        df['out的最大值'] = ['{:.3}MB'.format(eval(max[1]) / 1024 / 1024) for max in list_max]
    except:
        df['out的最大值'] = ['无']
    try:
        df.to_csv("zabbix监控项Interface内容.csv", mode="w", header=True,index=False, encoding="gbk")
        print("写入成功")
    except Exception as e:
        print(e)
        print('写入失败')

def writeexcel_cpu(name,ip,list_max,list_min,list_avg):
    df = pd.DataFrame()
    df['主机名'] = [str(n) for n in name]
    df['IP地址'] = [str(i) for i in ip]
    try:
        df['cpu使用率的最小值'] = ['{}%'.format(min[0]) for min in list_min]
    except:
        df['cpu使用率的最小值'] = ['无']
    try:
        df['cpu使用率的均值'] = ['{}%'.format(avg[0]) for avg in list_avg]
    except:
        df['cpu使用率的均值'] = ['无']
    try:
        df['cpu使用率的最大值'] = ['{}%'.format(max[0]) for max in list_max]
    except:
        df['cpu使用率的最大值'] = ['无']

    try:
        df.to_csv("zabbix监控项cpu内容.csv", mode="w", header=True,index=False, encoding="gbk")
        print("写入成功")
    except Exception as e:
        print(e)
        print('写入失败')

def writeexcel_Memory(name,ip,list_max,list_min,list_avg):
    df = pd.DataFrame()
    df['主机名'] = [str(n) for n in name]
    df['IP地址'] = [str(i) for i in ip]
    try:
        df['processor:free memory的最小值'] = ['{:.3}MB'.format(eval(min[0]) / 1024 / 1024) for min in list_min]
    except:
        df['processor:free memory的最小值'] = ['无']
    try:
        df['processor:free memory的均值'] = ['{:.3}MB'.format(eval(avg[0]) / 1024 / 1024) for avg in list_avg]
    except:
        df['processor:free memory的均值'] = ['无']
    try:
        df['processor:free memory的最大值'] = ['{:.3}MB'.format(eval(max[0]) / 1024 / 1024) for max in list_max]
    except:
        df['processor:free memory的最大值'] = ['无']

    try:
        df['I/O:free memory的最小值'] = ['{:.3}MB'.format(eval(min[1]) / 1024 / 1024) for min in list_min]
    except:
        df['I/O:free memory的最小值'] = ['无']
    try:
        df['I/O:free memory的均值'] = ['{:.3}MB'.format(eval(avg[1]) / 1024 / 1024) for avg in list_avg]
    except:
        df['I/O:free memory的均值'] = ['无']
    try:
        df['I/O:free memory的最大值'] = ['{:.3}MB'.format(eval(max[1]) / 1024 / 1024) for max in list_max]
    except:
        df['I/O:free memory的最大值'] = ['无']

    try:
        df['Processor:Used memory的最小值'] = ['{:.3}MB'.format(eval(min[2]) / 1024 / 1024) for min in list_min]
    except:
        df['Processor:Used memory的最小值'] = ['无']
    try:
        df['Processor:Used memory的均值'] = ['{:.3}MB'.format(eval(avg[3]) / 1024 / 1024) for avg in list_avg]
    except:
        df['Processor:Used memory的均值'] = ['无']
    try:
        df['Processor:Used memory的最大值'] = ['{:.3}MB'.format(eval(max[2]) / 1024 / 1024) for max in list_max]
    except:
        df['Processor:Used memory的最大值'] = ['无']

    try:
        df['I/O:Used memory的最小值'] = ['{:.3}MB'.format(eval(min[3]) / 1024 / 1024) for min in list_min]
    except:
        df['I/O:Used memory的最小值'] = ['无']
    try:
        df['I/O:Used memory的均值'] = ['{:.3}MB'.format(eval(avg[3]) / 1024 / 1024) for avg in list_avg]
    except:
        df['I/O:Used memory的均值'] = ['无']
    try:
        df['I/O:Used memory的最大值'] = ['{:.3}MB'.format(eval(max[3]) / 1024 / 1024) for max in list_max]
    except:
        df['I/O:Used memory的最大值'] = ['无']

    try:
        df['Processor:Memory utilization的最小值'] = ['{:.3}%'.format(eval(min[4])) for min in list_min]
    except:
        df['Processor:Memory utilization的最小值'] = ['无']
    try:
        df['Processor:Memory utilization的均值'] = ['{:.3}%'.format(eval(avg[4])) for avg in list_avg]
    except:
        df['Processor:Memory utilization的均值'] = ['无']
    try:
        df['Processor:Memory utilization的最大值'] = ['{:.3}%'.format(eval(max[4])) for max in list_max]
    except:
        df['Processor:Memory utilization的最大值'] = ['无']

    try:
        df['I/O:Memory utilization的最小值'] = ['{:.3}%'.format(eval(min[5])) for min in list_min]
    except:
        df['I/O:Memory utilization的最小值'] = ['无']
    try:
        df['I/O:Memory utilization的均值'] = ['{:.3}%'.format(eval(avg[5])) for avg in list_avg]
    except:
        df['I/O:Memory utilization的均值'] = ['无']
    try:
        df['I/O:Memory utilization的最大值'] = ['{:.3}%'.format(eval(max[5])) for max in list_max]
    except:
        df['I/O:Memory utilization的最大值'] = ['无']

    try:
        df.to_csv("zabbix监控项memory内容.csv", mode="w", header=True,index=False, encoding="gbk")
        print("写入成功")
    except Exception as e:
        print(e)
        print('写入失败')






if __name__ == '__main__':
    token = gettoken()
    timestamp = timestamp(x, y)
    df1 = pd.read_excel('模板.xlsx').loc[:,['主机名','监控项名称']]
    list_hostname = [str(n) for n in df1['主机名']]
    list_itemname = [str(i) for i in df1['监控项名称']]
    sum_cpu_name = []
    sum_cpu_ip = []
    sum_cpu_min = []
    sum_cpu_max = []
    sum_cpu_avg = []
    for i in range(len(list_hostname)):
        hostid,name,ip = get_hosts(list_hostname[i], token)
        if "CPU" in list_itemname[i]:
            list_max, list_min, list_avg =gethist(hostid,list_itemname[i], token, timestamp)
            sum_cpu_name.append(name)
            sum_cpu_ip.append(ip)
            sum_cpu_min.append(list_min)
            sum_cpu_max.append(list_max)
            sum_cpu_avg.append(list_avg)
    writeexcel_cpu(sum_cpu_name,sum_cpu_ip,sum_cpu_max,sum_cpu_min,sum_cpu_avg)

    sum_net_name = []
    sum_net_ip = []
    sum_net_min = []
    sum_net_max = []
    sum_net_avg = []
    for i in range(len(list_hostname)):
        hostid,name,ip = get_hosts(list_hostname[i], token)
        if "Interface" in list_itemname[i]:
            list_max, list_min, list_avg =gethist(hostid,list_itemname[i], token, timestamp)
            sum_net_name.append(name)
            sum_net_ip.append(ip)
            sum_net_min.append(list_min)
            sum_net_max.append(list_max)
            sum_net_avg.append(list_avg)
    writeexcel_net(sum_net_name,sum_net_ip,sum_net_max, sum_net_min, sum_net_avg)

    sum_Memory_name = []
    sum_Memory_ip = []
    sum_Memory_min = []
    sum_Memory_max = []
    sum_Memory_avg = []
    for i in range(len(list_hostname)):
        hostid, name, ip = get_hosts(list_hostname[i], token)
        if "Memory" in list_itemname[i]:
            list_max, list_min, list_avg = gethist(hostid, list_itemname[i], token, timestamp)
            sum_Memory_name.append(name)
            sum_Memory_ip.append(ip)
            sum_Memory_min.append(list_min)
            sum_Memory_max.append(list_max)
            sum_Memory_avg.append(list_avg)
    writeexcel_Memory(sum_Memory_name, sum_Memory_ip,sum_Memory_max, sum_Memory_min, sum_Memory_avg)



    logout(token)
