[toc]

## js逆向解析之有道登录

> js 逆向
1. 寻找关键点 -> 网络请求的一霎那
2. 对网络请求之前的代码进行分析
3. 比较难的js代码可以利用 js2py 让他去执行

### 项目需求分析
> 
实现有道登录以下是登录网址：
http://account.youdao.com/login?service=dict&back_url=http%3A%2F%2Fdict.youdao.com%2Fsearch%3Fq%3Das%26tab%3D%23keyfrom%3D%24%7Bkeyfrom%7D

### 爬虫的分析思路
- url
   ` https://logindict.youdao.com/login/acc/login`

- 请求方式
    `POST`

- 请求参数
    ```python
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
    ```
    
- 请求头
	` 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'`
    
### 详细分析（图文版）
#### 第一步：把网址copy到浏览器，进入后按f12进入控制台

![QQ截图20181111224331.jpg](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/QQ%E6%88%AA%E5%9B%BE20181111224331.jpg)


#### 第二步：故意输入一个错误的密码查看控制台的变化并找到post请求的网页接口分析

![1.jpg](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/1.jpg)

- 登录接口和请求方式

![QQ截图20181111224951.jpg](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/QQ%E6%88%AA%E5%9B%BE20181111224951.jpg)

- 请求参数

![2.png](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/2.png)


### 找到js入口，分析加密方式
####  方法一
- 回退一下到登录页面，找到form里有用的参数这里以`validate`为关键字参数
![20181111225620.png](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/20181111225620.png)

- 运用google浏览器实现搜索

![QQ截图20181111225833.jpg](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/QQ%E6%88%AA%E5%9B%BE20181111225833.jpg)

- 找到对应的函数，并对js进行优化输出

![QQ截图20181111225947.jpg](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/QQ%E6%88%AA%E5%9B%BE20181111225947.jpg)

- 找到加密的方法，并打上断点进行调试

![QQ截图20181111230101.jpg](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/QQ%E6%88%AA%E5%9B%BE20181111230101.jpg)

- 找出`hex_md5`对应的js文件，保存下来

![QQ截图20181111230943.jpg](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/QQ%E6%88%AA%E5%9B%BE20181111230943.jpg)

![QQ截图20181111231149.jpg](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/QQ%E6%88%AA%E5%9B%BE20181111231149.jpg)


- 方法二
- 直接用加密的参数名也就是`请求参数`里的`password`进行全局搜索和方法一的前三步相同
- 这样也能找到相应的参数总共有13个password这里是第`12个位置`的password
![QQ截图20181111231620.jpg](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin/blob/master/images/QQ%E6%88%AA%E5%9B%BE20181111231620.jpg)


### 完整的实现代码
```python

# 导入使用的模块
import js2py
import requests

# 请求的url接口地址
url = 'https://logindict.youdao.com/login/acc/login'

# 利用js2py构造一个上下文中间变量
context = js2py.EvalJs()

# 需要登录的用户名和密码
username = 'username@163.com'
password = 'pasword'

# 需要执行加密的已下载的js文件
with open('logincom.js', 'r') as f:
    context.execute(f.read())

# 把密码放在js中间变量
context.password = password

# 需要执行的js代码，这里我自己改了，感觉没有必要用那么多参数，里面的aaa我任意定义的
js_string = '''
var aaa = hex_md5(password);
'''
# print(js_string)

context.execute(js_string)
# 打印测试加密后的密码数据
print(context.aaa)

# 请求参数（把构造后的完整的请求参数放到data字典中去）
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
    'ru': 'http://dict.youdao.com/search?q=as&tab=#keyfrom=${keyfrom}'
}

# 设置请求头，模拟浏览器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

response = requests.post(url, headers=headers, data=data)

# 把解析后的数据保存在youdao.html
with open('youdao.html', 'wb') as f:
    f.write(response.content)

```
