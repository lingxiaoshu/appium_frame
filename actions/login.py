# 
# -*- coding: utf-8 -*-
# ---
# @Project: mobile_frame
# @Software: PyCharm
# @File: login.py
# @Author: lxs
# @Time: 2023/3/27 16:55
from common.driver import InitDriver
from pages.doubanlogin_page import LoginPage


class Login:
    def __init__(self, driver: InitDriver):
        self.driver = driver

    def login(self, username='18812341234', password='mima'):
        loginpage = LoginPage(self.driver)
        loginpage.click_confirm()
        loginpage.click_tvAction()
        loginpage.click_username_login()
        loginpage.input_username(username)
        loginpage.input_pwd(password)
        loginpage.click_login_btn()