# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network
import ujson
import uasyncio
import random
import ure
import wbconfig

from machine import Pin
from urequests import request
from epd import EPD_2in13_V3
from aswitch import Pushbutton
from db import DB

class Wordbook:
    def __init__(self):
        self.epd = EPD_2in13_V3()
        self.db = DB()
        self.count = random.randint(1,100)
        self.epd.Clear()
        self.epd.fill(0xff)
    
    def short(self):
        print('short press')
        self.epd.switch = True
    
    def double(self):
        print('double press')

    def long(self):
        print('long press')

    # wifi
    async def crawler(self):
        self.wifi = network.WLAN(network.STA_IF)
        if not self.wifi.isconnected():
            self.wifi.active(True) 
            self.wifi.connect('loops','quanquan')
            retry_times = 30
            while not self.wifi.isconnected() and retry_times > 0:
                print("wifi retry: " , 30-retry_times+1)
                await uasyncio.sleep(2)
                retry_times -= 1
            if not self.wifi.isconnected():
                self.wifi.active(False)
                raise Exception('wifi connect failed')
            print('wifi init: '+str(self.wifi.ifconfig()))

        param={
            'limit': '1000000',
            'offset': ''
        }
        # cookie
        cookie = wbconfig.cookie

        res = request('GET','http://dict.youdao.com/wordbook/webapi/words', params=param, cookies=cookie)
        await res.saveYoudao()
        self.wifi.active(False) 
            
    # button
    async def button(self):
        self.b1 = Pin(12, Pin.IN, Pin.PULL_UP)
        self.pb = Pushbutton(self.b1,suppress=True)
        self.pb.release_func(self.short, ())
        self.pb.double_func(self.double, ())
        self.pb.long_func(self.long, ())
        self.b1.irq(trigger=Pin.IRQ_FALLING, handler=lambda t:self.pb.press())
        print('button init')

        while True:
            await uasyncio.sleep(0)
            for i in self.db.values():
                if self.count != 0:
                    self.count -= 1
                else:
                    json = ujson.loads(i.decode('utf-8'))

                    self.epd.fill(0xff)
                    self.epd.font_set(0x23,0,1,0)
                    self.epd.text(json['word'], 0, 0, 0x00)
                    
                    trans = json['trans'].replace(' ', '')
                    count = 0
                    for c in trans:
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
                    if count < 10 * 4 * 2:
                        self.epd.font_set(0x23,0,1,0)
                        composeSet = {'size': 24, 'width': 10, 'height': 4}
                    elif count < 15 * 6 * 2:
                        self.epd.font_set(0x22,0,1,0)
                        composeSet = {'size': 16, 'width': 15, 'height': 6}
                    elif count < 20 * 8 * 2:
                        self.epd.font_set(0x21,0,1,0)
                        composeSet = {'size': 12, 'width': 20, 'height': 8}
                    else:
                        self.epd.font_set(0x21,0,1,0)
                        composeSet = {'size': 12, 'width': 20, 'height': 8}
                        
                    lines = []
                    line = ''
                    count = 0
                    for c in trans:
                        if c < '\u0080':
                            # ascii
                            if count + 1 <= (composeSet['width']) * 2 - 1:
                                count += 1
                            else:
                                lines.append(line)
                                line = ''
                                count = 0
                        else:
                            if count + 2 <= (composeSet['width']) * 2 - 1:
                                count += 2
                            else:
                                lines.append(line)
                                line = ''
                                count = 0
                        line += c
                    lines.append(line)
                    
                    for i,l in enumerate(lines):
                        # print(l)
                        self.epd.text(l, 0, 24 + composeSet['size'] * i, 0x00)

                    await self.epd.display_Partial(self.epd.buffer)
                    self.count = random.randint(1,100)

async def main():
    wb = Wordbook()
    await uasyncio.gather(wb.button(),wb.crawler())

    # end
    wb.epd.sleep()
    wb.epd.font_free()
    wb.db.close()
    wb.wifi.active(False) 

uasyncio.run(main())