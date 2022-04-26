# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network
import ujson
import uasyncio
import random
import wbconfig
import machine
import os

from machine import Pin
from urequests import request
from epd import EPD_2in13_V3
from aswitch import Pushbutton
from db import DB
from log import logToFile

class Wordbook:
    def __init__(self):
        self.epd = EPD_2in13_V3()
        self.db = DB()
        self.count = random.randint(100,5000)
        self.epd.Clear()
        self.epd.fill(0xff)
        self.switch = True

        self.word = ''
    
    def short(self):
        print('short press')
        self.switch = True
    
    def double(self):
        print('double press')

    def long(self):
        print('long press')
        self.db.record(self.word)
        self.switch = True

    # wifi
    async def crawler(self):
        await self.pb.crawlerLock.acquire()
        self.wifi = network.WLAN(network.STA_IF)
        if not self.wifi.isconnected():
            self.wifi.active(True) 
            wifiList = self.wifi.scan()
            for w in wifiList:
                w = w[0].decode('utf-8')
                if w in wbconfig.wifi:
                    print('start to connect: '+w)
                    self.wifi.connect(w,wbconfig.wifi[w])
                    retry_times = 10
                    while not self.wifi.isconnected() and retry_times > 0:
                        print("wifi retry: " , 10-retry_times+1)
                        await uasyncio.sleep(1)
                        retry_times -= 1
                    if self.wifi.isconnected():
                        print('wifi init: '+str(self.wifi.ifconfig()))
                        break
            else:
                if not self.wifi.isconnected():
                    self.wifi.active(False)
                    self.pb.crawlerLock.release()
                    raise Exception('wifi connect failed')

        # crawler
        param={
            'limit': '1000000',
            'offset': ''
        }
        # cookie
        cookie = wbconfig.cookie
        try:
            res = request('GET','http://dict.youdao.com/wordbook/webapi/words', params=param, cookies=cookie)

            await res.saveYoudao(self.db)
            self.db.flush()
        except BaseException as e:
                print('crawler failed '+str(e.args))
        finally:
            self.wifi.active(False) 
            self.pb.crawlerLock.release()
            
    # button
    async def button(self):
        self.b1 = Pin(12, Pin.IN, Pin.PULL_UP)
        self.pb = Pushbutton(self.b1,suppress=True)
        self.pb.release_func(self.short, ())
        self.pb.double_func(self.double, ())
        self.pb.long_func(self.long, ())
        # self.b1.irq(trigger=Pin.IRQ_FALLING, handler=lambda t:self.pb.press())
        import esp32
        esp32.wake_on_ext0(pin = self.b1, level = esp32.WAKEUP_ALL_LOW)
        print('button init')

        while True:
            await uasyncio.sleep(0)
            try:
                for i in self.db.values():
                    if self.count != 0:
                        self.count -= 1
                    else:
                        print('load data')
                        json = ujson.loads(i.decode('utf-8'))

                        self.epd.fill(0xff)
                        self.epd.font_set(0x23,0,1,0)
                        self.epd.text(json['word'], 0, 0, 0x00)
                        
                        count = 0
                        for c in json['trans']:
                            if c < '\u0080':
                                # ascii
                                count += 1
                            else:
                                count += 2

                        self.epd.font_set(0x03,0,1,0)
                        
                        # font24 10 * 4 = 40
                        # font16 15 * 6 = 90
                        # font12 20 * 8 = 160
                        composeSet = {}
                        if count < (10 - 1) * 4 * 2:
                            self.epd.font_set(0x23,0,1,0)
                            composeSet = {'size': 24, 'width': 10, 'height': 4}
                        elif count < (15 - 1) * 6 * 2:
                            self.epd.font_set(0x22,0,1,0)
                            composeSet = {'size': 16, 'width': 15, 'height': 6}
                        elif count < (20 - 1) * 8 * 2:
                            self.epd.font_set(0x21,0,1,0)
                            composeSet = {'size': 12, 'width': 20, 'height': 8}
                        else:
                            self.epd.font_set(0x21,0,1,0)
                            composeSet = {'size': 12, 'width': 20, 'height': 8}
                            
                        lines = []
                        line = ''
                        count = 0
                        for c in json['trans']:
                            if c < '\u0080':
                                # ascii
                                if count + 1 <= (composeSet['width'] - 1) * 2:
                                    count += 1
                                else:
                                    lines.append(line)
                                    line = ''
                                    count = 0
                            else:
                                if count + 2 <= (composeSet['width'] - 1) * 2:
                                    count += 2
                                else:
                                    lines.append(line)
                                    line = ''
                                    count = 0
                            line += c
                        lines.append(line)
                        
                        for i,l in enumerate(lines):
                            # print(l)
                            self.epd.text(l, 0, 25 + composeSet['size'] * i, 0x00)

                        self.epd.display_Partial(self.epd.buffer)
                        if self.pb.epdLock.locked():
                            self.pb.epdLock.release()

                        machine.freq(80000000)
                        while not self.switch:
                            await uasyncio.sleep(0)
                        machine.freq(240000000)

                        self.epd.TurnOnDisplayPart()
                        await self.pb.epdLock.acquire()
                        self.switch = False

                        self.count = 1
                        self.word = json['word']
                        
            except BaseException as e:
                print('exit unexpected '+str(e.args))
                self.count = 100

async def main():
    # Begin loging to file
    os.dupterm(logToFile())
    
    wb = Wordbook()
    await uasyncio.gather(wb.button(),wb.crawler())

    # end
    wb.epd.sleep()
    wb.epd.font_free()
    wb.db.close()
    wb.wifi.active(False) 

    # Stop loging to file
    os.dupterm(None)

uasyncio.run(main())