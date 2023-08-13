import json
import os
import subprocess
import sys
import threading
import time

from PIL import Image
from pystray import Icon
from wintoast import ToastNotifier


def is_process_running(process_name):
    try:
        # 配置子进程的启动信息
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # 检查进程是否存在
        task_check = subprocess.check_output(['tasklist', '/fi', 'imagename eq %s' % process_name], startupinfo=startupinfo)
        # print(task_check.decode('gbk'))
        if task_check == b'\xd0\xc5\xcf\xa2: \xc3\xbb\xd3\xd0\xd4\xcb\xd0\xd0\xb5\xc4\xc8\xce\xce\xf1\xc6\xa5\xc5\xe4\xd6\xb8\xb6\xa8\xb1\xea\xd7\xbc\xa1\xa3\r\n':
            return False
        else:
            return True
    except subprocess.CalledProcessError:
        return False


# 创建一个系统托盘图标
def run_icon():
    global icon
    global elapsed_time
    global limit
    # icon = Icon("Health System", image, f"{elapsed_time} / {limit}")
    while True:
        icon = Icon("Health System", image, f"{elapsed_time} / {limit}")
        # t = threading.Thread(target=run_icon, args=(icon,))
        # t.daemon = True
        # t.start()
        # time.sleep(2)
        # icon.stop()
        # t.join()
        e = threading.Timer(60.0, on_exit)
        e.start()
        icon.run()


# def update_title(elapsed_time, limit):
#     global icon
#      = Icon("Health System", image, f"{elapsed_time} / {limit}")

def on_exit():
    icon.stop()


# 获取日期
date = time.strftime('%Y%m%d', time.localtime(time.time()))
# 获取星期
week = int(time.strftime('%w', time.localtime(time.time())))

# 读取json文件
with open('data.json', 'r') as f:
    data = json.load(f)
path = data["path"]
elapsed_time = data["elapsed_time"]
limit = data["limit"]
if data['date'] != date:
    elapsed_time = 0
    if week < 5 or week == 7:
        limit = 20
    else:
        limit = 90
    # 写入json文件
    with open('data.json', 'w') as g:
        data['date'] = date
        data['path'] = path
        data['week'] = week
        data['limit'] = limit
        data["elapsed_time"] = 0
        json.dump(data, g)

# 创建新线程并运行图标
icon_image_path = ".\\icon.ico"
image = Image.open(icon_image_path)
icon = Icon("Health System", image, f"{elapsed_time} / {limit}")
i = threading.Thread(target=run_icon)
i.daemon = True
i.start()

# 打开路径指定的程序
os.startfile(path)
while True:
    # 检查是否正在运行
    if is_process_running('javaw.exe'):
        pass
        # print(f"{elapsed_time} / {limit}")
    else:
        # 写入json文件
        with open('data.json', 'w') as h:
            data["elapsed_time"] = elapsed_time
            json.dump(data, h)
        icon.stop()
        sys.exit()
    if elapsed_time == limit - 10:
        N10_toaster = ToastNotifier()
        N10_toaster.show_toast("Health System",
                               "10 minutes remaining, please arrange the time reasonably!",
                               icon_path=".\\icon.ico",
                               duration=3,
                               threaded=True)
    if elapsed_time == limit:
        full_toaster = ToastNotifier()
        full_toaster.show_toast("Health System",
                                "The limit time has been reached!",
                                icon_path=".\\icon.ico",
                                duration=3,
                                threaded=True)
    if elapsed_time == limit + 10:
        P10_toaster = ToastNotifier()
        P10_toaster.show_toast("Health System",
                               "10 minutes exceeded, please exit!",
                               icon_path=".\\icon.ico",
                               duration=3,
                               threaded=True)
    if elapsed_time == limit + 20:
        P20_toaster = ToastNotifier()
        P20_toaster.show_toast("Health System",
                               "20 minutes exceeded, please exit! Forced exit in 10 minutes!",
                               icon_path=".\\icon.ico",
                               duration=3,
                               threaded=True)
    if elapsed_time >= limit + 30:
        # 结束进程
        subprocess.Popen('taskkill /f /im javaw.exe', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.Popen('taskkill /f /im java.exe', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 通知
        Finish_toaster = ToastNotifier()
        Finish_toaster.show_toast("Health System",
                                  "Exceeded the maximum usage time by 30 minute, forced to exit!",
                                  icon_path=".\\icon.ico",
                                  duration=3)
        icon.stop()
        sys.exit()
    time.sleep(60)
    elapsed_time += 1
