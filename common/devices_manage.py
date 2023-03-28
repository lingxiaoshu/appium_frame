# 
# -*- coding: utf-8 -*-
# ---
# @Project: mobile_frame
# @Software: PyCharm
# @File: devices_manage.py
# @Author: lxs
# @Time: 2023/3/27 20:37
'''
1 随机获取端口号
2 动态获取设备信息：uid和端口号，构造成字典的形式
最后将信息写入devices.yml
'''
import os
import platform
import random

import yaml

from setting import DIR_NAME


def random_port(start=4000, end=9000):
    port = random.randint(start, end)
    # 判断port是否被占用
    system_name = platform.system()
    while True:
        if system_name.lower() == 'windows':
            res = os.popen(f'netstat -ano|findstr {port}').read().strip()
            if 'LISTENING' not in res:  # 证明端口号没有被占用
                break
            else:  # 如果被占用，随机生成
                port = random.randint(start, end)
        else:  # mac
            res = os.popen(f'lsof -i:{port}').read().strip()
            if 'LISTEN' not in res:  # 没有被占用
                break
            else:  # 被占用即随机生成
                port = random.randint(start, end)

    return port

# 动态获取设备信息
def get_devices():
    '''
    获取当前电脑所连接的设备
    1.手机到底是安卓还是苹果手机
     1.1无论是什么电脑都首先用adb devices获取android手机的设备
     =>证明现在在做安卓手机的自动化测试
     1.2 如果操作系统不是windows 可能是在ios手机做测试
     判断标准：ios用idevice_id -l 获取ios的设备号
    2.udid 和其他一些端口号
    :return:
    '''
    system_name = platform.system()  # 操作系统的名字
    # 定义一个设备列表 [{},{}]
    devices_list = []
    # 执行获取设备的命令  adb devices readlines()  读取出来的就是列表
    res = os.popen('adb devices').read().strip()
    # print(f'res的值是{res}')
    # 解析res获取设备的ip地址和端口号
    all_lines = res.split('\n')[1:]
    # print(f'all_lines的值是{all_lines}')
    for line in all_lines:
        # print(f'line.split()的值是{line.split()}')
        udid = line.split()[0]
        status = line.split()[1]
        # print(f'status的值是{status}')
        if status == 'device':
            # 设备的信息都构造完成 放在一个字典中
            # 1.启动appium服务的端口号:4723
            port = random_port(end=5000)
            # 2.systemPort 手机6790->appium8203 端口的映射
            # 手机和appium做映射的那个appium的端口号，不能重复
            systemPort = random_port(start=5001, end=6000)
            # 3.chromedriver-port h5原生页面需要的端口号
            chromedriverPort = random_port(start=6001, end=7000)
            # 构造设备信息-写入要yml文件中-在需要获取设备信息的位置 在动态读取yml文件的内容
            device_info = {
                'platform': 'android',
                'udid': udid,  # 设备唯一的标识
                'port': port,# python脚本和appium服务通信的端口
                'systemPort': systemPort,# appium服务和手机的uiautomator2通信的端口
                'chromedriverPort': chromedriverPort  # 安卓在做h5是chromedriver的端口号
            }
            # print(f'device_info的值是{device_info}')
            devices_list.append(device_info)

        # print(f'devices_list的值是{devices_list}')

    # 不是windows电脑的时候
    if system_name.lower() != 'windows':
        # ios用idevice_id -l 获取ios的设备号
        res = os.popen('idevice_id -l').read().strip()
        all_lines = res.split('\n')
        for line in all_lines:
            udid = line.strip()
            port = random_port(end=5000)
            chromedriverPort = random_port(start=7001, end=8000)
            # ios手机测试时候appium服务和手机上的wda的通信的端口
            wdaPort = random_port(start=8001, end=9000)
            device_info = {
                'platform': 'ios',
                'udid': udid,
                'port': port,
                'chromedriverPort': chromedriverPort,
                'wdaPort': wdaPort
            }
            devices_list.append(device_info)
    # 拿到的所有的信息写入到yml配置文件中
    with open(DIR_NAME+'/config/devices.yml', 'w', encoding='utf-8') as f:
        # 写入yaml文件
        yaml.dump(devices_list, f)
    return devices_list