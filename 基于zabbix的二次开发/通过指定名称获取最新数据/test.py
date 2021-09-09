#!/usr/bin/env python
# -*- coding: utf-8 -*-

import exifread
import re
import json
import requests


def latitude_and_longitude_convert_to_decimal_system(*args):
    """
    经纬度转为小数, 作者尝试适用于iphone6、ipad2以上的拍照的照片，
    :param arg:
    :return: 十进制小数
    """
    return float(args[0]) + (
                (float(args[1]) + (float(args[2].split('/')[0]) / float(args[2].split('/')[-1]) / 60)) / 60)


def find_GPS_image(pic_path):
    GPS = {}
    date = ''
    with open(pic_path, 'rb') as f:
        tags = exifread.process_file(f)
        for tag, value in tags.items():
            if re.match('GPS GPSLatitudeRef', tag):
                GPS['GPSLatitudeRef'] = str(value)
            elif re.match('GPS GPSLongitudeRef', tag):
                GPS['GPSLongitudeRef'] = str(value)
            elif re.match('GPS GPSAltitudeRef', tag):
                GPS['GPSAltitudeRef'] = str(value)
            elif re.match('GPS GPSLatitude', tag):
                try:
                    match_result = re.match('\[(\w*),(\w*),(\w.*)/(\w.*)\]', str(value)).groups()
                    GPS['GPSLatitude'] = int(match_result[0]), int(match_result[1]), int(match_result[2])
                except:
                    deg, min, sec = [x.replace(' ', '') for x in str(value)[1:-1].split(',')]
                    GPS['GPSLatitude'] = latitude_and_longitude_convert_to_decimal_system(deg, min, sec)
            elif re.match('GPS GPSLongitude', tag):
                try:
                    match_result = re.match('\[(\w*),(\w*),(\w.*)/(\w.*)\]', str(value)).groups()
                    GPS['GPSLongitude'] = int(match_result[0]), int(match_result[1]), int(match_result[2])
                except:
                    deg, min, sec = [x.replace(' ', '') for x in str(value)[1:-1].split(',')]
                    GPS['GPSLongitude'] = latitude_and_longitude_convert_to_decimal_system(deg, min, sec)
            elif re.match('GPS GPSAltitude', tag):
                GPS['GPSAltitude'] = str(value)
            elif re.match('.*Date.*', tag):
                date = str(value)
    return {'GPS_information': GPS, 'date_information': date}


def loads_jsonp(_jsonp):
    """
    解析jsonp数据格式为json
    :return:
    """
    try:
        return json.loads(re.match(".*?({.*}).*", _jsonp, re.S).group(1))
    except:
        raise ValueError('Invalid Input')


def Findaddr(gps):
    url = 'http://restapi.amap.com/v3/geocode/regeo?key=169d2dd7829fe45690fabec812d05bc3&s=rsv3&location=112.960889,28.166693&callback=jsonp_26934_&platform=JS&logversion=2.0&sdkversion=1.3&appname=http%3A%2F%2Fwww.gpsspg.com%2Fiframe%2Fmaps%2Famap_191222.htm%3Fmapi%3D3%26t%3D1579247642522&csid=F79901E4-BD9A-4813-80D3-FE04659E4C39'
    headers = {
        'Referer': 'http://www.gpsspg.com/iframe/maps/amap_191222.htm?mapi=3&t=1579247642522',
        'User-Agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64) AppleWebKit/537.36(KHTML, likeGecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    data = {
        'key': '169d2dd7829fe45690fabec812d05bc3',
        's': 'rsv3',
        'location': gps,
        'callback': 'jsonp_26934_',
        'platform': 'JS',
        'logversion': 2.0,
        'sdkversion': 1.3,
        'appname': 'http://www.gpsspg.com/iframe/maps/amap_191222.htm?mapi=3&t=1579247642522',
        'csid': 'F79901E4-BD9A-4813-80D3-FE04659E4C39',
    }
    resp = requests.get(url, data=data, headers=headers)
    web_data = resp.text
    web_json = loads_jsonp(web_data)
    addr = web_json['regeocode']['formatted_address']
    return addr


GPS_info = find_GPS_image(pic_path='gps_test4.jpg')
gps1 = GPS_info['GPS_information']['GPSLatitude']
gps2 = GPS_info['GPS_information']['GPSLongitude']
gps = str(gps1) + ',' + str(gps2)
print(str(gps1) + ',' + str(gps2))
addr = Findaddr(gps)
print(addr)