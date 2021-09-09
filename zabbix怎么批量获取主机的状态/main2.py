import re
import pandas as pd

with open("test.txt","r",encoding='utf-8')as f:
    content = f.readlines()

list_host = []
list_ip = []
for c in content:
    host = re.compile('"host": "(.*?)",')
    hosts = host.findall(c)
    list_host.append(hosts[0])
    ip = re.compile('"ip": "(.*?)"}')
    ips = ip.findall(c)
    list_ip.append(ips[0])


duplicated = set()
for i in range(0, len(list_ip)):
    if list_ip[i] in list_ip[i+1:]:
        duplicated.add(list_ip[i])

list_host_1 = []
list_ip_1 = []
for i in range(len(list_ip)):
    for d in duplicated:
        if list_ip[i] == d:
            list_host_1.append(list_host[i])
            list_ip_1.append(list_ip[i])

df = pd.DataFrame()
df['主机'] = list_host_1
df['ip'] = list_ip_1
df.to_excel('重复项主机.xlsx')