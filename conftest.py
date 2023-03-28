import os
import time
from concurrent.futures.thread import ThreadPoolExecutor

from threading import Thread

import pytest
import allure
from PIL import Image, ImageFile

from actions.login import Login

from common.driver import InitDriver, GlobalDriver
from common.file_load import read_yml
from common.server import AppiumServer
from setting import DIR_NAME


# hook函数
def pytest_collection_modifyitems(items):
    # item表示每个测试用例，解决测试用例中名称中文显示问题
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode-escape")
        item._nodeid = item._nodeid.encode("utf-8").decode("unicode-escape")
# 失败截图,两个参数是固定的
@pytest.hookimpl(tryfirst=True, hookwrapper= True)
def pytest_runtest_makereport(item, call):
    # 测试用例完成后，得到结果yield
    outcome = yield
    resp = outcome.get_result()   # 拿到运行结果的测试报告
    # 判断失败的场景，开始截图
    # resp.when测试用例执行的状态：setup（初始化），teardown（结束），call（测试用例执行）是否等于测试用例&失败
    if resp.when == 'call' and resp.failed:
        img = GlobalDriver.driver.get_screenshot_as_png()
        # 失败的报告粘贴到allure报告中
        # allure.attach(读取出来的内容即bytes, 图片的名字， 附件的类型 )
        allure.attach(img, '失败截图', attachment_type=allure.attachment_type.PNG)

'''
fixture 函数可以实现setup的功能，在测试用例之前执行内容，类似初始化
功能更强大，可以任意命名
@pytest.fixture(scope="",autouse=False)
autouse=False:不自动引用
session：pytest发起请求到结束，只会执行一次（命令行发起pytest请求）
function：函数级别的测试用例和方法级别的测试用例执行一次
class：引用fixture函数的class类，就会执行一次
module:引用fixture函数的python文件，就会执行一次

引用：把fixture装饰的函数的名字当做参数传递到测试用例中调用即可
teardown在conftest.py中如何实现？
只需要yield这个关键字，关键字后写测试用例结束之后需要执行的内容
'''

# 用fixture()方法来写setup和teardown
@pytest.fixture(scope= 'session', autouse= True)
def init_driver(devices_info,worker_id):
    # 从devices_info中获取port和chromedriverPort这两个参数
    port = devices_info['port']
    chromedriverPort = devices_info['chromedriverPort']
    # 启动appium服务-创建driver(需要连接appium服务)
    # appium服务的启动->在执行测试用例之前
    # 多线程去执行->启动appium服务
    tpe = ThreadPoolExecutor()
    # tpe.submit(AppiumServer().start)
    tpe.submit(AppiumServer().start, port, chromedriverPort)
    # 创建Initdriver的对象
    GlobalDriver.driver = InitDriver(devices_info, worker_id)
    yield  # teardown的含义
    GlobalDriver.driver.quit()
    # 所有测试用例执行之后->appium服务就可以停掉
    AppiumServer().stop(port)
@pytest.fixture(scope='function', autouse=True)
def case_setup_teardown(worker_id):
    # 生成动态图时候可能会报错：一些文件被占用
    # 解决办法：加以下这行代码
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    # 截图-多线程去执行截图的任务
    th = Thread(target=shot, args=(GlobalDriver.driver, worker_id))
    # 启动线程
    th.start()

    yield  # 实现teardown的作用含义
    # 1列举所有的图片
    imges_list = os.listdir('video')
    new_list = []
    for img_name in imges_list:
        if img_name.startswith(worker_id) and img_name.endswith('.png'):
            new_list.append(img_name)
    # 2排序
    # 单任务master0.png master1 master2
    if worker_id == 'master':
        new_list.sort(key=lambda x: int(x[6:-4]))
    else:  # 多任务  gw01.png,gw11.png
        new_list.sort(key=lambda x: int(x[3:-4]))
    # 3.拼接gif图
    # pip install pillow
    # 3.1 首先拿到第一张图片
    first_img = Image.open(os.path.join('video', new_list[0]))
    # 3.2拿第一张图片与剩余的其他图片进行拼接
    other_imgs = []  # 其他.png要经过Image.open()进行转换才可以
    for i in new_list[1:]:
        fb = Image.open(os.path.join('video', i))
        other_imgs.append(fb)
    # 保存最终的gif图
    first_img.save(DIR_NAME + f'/video/{worker_id}_record.gif',  # 路径
                   append_images=other_imgs,
                   duration=300,
                   save_all=True,
                   loop=0)  # 持续播放
    time.sleep(2)
    # 4.gif图贴到allure报告中
    with open(DIR_NAME + f'/video/{worker_id}_record.gif', 'rb') as f:
        content = f.read()
        allure.attach(content, '测试用例播放图', attachment_type=allure.attachment_type.GIF)
    # 测试用例结束后返回首页
    GlobalDriver.driver.start_activity('com.douban.frodo', 'com.douban.frodo.activity.SplashActivity')
    # 清空数据,否则第二次不会从首页开始
    GlobalDriver.driver.reset_app()
    time.sleep(3)

def shot(dr, worker_id):
    '''
    不断的截图
    :return:
    兼容性：不同的浏览器运行，多进程去运行
    worker_id: 名字是固定的，pytest底层已封装；单进程任务时，worker_id = master
    多任务执行时，worker_id = gw0，gw1，gw2……
    '''
    # 每条测试用例执行之前将video中的所有图片先清空
    img_lists = os.listdir('video')
    for img_name in img_lists:
        if img_name.startswith(worker_id) and img_name.endswith('.png'):
            # 删除包里面的文件内容
            os.remove('video/'+img_name)
    n = 0
    while True:
        try:
            dr.get_screenshot_as_file(DIR_NAME+f'/video/{worker_id}{n}.png')  # 图片名字动态变化
        except:
            return  # 截图失败退出循环
        # 每隔0.2s开始截图
        time.sleep(0.2)
        # 增量
        n += 1
# 增加命令行参数   --devices-file
def pytest_addoption(parser):
    parser.addoption('--devices-file', action='store')

# 获取命令行参数传递过来的值
@pytest.fixture(scope='session')
def devices_info(request, worker_id):
    devices_file = request.config.getoption('--devices-file')
    devices_info = read_yml(devices_file)
    # 如果是多设备，那么需要用多进程进行启动  pytest-xdist这个插件  worker_id gw0gw1
    # 单设备  单进程  worker_id master
    if worker_id == 'master':
        return devices_info[0]
    else:   # 多设备
        num = int(worker_id[2:])
        return devices_info[num]
