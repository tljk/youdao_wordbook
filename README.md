# 有道单词卡
基于微雪2.13墨水屏模块开发，实现单词学习/复习，词库同步有道单词本  
![demo.gif](https://github.com/tljk/youdao_wordbook/blob/master/demo.gif)  

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

## 将要实现
复习模式，记录单词复习情况（记得/不记得），根据记录选择复习的单词  
添加模式（学习模式），向有道单词本及本地数据添加单词  
联网释义  
音标显示  
状态显示  
休眠唤醒  

## 轮子
[framebuf中文](https://github.com/wangshujun-tj/mpy-Framebuf-boost-code)  
[cookie支持](https://github.com/mardigras2020/urequests)  
[epaper驱动](https://github.com/tljk/2.13inch-e-Paper-Cloud-Module-micropython-driver)  
[按键监听](https://github.com/peterhinch/micropython-async/blob/master/aswitch.py)  
[有道登录](https://github.com/WYL-BruceLong/Spider_JS_ReverseParsin)  