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


def apple_message(content, description):
    print("发送Apple消息")

    def apple_messaged(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            pushdeer = PushDeer(
                pushkey="PDU12869TGlP0AGWAKJi1mLOpOhsJn105nMk3Hg1V")
            pushdeer.send_text(content, desp=description)
        return wrapper

    print("Done")
    return apple_messaged


def wx_message(content, summary):
    print("发送微信消息")

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

            requests.post(url=url, json=body)
            return func(*args, **kwargs)
        return wrapper
    print("Done")
    return wx_messaged


def main():
    contents = "this is content"
    summarys = "this is summary"
    descriptions = "this is description"

    @apple_message(content=contents, description=descriptions)
    @wx_message(content=contents, summary=summarys)
    def test():
        print("this is test")

    test()


if __name__ == "__main__":
    main()

