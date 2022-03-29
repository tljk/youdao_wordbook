# -*- coding: utf-8 -*-
# @Time    : 2018-11-11 20:04
# @Author  : BruceLong
# @Email   : 18656170559@163.com
# @File    : js逆向有道登录.py
# @Software: PyCharm
'''
分析
url
    https://logindict.youdao.com/login/acc/login

请求方式
    POST

请求参数
     'app': 'web',
    'tp': 'urstoken',
    'cf': 3,
    'fr': 1,
    'product': 'DICT',
    'type': 1,
    'um': 'true',
    'username': username,
    'password': context.aaa,
    'ru': 'http://dict.youdao.com/search?q=as&tab=#keyfrom=${keyfrom}'

js 逆向
1. 寻找关键点 -> 网络请求的一霎那
2. 对网络请求之前的代码进行分析
3. 比较难的js代码可以利用 js2py 让他去执行

'''
import js2py
import requests

url = 'https://logindict.youdao.com/login/acc/login'

context = js2py.EvalJs()

username = ''
password = ''

with open('logincom.js', 'r') as f:
    context.execute(f.read())

context.password = password

js_string = '''
var password = password;
var aaa = hex_md5(password);
'''
# print(js_string)

context.execute(js_string)
print(context.aaa)

# 请求参数
data = {
    'app': 'web',
    'tp': 'urstoken',
    'cf': 3,
    'fr': 1,
    'product': 'DICT',
    'type': 1,
    'um': 'true',
    'username': username,
    'password': context.aaa,
    'ru': 'http://dict.youdao.com/wordbook/webapi/words?limit=10000000&offset=0'
}

context = js2py.EvalJs()
session = requests.Session()

# 模拟浏览器来设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

response = session.post(url, headers=headers, data=data)
cookies = requests.utils.dict_from_cookiejar(session.cookies)
print(cookies)

sessionTest = requests.Session()
sessionTest.cookies = requests.utils.cookiejar_from_dict(cookies)

response = sessionTest.post(url, headers=headers, data=data)

with open('youdao.json', 'wb') as f:
    f.write(response.content)
