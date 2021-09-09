#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import socket
import time
import random

# MAIL SETTING
SMTP_SERVER = '172.22.11.28'
SMTP_SENDER = 'lflchnitzabbix@lflogistics.com'
SMTP_RECEIVER = 'RoyMS_Li@macroview.com'


def sendMailBySocket(sender, receiver, data):
    """
    @description: 使用socket方式发送邮件
    :param sender: 发件人邮箱
    :param receiver: 收件人邮箱
    :param data: 邮件内容
    :return: BOOL
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定本机ip
    s.bind(('10.132.243.230', 0))
    try:
        # 连接smtp server
        s.connect((SMTP_SERVER, 25))
        # s.send("EHLO server\r\n".encode(encoding='utf-8'))
        s.send("MAIL FROM:{}\r\n".format(sender).encode(encoding='utf-8'))
        s.send("RCPT TO:{}\r\n".format(receiver).encode(encoding='utf-8'))
        s.send("DATA\r\n".encode(encoding='utf-8'))
        s.send(data.encode('utf-8'))
        s.send("\r\n.\r\n".encode(encoding='utf-8'))
        s.send("QUIT\r\n".encode(encoding='utf-8'))
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        s.close()


def makeContent(sender, receiver, mail_subject, mail_content, ishtml=False):
    """
    :param sender: 发件人
    :param receiver: 收件人
    :param mail_subject: 邮件主题
    :param mail_content: 邮件内容
    :param isHtml: 是否HTML格式
    :return: str
    """
    # 构造邮件头 和 MIMEtext 分段
    # 需要注意的就是boundary="-----=_Part_{random}_=-----" 这行定义了一个邮件的分段标志，
    # 这里假设分段标志为A，即boundary="A"。则每一个内容分段开头一行必须是--A，而邮件的结尾必须有A--
    mail_template = '''Date: {date}\r\nFrom: <{from}>\r\nTo: <{to}>\r\nSubject: {subject}\r\nX-priority: {priority}\r\nX-Mailer: Charmail 1.0.0[cn]\r\nMIME-Version: 1.0\r\nContent-Type: multipart/alternative;\r\n\tboundary="-----=_Part_{random}_=-----"\r\n{content}\r\n-------=_Part_{random}_=-------'''

    # 构造邮件的一个内容分段（该分段的内容类型为text/plain）
    # 需要注意的是内容的分段必须以上面定义的分段标志开始，且在分段标志的最前面加上两个短横杠--
    text_content_template = '''-------=_Part_{random}_=-----\r\nContent-Type: text/plain;\n\tcharset="UTF-8"\r\nContent-Transfer-Encoding: base64\r\n\r\n{content}\r\n'''

    # 构造邮件的一个内容分段（该分段的内容类型为text/html）
    html_content_template = '''-------=_Part_{random}_=-----\r\nContent-Type: text/html;\r\n\tcharset=UTF-8\r\nContent-Transfer-Encoding: quoted-printable\r\n{content}\r\n'''

    # 构造邮件的一个内容分段（该分段的内容类型为zip附件）
    attachment_content_template = '''-------=_Part_{random}_=-----\r\nContent-Type: {type};\r\n\tname={name}\r\nContent-Transfer-Encoding: base6\r\nContent-Disposition: attachment;\r\n\tfilename={name}\r\n{content}\r\n'''

    # MIME 支持的文件类型有很多，详细的可以参考http://www.w3school.com.cn/media/media_mimeref.asp
    attachment_type = ['text/plain', 'application/zip', 'image/jpeg']

    # 生成随机码用于内容分段
    rand = str(random.randint(0, 10000))

    if ishtml is True:
        content = html_content_template
        content = content.replace('{content}', mail_content)
        content = content.replace('{random}', rand)
    else:
        content = text_content_template
        content = content.replace('{content}', mail_content)
        content = content.replace('{random}', rand)
    # 替换邮件头及分段内容
    mail_template = mail_template.replace('{date}', time.asctime(time.localtime(time.time())))
    mail_template = mail_template.replace('{from}', sender)
    mail_template = mail_template.replace('{to}', receiver)
    mail_template = mail_template.replace('{subject}', mail_subject)
    mail_template = mail_template.replace('{priority}', '3')
    mail_template = mail_template.replace('{random}', rand, 5)
    mail_template = mail_template.replace('{content}', content)
    return mail_template


def sendMail(sender, receiver, mail_subject, mail_content, ishtml):
    return sendMailBySocket(sender, receiver, makeContent(sender, receiver, mail_subject, mail_content, ishtml))


def main():
    mail_subject = 'TEST'
    mail_content = 'THIS IS A TEST MAIL FROM PYTHON SCRIPT'
    result = sendMail(SMTP_SENDER, SMTP_RECEIVER, mail_subject, mail_content, True)
    if result is True:
        print('send success')
    else:
        print('send fail')


if __name__ == '__main__':
    main()
