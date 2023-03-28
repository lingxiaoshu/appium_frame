# 
# -*- coding: utf-8 -*-
# ---
# @Project: mobile_frame
# @Software: PyCharm
# @File: test_login.py
# @Author: lxs
# @Time: 2023/3/27 16:59
import pytest
from actions.login import Login
from common.driver import GlobalDriver


class TestLogin:
    def test_login(self):
        login = Login(GlobalDriver.driver)
        login.login()
        # 断言
        pytest.assume(GlobalDriver.driver.page_contains('首页'))
