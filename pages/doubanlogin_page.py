# 
# -*- coding: utf-8 -*-
# ---
# @Project: mobile_frame
# @Software: PyCharm
# @File: doubanlogin_page.py
# @Author: lxs
# @Time: 2023/3/27 16:45
from common.driver import InitDriver
from common.file_load import read_yml


class LoginPage:
    def __init__(self, driver: InitDriver):
        self.driver = driver
        self.page_name = self.__class__.__name__
        self.page_info = read_yml('/pagesfiles/douban.yml').get(self.page_name)

    def click_confirm(self):
        ele_info = self.page_info.get('同意按钮')
        self.driver.click(ele_info)

    def click_tvAction(self):
        ele_info = self.page_info.get('进入首页')
        self.driver.click(ele_info)

    def click_username_login(self):
        ele_info = self.page_info.get('帐号密码登录')
        self.driver.click(ele_info)

    def input_username(self, username):
        ele_info = self.page_info.get('输入用户名')
        self.driver.send_keys(ele_info, username)

    def input_pwd(self, password):
        ele_info = self.page_info.get('输入密码')
        self.driver.send_keys(ele_info, password)

    def click_login_btn(self):
        ele_info = self.page_info.get('登录按钮')
        self.driver.click(ele_info)