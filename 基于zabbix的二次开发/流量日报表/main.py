#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import requests
import datetime
import json
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sendMailBySocket import sendMailBySocket

# ip = '10.132.243.229'
# user = "Dashboard_API"
# password = "API#@098"

ip = '172.22.254.8:8123'
user = "Admin"
password = "zabbix"

# 邮件标题
email_title = '线路流量使用日报'
#邮件消息
email_msg = '服务小助手已为您整理线路流量使用日报，您可以通过以下内容，快速了解线路流量使用'

# 发送人邮箱地址
sender = 'lflchnitzabbix@lflogistics.com'
# 收件人邮箱地址
to_address = 'Felix_Zeng@macroview.com'


# STMP服务器地址
smtp_server = '172.22.11.28'

class ZabbixApi:
    def __init__(self, ip, user, password):
        self.url = 'http://' + ip + '/zabbix/api_jsonrpc.php'
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
    def get_service(self,serviceids):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "service.get",
            "params": {
                "output": "extend",
                "serviceids": serviceids,
                "selectTrigger":"extend",
            },
            "auth": self.auth,
            "id": 1
        })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2).json()
            result = response['result']
            print(result)
            for r in result:
                name = r['name'].replace("\t","")
                triggerid = r['triggerid']
                return name,triggerid
        except Exception as e:
            print("\033[0;31;0m HOST GET ERROR\033[0m")
            raise Exception

    def trigger_get(self,triggerids):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "trigger.get",
            "params": {
                "triggerids": triggerids,
                # "output": "extend",
                # "selectFunctions": "extend"
            },
            "auth": self.auth,
            "id": 1
        })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2).json()
            result = response['result']
            print(result)
        except Exception as e:
            print("\033[0;31;0m HOST GET ERROR\033[0m")
            raise Exception


    def get_getsla_time(self,serviceids,yesterday, today):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "service.getsla",
            "params": {
                "serviceids":serviceids,
                "intervals": [
                    {
                        "from": yesterday,
                        "to": today
                    }
                ]

            },
            "auth": self.auth,
            "id": 1
        })
        name,triggerid = self.get_service(serviceids)
        print(self.trigger_get(triggerid))
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2).json()
            result = response['result']
            sla = result['{}'.format(5)]['sla']
            for s in sla:
                oktime = s['okTime']
                problemtime = s['problemTime']
                if int(oktime) == 86400:
                    list_sum = [name,'OK']
                    return list_sum
                elif int(oktime) != 86400 and int(problemtime) <= 14400:
                    list_sum = [name, 'Need monitor']
                    return list_sum
                elif int(oktime) != 86400 and int(problemtime) > 14400:
                    list_sum = [name, 'Need Attention']
                    return list_sum
                if '90%' in name:
                    if int(oktime) == 86400:
                        list_sum = [name, 'OK']
                        return list_sum
                    elif int(oktime) != 86400 and int(problemtime) >= 7200:
                        list_sum = [name, 'Peak']
                        return list_sum
        except Exception as e:
            print("\033[0;31;0m HOST GET ERROR\033[0m")
            raise Exception

# 获取多日前0点与今日0点的时间戳
def getYesterday(day):
    today = datetime.date.today()
    oneday = datetime.timedelta(days=day)
    yesterday = today - oneday
    today_ = str(today) + " 0:00:00"
    yesterday_ = str(yesterday) + " 0:00:00"
    todayArray = time.strptime(today_, "%Y-%m-%d %H:%M:%S")
    yesterdayArray = time.strptime(yesterday_, "%Y-%m-%d %H:%M:%S")
    todayStamp = int(time.mktime(todayArray))
    yesterdayStamp = int(time.mktime(yesterdayArray))
    return str(yesterdayStamp), str(todayStamp)

def tail_html_str():
    zabbix = ZabbixApi(ip, user, password)
    yesterday, today = getYesterday(1)
    list_serviceids = [5]
    trigger_html_str = ''
    for l in list_serviceids:
        name, status = zabbix.get_getsla_time(l,yesterday, today)
        tail_html_str = '''<tr>
                            <td>{}</td>
                            <td>{}</td>       
                            </tr>'''.format(name,status)
        trigger_html_str = trigger_html_str + tail_html_str
        return trigger_html_str

def send_mail():

    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = email_title
    msgRoot['From'] = sender
    msgRoot['To'] = to_address

    table_html_code = '''
    <table width="90%" border="1" cellspacing="0" cellpadding="4" bgcolor="#cccccc" class="tabtop13">
        <tr>
            <th colspan="3" class="btbg titfont">
            </th>
        </tr>
        <tr class="btbg titfont">
            <th>Node Name</th>
            <th>status</th>
        </tr>
    <!-- trigger -->
    </table>
    <br>
    '''
    mail_html = open("table2.html", "r", encoding="utf-8").read()
    # 邮件html处理
    mail_html = mail_html.replace('<!-- imgstart -->', table_html_code)
    mail_html = mail_html.replace('<!-- trigger -->', tail_html_str())
    # print(tail_html_str())
    # print(mail_html)
    # mail_html = mail_html.replace('{#msg}', email_msg)
    # mail_html = mail_html.replace('{#title1}', '')
    #
    # content = MIMEText(mail_html, 'html', 'utf-8')
    # msgRoot.attach(content)
    # result = sendMailBySocket(sender, to_address, msgRoot.as_string())
    # if result is True:
    #     print('send success')
    # else:
    #     print('send fail')


if __name__ == '__main__':
    send_mail()
