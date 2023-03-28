# 
# -*- coding: utf-8 -*-
# ---
# @Project: mobile_frame
# @Software: PyCharm
# @File: server.py
# @Author: lxs
# @Time: 2023/3/27 17:48
'''
启动和关闭appium服务
通过命令行操作
1.多设备运行，每个手机对应一个appium服务
2.ios和安卓，stop方法不同
'''
import os
import platform
import subprocess

from setting import DIR_NAME


class AppiumServer:
    def start(self, port=4723, chromedriver_port=8000):
        # 1.存放log日志
        appium_log_file = DIR_NAME + f'/logs/appium{port}.log'
        # 2.启动appium服务
        command = f'appium -p {port} --chromedriver-port {chromedriver_port} -g {appium_log_file}'
        # 3.python中执行命令行参数
        subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True).communicate()
    def stop(self, port=4723):
        '''
              1.找到启动端口对应的服务
              2.杀死服务
              3.字符串进行处理->目标内容
              '''
        # 先通过命令去获取电脑的操作系统的名字:命令行不一样
        system_name = platform.system()  # 获取操作系统的名字
        print(system_name)
        if system_name.lower() == 'windows':
            # 可以获取命令的返回值
            res = os.popen(f'netstat -ano|findstr {port}')
            # print(f'获取到的res是{res}')
            content = res.read().strip()  # content 字符串
            # print(content)
            if 'LISTENING' in content:
                all_lines = content.split('\n')  # 查询出来的不止一行 列表
                # print(all_lines)
                for line in all_lines:
                    if 'LISTENING' in line:
                        # print(f'line.split{line.split("LISTENING")}')
                        processs_id = line.split('LISTENING')[1].strip()
                        os.popen(f'taskkill -f -pid {processs_id}')
                        break
        else:  # mac
            res = os.popen(f'lsof -i:{port}')  # 获取端口号对应的进程号
            res_str = res.read().strip()
            if res_str != '' and 'LISTEN' in res_str:
                all_lines = res_str.split('\n')  # 列表
                for line in all_lines:
                    if 'LISTEN' in line:
                        # print(f'line.split{line.split("LISTENING")}')
                        processs_id = line.split('LISTEN')[1].strip()[0:5]
                        os.popen(f'kill {processs_id}')
                        break

if __name__ == '__main__':
    server = AppiumServer()
    # server.start()
    server.stop()