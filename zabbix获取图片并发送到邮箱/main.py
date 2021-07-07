import requests
import os, stat, datetime
import urllib.request
import datetime
import time as Time
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import parseaddr, formataddr
from smtplib import SMTP

# 邮件标题
email_title = "LF-zabbix二次开发-重要线路图"
# 邮件内容
email_msg = "服务小助手已为您整理所有重要线路流量，您可以通过以下流量图，快速了解各线路流量情况。"
sender = 'GZ_DSOC_Console_@macroview.com'# 发送人邮箱地址
# 收件人邮箱地址
to_address = ['Felix_Zeng@macroview.com']
cc_address = ['Felix_Zeng@macroview.com']

host = '172.22.254.8'

username = 'gz_cns_console' # 发送人账号
#基本修改这个密码就好，每三个月跟住邮箱密码修改一次(由于邮箱会修改密码)
password = 'C0ns0lePC@410'# 发送人密码
smtp_server = 'webmail.macroview.com' # STMP服务器地址
n_day = 1# 截取多少天前的图表


headers = {
    "Host": host,
    "Origin": "https://" + host,
    "Referer": "https://{}/zabbix/index.php".format(host),
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
}

session = requests.session()
session.headers = headers



def monidenglu(id):
    url = 'https://{}/zabbix/index.php'.format(host)
    data = {
        "name": "Admin",
        "password": "zabbix",
        "autologin": "1",
        "enter": "登录",
    }
    html = session.post(url=url,headers=headers,data=data,verify=False)
    if html.status_code == 200:
        get_html(session,id)
    else:
        print(html.status_code)

def get_html(sess,itemid):
    # 定义获取图片的参数
    graph_params = {
        "from":"now-1d/d",
        "to":"now-1d/d",
        "itemids[0]": itemid,
        "type": "0",
        "profileIdx": "web.item.graph.filter",
        "profileIdx2": itemid,
        "width": "1820",
        "height":"600",
    }
    graph_url = 'https://{}/zabbix/chart.php?'.format(host)
    #模拟登陆，发送get请求获取图片数据
    graph_req = sess.get(url=graph_url, params=graph_params,verify=False)
    #获取当前时间，用于给图片命名
    time_tag = Time.strftime("%Y%m%d%H%M%S", Time.localtime())
    year = time_tag[0:4]
    month = time_tag[4:6]
    day = time_tag[6:8]
    graph_name = '{}'.format(itemid)+'.png'
    # #创建保存图片的文件，如果不存在便创建文件夹
    graph_path = 'img/{}/{}/{}'.format(year,month,day)
    if not os.path.exists(graph_path):
        os.makedirs(graph_path)
    # 使用绝对路径保存图片
    graph_name = os.path.join(graph_path, graph_name)
    # 将获取到的图片数据写入到文件中去
    with open(graph_name, 'wb') as f:
        f.write(graph_req.content)
    send_mail_pis(graph_path)


# 获取多日前0点与今日0点的时间戳
def getYesterday(day):
    today = datetime.date.today()
    oneday = datetime.timedelta(days=day)
    yesterday = today - oneday
    today_ = str(today) + " 0:00:00"
    yesterday_ = str(yesterday) + " 0:00:00"
    todayArray = Time.strptime(today_, "%Y-%m-%d %H:%M:%S")
    yesterdayArray = Time.strptime(yesterday_, "%Y-%m-%d %H:%M:%S")
    todayStamp = int(Time.mktime(todayArray)) * 1000
    yesterdayStamp = int(Time.mktime(yesterdayArray)) * 1000
    return str(yesterdayStamp), str(todayStamp), str(yesterday)

# 发送多张图片邮件
def send_mail_pis(graph_path):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = email_title
    msgRoot['From'] = sender
    msgRoot['To'] = ",".join(to_address)  # 发给多人
    msgRoot['Cc'] = ",".join(cc_address)  # 发给多人
    mail_html = open("mail.html", "r", encoding="utf-8").read()
    yesterdayIs = str(getYesterday(1)[2]).split("-")
    time2 = yesterdayIs[2] + '/' + yesterdayIs[1] + '/' + yesterdayIs[0]
    time3 = yesterdayIs[1] + '/' + yesterdayIs[2]
    mail_html = mail_html.replace("{#time1}", Time.strftime("%H:%M %d/%m/%Y", Time.localtime()))
    mail_html = mail_html.replace("{#time2}", time2)
    mail_html = mail_html.replace("{#time3}", time2)
    mail_html = mail_html.replace("{#title}", email_title)
    mail_html = mail_html.replace("{#title1}", email_title.replace("日报", ""))
    mail_html = mail_html.replace("{#msg}", email_msg)

    mylist = os.listdir(graph_path)


    #对图片进行定位
    for m in mylist:
        insert_img_str = """
            <br><img src="cid:image%s" alt="image%s"><br><!-- imgend -->
            """ % (m,m)
        mail_html = re.sub("<!-- imgend -->", insert_img_str, mail_html)
    content = MIMEText(mail_html, 'html', 'utf-8')
    msgRoot.attach(content)

    # 获取图片
    for m in mylist:
        fp = open('{}/{}'.format(graph_path,m), 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', 'image' + str(m))  # 该id和html中的img src对应
        msgRoot.attach(msgImage)

    # signature_img_file = 'img/signature.png'
    # fp = open(signature_img_file, 'rb')
    # msgImage = MIMEImage(fp.read())
    # fp.close()
    # msgImage.add_header('Content-ID', 'image_sign')  # 该id和html中的img src对应
    # msgRoot.attach(msgImage)

    smtp = SMTP(smtp_server, '587')
    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(sender, to_address + cc_address, msgRoot.as_string())
    smtp.quit()
    file_name = 'log'
    fp = open(file_name, "a", encoding="utf-8")
    fp.write(Time.strftime("%Y-%m-%d %H:%M:%S", Time.localtime()) + " LF邮件已发送\n")
    fp.close()


if __name__ == '__main__':
    #这里输入要监控的图像监控项的id
    itemid = []
    for i in itemid:
        monidenglu(i)
        print('发送成功')