#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import socket


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
    s.bind(('10.132.243.229', 0))
    try:
        # 连接smtp server
        s.connect(('172.22.11.28', 25))
        # s.send("EHLO server\r\n".encode(encoding='utf-8'))
        s.send("MAIL FROM:{}\r\n".format(sender).encode(encoding='utf-8'))
        s.send("RCPT TO:{}\r\n".format(receiver).encode(encoding='utf-8'))
        s.send("DATA\r\n".encode(encoding='utf-8'))
        s.send(data.encode('utf-8'))
        s.send("\r\n.\r\n".encode(encoding='utf-8'))
        print(s.recv(1024))
        s.send("QUIT\r\n".encode(encoding='utf-8'))
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        s.close()





