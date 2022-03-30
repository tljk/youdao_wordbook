# 有道单词卡
基于微雪2.13墨水屏模块开发，实现单词学习/复习，词库同步有道单词本

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

## 轮子
[framebuf中文](https://github.com/wangshujun-tj/mpy-Framebuf-boost-code)
[cookie支持](https://github.com/mardigras2020/urequests)
[epaper驱动](https://github.com/tljk/2.13inch-e-Paper-Cloud-Module-micropython-driver)
[按键监听](https://github.com/peterhinch/micropython-async/blob/master/aswitch.py)