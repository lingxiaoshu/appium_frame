
import os
import pytest

from common.devices_manage import get_devices

if __name__ == '__main__':
    # 多设备信息的获取
    get_devices()
    # 将命令行输入的命令封装到python脚本中
    # pytest 在python文件中执行
    pytest.main()
    # python 中执行命令行参数
    os.system('allure generate .\\reports\\report -o ./reports/html --clean')


