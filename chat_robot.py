'''
文件描述：基于微信公众号实现AI客服
作者：xyc
邮箱：3474442911@qq.com
时间：2019-7-5 16:05
'''

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
import xmltodict
import flask
import urllib.request
import json
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException


app = flask.Flask(__name__)


@app.route("/wx", methods=["GET", "POST"])
def weixin_handler():
    token = "xuyucheng"
    signature = flask.request.args.get("signature")
    timestamp = flask.request.args.get("timestamp")
    nonce = flask.request.args.get("nonce")
    echostr = flask.request.args.get("echostr")

    try:
        # 校验token
        check_signature(token, signature, timestamp, nonce)
    except InvalidSignatureException:
        # 处理异常情况或忽略
        flask.abort(403)  # 校验token失败，证明这条消息不是微信服务器发送过来的
    
    if flask.request.method == "GET":
        return echostr
    elif flask.request.method == "POST":
        print(flask.request.data)
        
        xml_str = flask.request.data
        if not xml_str:
            return ""
        # 对xml字符串进行解析
        xml_dict = xmltodict.parse(xml_str)
        xml_dict = xml_dict.get("xml")

        # 提取消息类型
        msg_type = xml_dict.get("MsgType")
        if msg_type == "text":
            user_msg = xml_dict.get("Content")
            if user_msg in '你是谁？':
                robot_reply = '我是小新，有事您说话！'
            elif user_msg in '你叫什么名字？':
                robot_reply = '我是玉树临风的许遇成'
            elif user_msg in '你们小组编号是什么？':
                robot_reply = '我们组的编号是number one'
            elif user_msg in "你们组的成员有哪些？":
                robot_reply = '我们组成员是：吴永强，李航，许遇成，果越城，万华，张扬，周志勇和彭晨雨'
            elif user_msg in '最新军事新闻头条':
                robot_reply = '最新头条\n\n'
                with urllib.request.urlopen('https://3g.163.com/touch/reconstruct/article/list/BA10TA81wangning/0-10.html') as req:
                    raw_data = req.read()               # 读取所有响应数据
                raw_data = raw_data.decode('utf-8')     # 将字节转化为字符串
                # 去除 "artiList(" 和最后的 ")"
                data = json.loads(raw_data[9:-1])
                data = data['BA10TA81wangning']
                index = 0
                for e in data:
                    if e['source'] != '' and e['title'] != '' and e['url'] != '' and 'http' in e['url']:
                        index += 1
                        robot_reply += '<a href="' + e['url'] + '">' + str(index) + '. ' + e['title']+'</a>\n\n'
            else:
                robot_reply = requests.post('http://api.itmojun.com/chat_robot', {'msg': user_msg}).text
            # 表示发送的是文本消息
            # 构造返回值，经由微信服务器回复给用户的消息内容
            resp_dict = {
                "xml": {
                    "ToUserName": xml_dict.get("FromUserName"),
                    "FromUserName": xml_dict.get("ToUserName"),
                    "CreateTime": int(time.time()),
                    "MsgType": "text",
                    "Content": robot_reply
                }
            }

            # 将字典转换为xml字符串
            resp_xml_str = xmltodict.unparse(resp_dict)
        
            # 返回消息数据给微信服务器
            return resp_xml_str
        else:
            resp_dict = {
                "xml": {
                    "ToUserName": xml_dict.get("FromUserName"),
                    "FromUserName": xml_dict.get("ToUserName"),
                    "CreateTime": int(time.time()),
                    "MsgType": "text",
                    "Content": "I am xiaoxin"
                }
            }
            resp_xml_str = xmltodict.unparse(resp_dict)
            # 返回消息数据给微信服务器
            return resp_xml_str


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="80")

    