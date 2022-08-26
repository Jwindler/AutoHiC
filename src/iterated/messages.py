#!/usr/bin/env python 
# encoding: utf-8 

"""
@author: Swindler
@contact: 1033199817@qq.com
@file: messages.py
@time: 7/4/22 8:50 PM
@function: 给微信和Apple推送消息
"""

from pypushdeer import PushDeer
import requests
import subprocess
import time


def apple_message(content, description):
    def apple_messaged(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            pushdeer = PushDeer(
                pushkey="PDU12869TGlP0AGWAKJi1mLOpOhsJn105nMk3Hg1V")
            pushdeer.send_text(content, desp=description)

        return wrapper

    return apple_messaged


def wx_message(content, summary):
    def wx_messaged(func):
        def wrapper(*args, **kwargs):
            url = "https://wxpusher.zjiecode.com/api/send/message"

            body = {
                "appToken": "AT_Q0LzIJC0n1DTzJ26ibZ5vgEOdVmk6VDP",
                "content": content,
                "summary": summary,
                "Content-Type": 1,
                "topicIds": [
                    123
                ],
                "uids": [
                    "UID_jnK5ljLroAFngcHhBDU5xiZKzssX"
                ],
                "url": "https://wxpusher.zjiecode.com"
            }
            func(*args, **kwargs)
            requests.post(url=url, json=body)

        return wrapper

    return wx_messaged


# 既可以判断执行是否成功，还可以获取执行结果
def subprocess_popen(statement):
    p = subprocess.Popen(statement, shell=True, stdout=subprocess.PIPE)  # 执行shell语句并定义输出格式
    while p.poll() is None:  # 判断进程是否结束（Popen.poll()用于检查子进程（命令）是否已经执行结束，没结束返回None，结束后返回状态码）
        if p.wait() is not 0:  # 判断是否执行成功（Popen.wait()等待子进程结束，并返回状态码；如果设置并且在timeout指定的秒数之后进程还没有结束，将会抛出一个TimeoutExpired异常。）
            print("命令执行失败，请检查设备连接状态")
            return False
        else:
            re = p.stdout.readlines()  # 获取原始执行结果
            result = []
            for i in range(len(re)):  # 由于原始结果需要转换编码，所以循环转为utf8编码并且去除\n换行
                res = re[i].decode('utf-8').strip('\r\n')
                result.append(res)
            return result[0]


def main():
    contents = "Test Run Completed"  # Apple通知Title
    summarys = "Test Result"  # 微信消息通知Title

    descriptions = "Test Run Completed"  # 通知内容

    job_id = "11319"

    # Shell命令
    statement = "ps -ef|awk '{print $2}' | grep " + job_id + " | wc -l"

    @apple_message(content=contents, description=descriptions)
    @wx_message(content=contents, summary=summarys)
    def test():
        while True:
            task_state = subprocess_popen(statement)
            if task_state == "1":
                time.sleep(600)  # 任务运行中，每隔10分钟检查一次
            else:
                print("任务已经完成")
                break

    test()


if __name__ == "__main__":
    main()
