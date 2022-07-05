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
import phonetic
import framebuf
import gc

from machine import Pin
from urequests import request
from epd import EPD_2in13_V3
from db import DB
class Wordbook:
    def __init__(self):
        self.epd = EPD_2in13_V3()
        self.db = DB()
        self.count = random.randint(100,5000)
        self.epd.Clear()
        self.epd.fill(0xff)
        self.switch = True
        self.update = False
        self.lock = uasyncio.Lock()
        self.word = ''

    # wifi
    async def crawler(self):
        while True:
            await uasyncio.sleep(0)
            while not self.lock.locked():
                await uasyncio.sleep(0)
            
            try:
                self.wifi = network.WLAN(network.STA_IF)
                self.wifi.active(True) 
                wifiList = self.wifi.scan()

                for w in wifiList:
                    w = w[0].decode('utf-8')
                    if w in wbconfig.wifi:
                        print('start to connect: '+w)
                        self.wifi.connect(w,wbconfig.wifi[w])
                        retry_times = 60
                        while not self.wifi.isconnected() and retry_times > 0:
                            print("wifi retry: " , 60-retry_times+1)
                            await uasyncio.sleep(1)
                            retry_times -= 1
                        if self.wifi.isconnected():
                            print('wifi init: '+str(self.wifi.ifconfig()))
                            break

                if not self.wifi.isconnected():
                    print('wifi connect failed')
                else:
                    # crawler
                    param={
                        'limit': '1000000',
                        'offset': ''
                    }
                    # cookie
                    cookie = wbconfig.cookie
                    # try:
                    res = request('GET','http://dict.youdao.com/wordbook/webapi/words', params=param, cookies=cookie)
                    await res.saveYoudao(self.db)
                    # except BaseException as e:
                    #     # self.lock.release()
                    #     # self.wifi.active(False) 
                    #     print('crawler failed')                        
                    # self.db.flush()

            except BaseException as e:
                import sys
                sys.print_exception(e)

            self.update = True
            self.db.flush()
            self.db.close()
            self.db = DB()
            self.lock.release()
            self.wifi.active(False) 
            gc.collect()
    
    def press(self):
        self.switch = True

    async def wake(self):
        await self.lock.acquire()

    # button
    async def button(self):
        self.b1 = Pin(12, Pin.IN, Pin.PULL_UP)
        self.b1.irq(trigger=Pin.IRQ_FALLING, handler=lambda t:self.press())
        import esp32
        esp32.wake_on_ext0(pin = self.b1, level = esp32.WAKEUP_ALL_LOW)
        print('button init')

        while True:
            await uasyncio.sleep(0)
            
            try:
                for w in self.db.data.items():
                    if self.word != w and self.word != '':
                        self.count = 1
                    elif self.word == w:
                        self.count = 1
                        self.word = ''

                    if self.count != 0:
                        self.count -= 1
                    else:
                        # print('load data')
                        gc.collect()
                        json = ujson.loads(w[1].decode('utf-8'))

                        self.epd.fill(0xff)
                        self.epd.font_set(0x23,0,1,0)
                        self.epd.text(w[0], 0, 0, 0x00)

                        offset = 4
                        for c in json['phonetic']:
                            if phonetic.font.get(c):
                                font_buf = bytearray(phonetic.font.get(c))
                                font_framebuffer = framebuf.FrameBuffer(font_buf, len(font_buf)//3, 24, framebuf.MONO_HLSB)
                                self.epd.blit(font_framebuffer, len(w[0])*12+offset, 0)
                                if c in '(),-.:;[]ˈˌː':
                                    offset+=4
                                elif c in 'mwæ':
                                    offset+=12
                                else:
                                    offset+=len(font_buf)//3
                        
                        count = len(json['trans'].encode())
                        length = len(json['trans'])
                        
                        y = (count - length)//2
                        x = length - y

                        count = x + 2 * y

                        self.epd.font_set(0x03,0,1,0)
                        
                        # font24 10 * 4 = 40
                        # font16 15 * 6 = 90
                        # font12 20 * 8 = 160
                        composeSet = {}
                        if count < (10) * 4 * 2:
                            self.epd.font_set(0x23,0,1,0)
                            composeSet = {'size': 24, 'width': 10, 'height': 4}
                        elif count < (15) * 6 * 2:
                            self.epd.font_set(0x22,0,1,0)
                            composeSet = {'size': 16, 'width': 15, 'height': 6}
                        elif count < (20) * 8 * 2:
                            self.epd.font_set(0x21,0,1,0)
                            composeSet = {'size': 12, 'width': 20, 'height': 8}
                        else:
                            self.epd.font_set(0x21,0,1,0)
                            composeSet = {'size': 12, 'width': 20, 'height': 8}
                        
                        start=0 
                        end=0
                        for i in range(composeSet['height']):
                            offset = (composeSet['width']*3 - len(json['trans'][start:start+composeSet['width']].encode()))//3 - 1
                            end = start + composeSet['width'] + offset
                            self.epd.text(json['trans'][start:end], 0, 25 + composeSet['size'] * i, 0x00)
                            start=end

                        self.epd.display_Partial(self.epd.buffer)

                        machine.freq(80000000)
                        while not self.switch:
                            await uasyncio.sleep(0)
                            if not self.lock.locked():
                                print('sleep')
                                await uasyncio.sleep(0.1)
                                machine.lightsleep(1000*60*60)
                                # print(machine.wake_reason())
                                if machine.wake_reason() == 4:
                                    await self.wake()

                        machine.freq(240000000)
                        self.epd.TurnOnDisplayPart()
                        self.switch = False
                        self.count = 1

                        if self.update:
                            while self.lock.locked():
                                await uasyncio.sleep(0.1)
                            self.update = False
                            self.word = w
                            self.count = random.randint(100,5000)
                            break

            except BaseException as e:
                import sys
                sys.print_exception(e)

            self.count = random.randint(100,5000)
