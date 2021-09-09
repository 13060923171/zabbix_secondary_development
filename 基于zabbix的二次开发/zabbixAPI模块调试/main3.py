import requests
import json
import time


ip = '172.22.254.50:8123'
user = "Admin"
password = "zabbix"
host = '172.22.254.50'


class ZabbixApi:
    def __init__(self, ip, user, password):
        self.url = 'http://' + ip + '/zabbix/api_jsonrpc.php'
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
        })
        try:
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=2)
            auth = response.json().get('result', '')
            return auth
        except Exception as e:
            print("\033[0;31;0m Login error check: IP,USER,PASSWORD\033[0m")
            raise Exception

    def get_host_group(self,itemid):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "trigger.get",
            "params": {
                "triggerids": itemid,
                 "output": "extend",
                "sortfield":'status',
                "sortorder": 'DESC',
                "selectDependencies":"extend",
                # "only_true": '1',  # 仅返回最近处于故障状态的触发器
                # "active": '1',  # 仅返回所属被监控主机的已启用触发器
                "withUnacknowledgedEvents": '1',
                "expandDescription": '1',
                "selectFunctions": "extend",
                "selectHosts": ['name'],  # 返回所属主机信息
                "selectGroups":['name']

            },
            "auth":self.auth,
            "id": 1
        })


        response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
        result = response.json()
        result = result['result']
        list_groups = []
        if len(result) >=0:
            host = result[0]['hosts'][0]['name']
            group = result[0]['groups']
            for g in group:
                groups = g['name']
                list_groups.append(groups)
            return host,list_groups

    def get_problem(self,triggerid):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "problem.get",
            "params": {
                "output": "extend",
                "selectAcknowledges": "extend",
                "selectTags": "extend",
                "objectids": triggerid,
                "recent": "true",
                "sortfield": ["eventid"],
                "sortorder": "DESC"
            },
            "auth": self.auth,
            "id": 1
        })

        response = requests.get(url=self.url, headers=self.headers, data=data, timeout=2)
        result = response.json()
        result = result['result']
        last_time = ''
        list_acknowledges = []
        if len(result) >= 0:
            start_time = result[0]['clock']
            end_time = result[0]['r_clock']
            acknowledges = result[0]['acknowledges']
            for a in acknowledges:
                clock = a['clock']
                clock = int(clock)
                clock = time.localtime(clock)
                dt = time.strftime("%Y-%m-%d %H:%M:%S", clock)
                message = a['message']
                list_acknowledges.append([dt,message])
            if int(end_time) > 0:
                last_time = int(end_time) - int(start_time)
                if int(last_time) <= 60:
                    last_time = str(last_time) + "s"
                elif 60 <= int(last_time) <= 3600:
                    last_time = float(int(last_time) / int(60))
                    last_time = "%.1lf" % last_time
                    last_time = last_time.split('.')
                    last_time = str(last_time[0]) + "m" + str(int(last_time[1]) * 60) + "s"
            else:
                now_time = int(time.time())
                last_time = int(now_time) - int(start_time)
                if int(last_time) <= 60:
                    last_time = str(last_time) + "s"
                elif 60 <= int(last_time) <= 3600:
                    last_time = float(int(last_time) / int(60))
                    last_time = "%.1lf" %last_time
                    last_time = last_time.split('.')
                    last_time = str(last_time[0]) + "m" + str(int(float(int(last_time[1]) / 10) * 60)) + "s"
                else:
                    last_time = float(int(last_time) / int(3600))
                    last_time = "%.2lf" % last_time
                    last_time = last_time.split('.')
                    last_time = str(last_time[0]) + "h" + str(int(float(int(last_time[1]) / 100) * 60)) + "m"
            return last_time,list_acknowledges



if __name__ == '__main__':
    try:
        zabbix = ZabbixApi(ip, user, password)
        #触发器的id
        trigger = '21020'
        a = zabbix.get_host_group(trigger)
        c = '主机:{}\n主机组:{}\n'.format(a[0],','.join(a[1]))
        print(c)
        b = zabbix.get_problem(trigger)
        if len(b[1]) > 0:
            for i in b[1]:
                d = '持续时间:{}\nack跟进最新时间:{},ack跟进最新消息:{}'.format(b[0],i[0],i[1])
                print(d)
        else:
            d = '持续时间:{}\nack跟进情况:无'.format(b[0])
            print(d)


    except Exception as e:
        print(e)
