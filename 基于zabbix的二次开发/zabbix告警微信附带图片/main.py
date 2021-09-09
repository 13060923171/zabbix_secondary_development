#!/usr/bin/env python3
#coding=utf-8

import requests, json
import urllib3
import smtplib,os,time,re,requests,sys
from email.mime.image import MIMEImage


class WechatImage(object): # 根据企业微信api接口文档，定义一个类，使用mpnews类型，https://qydev.weixin.qq.com/wiki/index.php?title=%E6%B6%88%E6%81%AF%E7%B1%BB%E5%9E%8B%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F
    def get_token(self, corpid, secret): # 获取token
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        data = {"corpid": corpid,
                "corpsecret": secret}
        r = requests.get(url=url, params=data, verify=False)
        token = r.json()['access_token']
        return token

    def get_image_url(self, token, path): # 上传临时素材图片，然后返回media_id
        url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=image" % token
        data = {"media": open(path, 'rb')}
        r = requests.post(url=url, files=data)
        dict_data = r.json()
        return dict_data['media_id']
    def get_messages( self,subject,content,path): #定义mpnews类型中的参数字典
        data = ''
        messages = {}
        body = {}
        content_html=text_to_html(content)
        token = self.get_token(corpid, secret)
        image = self.get_image_url(token, path)
        content_html += "<br/> <img src='https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s'>" % (token, image)
        body["title"] = subject
        body['digest'] = content
        body['content'] = content_html
        body['thumb_media_id'] = image
        data = []
        data.append(body)
        messages['articles'] = data
        return messages
    def send_news_message(self, corpid, secret,to_user, agentid,path): #定义发送mpnews类型的数据
        token = self.get_token(corpid, secret)
        messages = self.get_messages(subject, content,path)
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % token
        data = {"toparty": to_user,                                 # 企业号中的用户帐号
                "agentid": agentid,                             # 企业号中的应用id
                "msgtype": "mpnews",
                "mpnews": messages,
                "safe": "0"}
        headers = {'content-type': 'application/json'}
        data_dict = json.dumps(data, ensure_ascii=False).encode('utf-8')
        r = requests.post(url=url, headers=headers, data=data_dict)
        return r.text
def text_to_html(text): #将邮件内容text字段转换成HTML格式
    d=text.splitlines()
    #将邮件内容以每行作为一个列表元素存储在列表中
    html_text=''
    for i in d:
        i='' + i + '<br>'
        html_text+=i + '\n'
    #为列表的每个元素后加上html的换行标签
    return html_text
def get_itemid():
    #获取报警的itemid
    itemid=re.search(r'监控ID:(\d+)',sys.argv[3]).group(1)
    return itemid
def get_graph(itemid):
    #获取报警的图表并保存:x:x:x
    session = requests.session()
    url = 'https://{}/zabbix/index.php'.format(host)
    try:
        headers = {
            "Host": host,
            "Origin": "https://" + host,
            "Referer": "https://{}/zabbix/index.php".format(host),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
        }
        #定义请求消息头

        data = {
            "name": user,
            "password": password,
            "autologin": "1",
            "enter": "登录",
        }
        #定义传入的data
        login=session.post(url=url,headers=headers,data=data,verify=False)
        #进行登录
        graph_params={
            "from" :"now-10m",
            "to" : "now",
            "itemids[0]": itemid,
            "type": "0",
            "profileIdx": "web.item.graph.filter",
            "profileIdx2": itemid,
            "width" : "290", #图片的高宽参数可以自行调整
            "height" : "40",
        }
        #定义获取图片的参数
        graph_req=session.get(url=graph_url,params=graph_params,verify=False)
        #发送get请求获取图片数据
        time_tag=time.strftime("%Y%m%d%H%M%S", time.localtime())
        graph_name='baojing_'+time_tag+'.png'
        #用报警时间来作为图片名进行保存
        graph_name = os.path.join(graph_path, graph_name)
        #使用绝对路径保存图片
        with open(graph_name,'wb') as f:
            f.write(graph_req.content)
            #将获取到的图片数据写入到文件中去
        return graph_name
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    user='Admin'    #定义zabbix用户名
    password='zabbix'    #定义zabbix用户i密
    graph_path='/usr/lib/zabbix/alertscripts/graph/'   #定义图片存储路径，图片需要定时清理
    graph_url='https://172.22.254.50/zabbix/chart.php?'     #定义图表的url
    host='172.22.254.50'
    itemid=get_itemid()
    path =get_graph(itemid)
    to_user = str(sys.argv[1])
    subject = str(sys.argv[2])
    content = str(sys.argv[3])
    corpid= "ww467086d3680324bf"
    secret = "zjSkIZgHN2-VKYV0WRQrwuPKVIAHaB8YwwonaXvW340"
    agentid = "1000002"
    wechat_img = WechatImage()
    wechat_img.send_news_message(corpid, secret,to_user, agentid, path)
