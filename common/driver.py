# 
# -*- coding: utf-8 -*-
# ---
# @Project: mobile_frame
# @Software: PyCharm
# @File: driver.py
# @Author: lxs
# @Time: 2023/3/4 21:15
import time

from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.extensions.android.nativekey import AndroidKey
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from common.file_load import read_yml
from common.logger import GetLogger
from msedge.selenium_tools import EdgeOptions

class GlobalDriver:
    driver = None


class InitDriver:
    def __init__(self, devices_info, worker_id='master'):
        # grid 去调用操作系统的浏览器的话，remote_url
        self.logger = GetLogger().get_logger(worker_id)
        platform = devices_info['platform']
        udid = devices_info['udid']
        port = devices_info['port']
        if platform == 'ios':
            wda = devices_info['wdaPort']
            caps = read_yml('/config/ios.yml')
            caps['udid']= udid
            caps['wdaLocalPort']= wda
        else:
            systemPort = devices_info['systemPort']
            caps = read_yml('/config/android.yml')
            caps['udid'] = udid
            caps['systemPort'] = systemPort

        self.driver = webdriver.Remote(f"http://localhost:{port}/wd/hub", caps)
        self.driver.implicitly_wait(30)

    # 对定位元素进行封装
    def find_element(self, ele_info):
        try:
            locator = self.get_by(ele_info)
            el = self.driver.find_element(*locator)
            self.logger.info(f'查找{ele_info}元素成功')
            return el
        except Exception as e:
            self.logger.error(f'查找{ele_info}元素失败，报错信息为{e}')
            raise Exception(f'查找{ele_info}元素失败，报错信息为{e}')

    # 封装地址
    def get(self, url):
        # 打开目标的网址
        self.driver.get(url)
        self.logger.info(f'登录{url}')
    # 点击操作
    def click(self,ele_info):
        # 定位到元素
        # 进行点击
        # el = self.find_element((ele_info))
        # el.click()
        # type = ele_info.get('type')
        # value = ele_info.get('value')
        # locator = type, value
        try:
            locator = self.get_by(ele_info)
            wait = WebDriverWait(self.driver, 20)
            wait.until(element_click_is_success(locator))
            self.logger.info(f'元素{ele_info}点击成功')
        except Exception as e:
            self.logger.error(f'元素{ele_info}点击失败，报错信息为{e}')
            raise Exception(f'元素{ele_info}点击失败，报错信息为{e}')
    def send_keys(self, ele_info, text):
        try:
            element = self.find_element(ele_info)
            element.clear()
            element.send_keys(text)
            self.logger.info(f'元素{ele_info}输入文本内容{text}成功')
        except Exception as e:
            self.logger.error(f'元素{ele_info}输入失败，报错信息为{e}')
            raise Exception(f'元素{ele_info}输入失败，报错信息为{e}')
    # 断言
    def page_source(self):
        try:
            self.logger.info('获取页面源码')
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f'获取页面源码，报错信息为{e}')
            raise Exception(f'获取页面源码，报错信息为{e}')
    # 断言：判断提示信息是否在页面源码中
    def page_contains(self, text):
        try:
            wait = WebDriverWait(self.driver, 20)
            # d表示self.driver对象
            flag = wait.until(lambda d: text in d.page_source)
            self.logger.info(f'元素源码中包含{text}文本')
        except Exception as e:
            flag = False
            self.logger.warning(f'元素源码中不包含{text}文本，报错信息不包含{e}')
        return flag
    # 退出
    def quit(self):
        try:
            self.driver.quit()
            self.logger.info('driver退出成功')
        except Exception as e:
            self.logger.error(f'driver退出失败，报错信息为{e}')
    # 获取定位策略locator,返回一个具体的定位策略
    # 增加app的定位方法
    def get_by(self, ele_info):
        '''
                ele_info = {'type':xpath/id/css, 'value':值}  # 人为定义
                type = ele_info.get('type')  # 定位策略
                value = ele_info.get('value')  # 值
                 driver.find_element(type, value).send_keys('xxxx')
                :return:
                '''
        type = ele_info.get('type')  # 定位策略
        value = ele_info.get('value')  # 值
        if type == 'id':
            locator = (By.ID, value)
        elif type == 'name':
            locator = (By.NAME, value)
        elif type == 'classname':
            locator = (By.CLASS_NAME, value)
        elif type == 'tagname':
            locator = (By.TAG_NAME, value)
        elif type == 'css':
            locator = (By.CSS_SELECTOR, value)
        elif type == 'xpath':
            locator = (By.XPATH, value)
        elif type == 'linktext':
            locator = (By.LINK_TEXT, value)
        elif type == 'plinktext':
            locator = (By.PARTIAL_LINK_TEXT, value)
        # app特有的定位方法
        # 安卓定位的方式
        elif type == 'uiautomator':
            locator = (MobileBy.ANDROID_UIAUTOMATOR, value)
        elif type == 'accessibilityid':  # 需要有content-desc属性可用
            locator = (MobileBy.ACCESSIBILITY_ID, value)
        # ios的定位方式
        elif type == 'predicate':
            locator = (MobileBy.IOS_PREDICATE, value)


        else:
            # raise 跑出异常
            self.logger.error('不支持的元素定位方法:{}'.format(type))
            raise Exception('不支持的元素定位方法:{}'.format(type))
        self.logger.info(f'元素的定位策略是{locator}')
        return locator
    def move_to_element(self, ele_info):
        '''
        鼠标悬浮
        :return:
        '''
        # 定位元素
        try:
            el = self.find_element(ele_info)
            action = ActionChains(self.driver)
            action.move_to_element(el).perform()
            self.logger.info(f'鼠标悬浮元素{ele_info}成功')
        except Exception as e:
            self.logger.error(f'鼠标悬浮元素{ele_info}失败，报错信息为{e}')
            raise Exception(f'鼠标悬浮元素{ele_info}失败，报错信息为{e}')
    # 截图
    def get_screenshot_as_png(self):
        try:
            png = self.driver.get_screenshot_as_png()
            self.logger.info('截图成功')
            return png
        except Exception as e:
            self.logger.error(f'截图失败，报错信息为{e}')
            raise Exception(f'截图失败，报错信息为{e}')
    # 截图并保存成文件
    def get_screenshot_as_file(self,filepath):
        try:
            png = self.driver.get_screenshot_as_file(filepath)
            self.logger.info('截图并保存成功')
        except Exception as e:
            self.logger.error(f'截图并保存失败，报错信息为{e}')
            raise Exception(f'截图并保存失败，报错信息为{e}')
    # 切换窗口
    def switch_window(self, filepath):
        time.sleep(3)
        try:
            handles = self.driver.window_handles
            self.driver.switch_to.window(handles[-1])
            self.logger.info('切换窗口成功')
        except Exception as e:
            self.logger.error(f'切换窗口失败，报错信息为{e}')
            raise Exception(f'切换窗口失败，报错信息为{e}')
    # 获取文本内容
    def get_text(self, ele_info):
        el = self.find_element(ele_info)
        try:
            text = el.text
            self.logger.info(f'获取元素文本内容成功，内容是{text}, 类型是{type(text)}')
            return text
        except Exception as e:
            self.logger.error(f'获取元素文本内容失败，报错信息为{e}')
            raise Exception(f'获取元素文本内容失败，报错信息为{e}')
    #app的api方法
    # 整个屏幕的滑动
    def swipe_on_screen(self, direction='up'):
        '''
        整个屏幕的滑动：上下左右
        向上滑动up：y轴减少
        向下滑动down：y轴增大
        向左滑动left：x轴减少
        向右滑动right：x轴增大
        :return:
        '''
        # 获取手机分辨率
        size = self.driver.get_window_size()
        print('屏幕的分辨率是{}'.format(size))
        width = size['width']
        height = size['height']
        if direction == 'up':
            self.driver.swipe(start_x=0.5 * width, start_y=0.5 * height, end_x=0.5 * width, end_y=0.25 * height)
        elif direction == 'down':
            self.driver.swipe(start_x=0.5 * width, start_y=0.25 * height, end_x=0.5 * width, end_y=0.75 * height)
        elif direction == 'left':
            self.driver.swipe(start_x=0.75 * width, start_y=0.5 * height, end_x=0.25 * width, end_y=0.5 * height)
        elif direction == 'right':
            self.driver.swipe(start_x=0.25 * width, start_y=0.5 * height, end_x=0.75 * width, end_y=0.05 * height)
        else:
            self.logger.error('您输入的方向不支持')
            raise Exception('您输入的方向不支持滑动')

    # 单个元素的滑动
    def swipe_on_element(self, el, direction='up'):
        # 获取元素的坐标
        x1 = el.location['x']
        y1 = el.location['y']
        # 获取元素的size
        w = el.size['width']
        h = el.size['height']
        if direction == 'up':
            # 向上滑动
            self.driver.swipe(start_x=x1 + 0.5 * w, start_y=y1 + 0.75 * h, end_x=x1 + 0.5 * w, end_y=y1 + 0.25 * h)
        elif direction == 'down':
            self.driver.swipe(start_x=x1 + 0.5 * w, start_y=y1 + 0.25 * h, end_x=x1 + 0.5 * w, end_y=y1 + 0.75 * h)
        elif direction == 'left':
            self.driver.swipe(start_x=x1 + 0.75 * w, start_y=y1 + 0.5 * h, end_x=x1 + 0.25 * w, end_y=y1 + 0.5 * h)
        elif direction == 'right':
            self.driver.swipe(start_x=x1 + 0.25 * w, start_y=y1 + 0.5 * h, end_x=x1 + 0.75 * w, end_y=y1 + 0.5 * h)
        else:
            self.logger.error('输入的方向不支持滑动')
            raise ('输入的方向不支持滑动')

    # 手势解锁滑动,调用手势方法，应用场景：设置-安全-屏幕锁定方式-图案
    def swipe_on_gesture(self, el, pwd=''):
        '''

        :param driver:
        :param el: 密码解锁的整个区域的元素
        :param pwd: 想要连接的点，从0开始，eg：pwd='13678'
        :return:
        '''
        # 获取元素的坐标
        x1 = el.location['x']
        y1 = el.location['y']
        # 获取元素的size
        w = el.size['width']
        h = el.size['height']
        # 滑动
        action = TouchAction(self.driver)
        # 每个点的坐标列表
        gesture_list = [{'x': x1 + 1 / 6 * w, 'y': y1 + 1 / 6 * h}, {'x': x1 + 1 / 2 * w, 'y': y1 + 1 / 6 * h},
                        {'x': x1 + 5 / 6 * w, 'y': y1 + 1 / 6 * h},
                        {'x': x1 + 1 / 6 * w, 'y': y1 + 1 / 2 * h}, {'x': x1 + 1 / 2 * w, 'y': y1 + 1 / 2 * h},
                        {'x': x1 + 5 / 6 * w, 'y': y1 + 1 / 2 * h},
                        {'x': x1 + 1 / 6 * w, 'y': y1 + 5 / 6 * h}, {'x': x1 + 1 / 2 * w, 'y': y1 + 5 / 6 * h},
                        {'x': x1 + 5 / 6 * w, 'y': y1 + 5 / 6 * h}]
        action = action.press(x=gesture_list[int(pwd[0])]['x'], y=gesture_list[int(pwd[0])]['y'])
        for i in pwd[1:]:
            action.move_to(x=gesture_list[int(i)]['x'], y=gesture_list[int(i)]['y'])
        action.release().perform()
    # 启动app，启动自己或者第三方app都可以
    def start_activity(self, app_package, app_activity):
        self.driver.start_activity(app_package, app_activity)

    # 清除app数据并且重新启动
    def reset_app(self):
        self.driver.reset()

    # 长按某元素
    def long_press(self, ele_info):
        element = self.find_element(ele_info)
        TouchAction(self.driver).long_press(el=element).release().perform()

    # 长按某坐标
    def long_press_cor(self, x, y):
        TouchAction(self.driver).long_press(x=x, y=y).release().perform()

    # 点手机上的返回键，只支持安卓
    def press_back(self):
        self.driver.press_keycode(AndroidKey.BACK)

    # 点击手机上的home键，只支持安卓
    def press_home(self):
        self.driver.press_keycode(AndroidKey.HOME)
        self.logger.info('点击手机Home键成功')

# 显示等待封装无法点击的场景
class element_click_is_success:
    '''
    locator：定位策略
    '''
    def __init__(self, locator):
        self.locator = locator
        # 定义函数的过程：定义参数、返回值、运行代码
    def __call__(self, driver):
        # 函数就是对象=类名() 等价于函数的名字
        try:
            # new一个参数locator，存储定位元素的变量
            # locator = By.CSS_SELECTOR, '#address_list>li:first-child'
            # 不定长参数，可以使用 args元组，
            driver.find_element(*self.locator).click()
            return True
        except Exception as e:
            return False

# 自定义一个显示等待的方法
class window_be_switch_success:
    def __init__(self, handle):
        self.handle = handle

    def __call__(self, driver):
        try:
            driver.switch_to.window(self.handle)
            return True
        except Exception:
            return False