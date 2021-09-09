# coding: utf8

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import get_zabbix_alert as za
import time, sys,json
from sendMailBySocket import sendMail


sender = 'lflchnitzabbix@lflogistics.com'  # 发送人邮箱地址
to_address = ['Felix_Zeng@macroview.com'] #收件人邮箱>地址
cc_address = ['Felix_Zeng@macroview.com']  # 抄送人邮箱地址

smtp_server = '172.22.11.28'  # STMP服务器地址


zabbix_user = 'Dashboard_API' # zabbix账号
zabbix_passwd = 'API#@098' # zabbix密码
zabbix_url = 'http://10.132.243.229/zabbix/api_jsonrpc.php' #zabbix api地址

# 邮件信息
email_title = "Smart Notification_LFL - Monitoring Event Analysis Daily Report" #邮件标题
email_msg = '服务小助手已为您整理重要告警讯息，您可以通过以下内容，快速了解告警历史记录' #邮件消息

# 时间间隔
day = 1

def send_mail(day):

    # msgRoot = MIMEMultipart('related')
    # msgRoot['Subject'] = email_title
    # msgRoot['From'] = sender
    # msgRoot['To'] = ",".join(to_address)  # 发给多人
    # msgRoot['Cc'] = ",".join(cc_address)  #

    table_html_code = '''<table width="90%" border="1" cellspacing="0" cellpadding="5" bgcolor="#cccccc" class="tabtop13">
        <tr>
            <th colspan="3" class="btbg titfont">主机组告警统计</th>
        </tr>
        <tr class="btbg titfont">
            <th>
                主机组
            </th>
            <th width="80px">
                所属部门
            </th>
            <th width="60%">
                告警次数
            </th>
        </tr>
    <!-- group -->
    </table>
    <br>
    <table width="90%" border="1" cellspacing="0" cellpadding="4" bgcolor="#cccccc" class="tabtop13">
        <tr>
            <th colspan="5" class="btbg titfont">按触发器告警统计(告警级别: SEVERITY 1：(S1) = Disaster , SEVERITY 2: (S2) = High , SEVERITY 3: S(3) = Average , SEVERITY 4: (S4) = Warning .)
            </th>
        </tr>
        <tr class="btbg titfont">
            <th>主机</th>
            <th width="40px">告警次数</th>
            <th>主机组</th>
            <th>触发器</th>
            <th width="40px">告警级别</th>
        </tr>
    <!-- trigger -->
    </table>
    <br>
    '''

    mail_html = open("table2.html", "r", encoding="utf-8").read()

    alert_class = za.get_zabbix_alert(zabbix_user, zabbix_passwd, zabbix_url)
    table_data = alert_class.get_table_html(day)
    time_str = za.get_time_str(day)

    # 邮件html处理
    mail_html = mail_html.replace('<!-- imgstart -->', table_html_code)
    mail_html = mail_html.replace('<!-- group -->', table_data[0])
    mail_html = mail_html.replace('<!-- trigger -->', table_data[1])
    mail_html = mail_html.replace('{#msg}', email_msg)
    mail_html = mail_html.replace('{#title1}', '')
    mail_html = mail_html.replace('{#time1}', time.strftime("%H:%M %d/%m/%Y", time.localtime()))
    mail_html = mail_html.replace('{#time3}', time.strftime("%H:%M %d/%m/%Y", time.localtime(time_str[1])))
    mail_html = mail_html.replace('{#time2}', time.strftime("%H:%M %d/%m/%Y", time.localtime(time_str[0])))


    result = sendMail(sender,to_address + cc_address,email_title,mail_html,True)
    if result is True:
        print('send success')
    else:
        print('send fail')

    # content = MIMEText(mail_html, 'html', 'utf-8')
    # msgRoot.attach(content)
    # smtp = smtplib.SMTP_SSL(smtp_server, 25)
    # # smtp = smtplib.SMTP(smtp_server, 587)
    # smtp.ehlo()
    # smtp.starttls()
    # smtp.login(username, password)
    # smtp.sendmail(sender, to_address + cc_address, msgRoot.as_string())
    # smtp.quit()

if __name__ == '__main__':
    try:
        day = sys.argv[1]
    except:
        print(day)
    send_mail(float(day))

