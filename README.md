# 有道单词卡
基于微雪2.13墨水屏模块开发，实现单词学习/复习，词库同步有道单词本  
[![cover.png](https://github.com/tljk/youdao_wordbook/blob/master/cover.png)](https://www.bilibili.com/video/BV1yv4y1M7Wo)  

## 前言
单词本里加了很多的单词，但是不见得就去复习  
所以就有了一个idea，一个随身携带可以同步的墨水屏单词本设备，结合墨水屏特性(低功耗，持久显示)利用碎片时间复习  
市面上已经出现了类似的产品，也更便宜更成熟，但是有道的一套用的很久了，并不想转到新的平台，于是乎就有了这个尝试  
  
目前的定位是能同步有道个人单词本的单词复习工具  
## 已经实现
联网爬取有道账号下单词本列表  
btree保存  
根据随机数遍历随机次实现随机单词  
显示单词释义，排版切换字体  
异步执行按键监听和爬虫  
休眠唤醒  
使用有道桌面版或者web版可以更新内容
音标显示

## 将要实现
复习模式，记录单词复习情况（记得/不记得），根据记录选择复习的单词    
联网释义    
状态显示  
同步删除  

## 使用模块
![](http://www.waveshare.net/photo/LCD/2.13inch-e-Paper-Cloud-Module/2.13inch-e-Paper-Cloud-Module-1.jpg)  
https://www.waveshare.net/shop/2.13inch-e-Paper-Cloud-Module.htm

## 安装
1. 下载  
   本仓库  
   模块驱动并安装
2. 连接模块，在设备管理器中显示  
3. 刷入镜像  
   python环境，安装工具包  
   `pip install esptool`  
   清除flash，COM4对应着设备端口号  
   `esptool.py --port COM4 erase_flash`  
   刷入对应镜像  
   `esptool.py --chip esp32 --port COM4 write_flash -z 0x1000 esp32_1.17_fb_boost_4M_ULAB.bin`  
   新增1.19.1，执行效率高，预留空间更大   
4. 修改配置  
   切换到Spider_JS_ReverseParsin  
   `cd Spider_JS_ReverseParsin`  
   安装依赖  
   `pip install -r requirements.txt`  
   获取有道cookie  
   `python js逆向有道登录1.py`  
   成功后会打印账号对应cookie以及生成单词数据文件youdao.json  
   将cookie填入wbconfig.py中"cookie="后  
   修改wifi ssid和密码  
5. 预编译  
   `pip install mpy-cross==1.18`  
   执行build.bat  
   或者使用mpy-cross对boot.py除外的所有py文件执行编译  
     
   如果报错mpy-cross版本不兼容，需要重新安装对应版本重新编译  
   v5对应1.18及以下  
   v6对应1.19及以上  
   
6. 上传代码  
   安装vscode 安装Pymakr插件  
   使用vscode打开/build文件夹(编译后)  
   连接并upload代码  
     
   参考[在vscode里基于Pymakr插件进行esp32的micropython开发](https://www.bilibili.com/read/cv7262936)  

## 外壳
![cover.png](https://github.com/tljk/youdao_wordbook/blob/master/shell.png)  
模型文件：[shell2 v8.f3d](https://github.com/tljk/youdao_wordbook/blob/master/shell2_v8.f3d), [shell2 v8.stl](https://github.com/tljk/youdao_wordbook/blob/master/shell2_v8.stl)  
壁面很薄，打印请使用刚性树脂，周围添加支撑

## 已知问题
1. OSError 28，空间不足或者data文件损坏
## 鸣谢
[framebuf中文](https://github.com/wangshujun-tj/mpy-Framebuf-boost-code)  
[cookie支持](https://github.com/mardigras2020/urequests)  
[epaper驱动](https://github.com/tljk/2.13inch-e-Paper-Cloud-Module-micropython-driver)  
[有道登录](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin)  