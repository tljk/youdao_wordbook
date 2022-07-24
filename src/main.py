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
import time
import esp32

from machine import Pin, RTC
from urequests import request
from epd import EPD_2in13_V3
from db import DB
class Wordbook:
    def __init__(self):
        self.epd = EPD_2in13_V3()
        self.db = DB()
        self.rtc = RTC()
        self.count = random.randint(100,5000) # the count number traverse to next word
        self.epd.Clear()
        self.epd.fill(0xff)
        self.word = ''
        
        self.crawlerTSF = uasyncio.ThreadSafeFlag()
        self.epdTSF = uasyncio.ThreadSafeFlag()
        self.lock = uasyncio.Lock()
        self.epdTSF.set()
        self.crawlerTSF.set()

        self.startup = True # auto crawler retry when startup
        self.pause = 10 # time to sleep when no action

        self.tick = 0
        self.b1 = Pin(12, Pin.IN, Pin.PULL_UP)
        self.b1.irq(trigger=Pin.IRQ_RISING, handler=lambda t:self.press())
        esp32.wake_on_ext0(pin = self.b1, level = esp32.WAKEUP_ALL_LOW)
        print('button init')
        
    # wifi
    async def crawler(self):
        while True:
            await self.crawlerTSF.wait() # critical point
            await self.lock.acquire()
            
            try:
                self.wifi = network.WLAN(network.STA_IF)
                self.wifi.active(True) 
                wifiList = self.wifi.scan()

                for w in wifiList:
                    w = w[0].decode('utf-8')
                    if w in wbconfig.wifi:
                        print('start to connect: '+w)
                        self.wifi.config(reconnects=2)
                        self.wifi.connect(w,wbconfig.wifi[w])
                        while not self.wifi.isconnected() and self.wifi.status() not in [203,200,204,201,202]:
                            await uasyncio.sleep(1)   # not in error status, wait
                            print(self.wifi.status())
                        if self.wifi.isconnected():
                            break
                
                await uasyncio.sleep(3) 
                if not self.wifi.isconnected():
                    print('wifi connect failed')
                else:
                    # time
                    import ntptime
                    ntptime.settime()
                    print(self.rtc.datetime())
                    # crawler
                    param={
                        'limit': '1000000',
                        'offset': ''
                    }
                    # cookie
                    cookie = wbconfig.cookie
                    res = request('GET','http://dict.youdao.com/wordbook/webapi/words', params=param, cookies=cookie)
                    await res.saveYoudao(self.db)

            except BaseException as e:
                import sys
                sys.print_exception(e)
                if self.startup:
                    self.crawlerTSF.set()
            else:
                self.startup = False

            self.pause = 10
            self.db.flush()
            self.lock.release()
            self.wifi.active(False) 
            gc.collect()
    
    def press(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.tick) > 300: # jitter
            self.epdTSF.set()
        # print(self.tick, now)
        self.tick = now

    async def hiber(self):
        while True:
            await uasyncio.sleep(1)
            if not self.lock.locked():
                if self.pause > 0:
                    self.pause -= 1
                else:
                    print('sleep')
                    await uasyncio.sleep(0.5)
                    machine.lightsleep(1000*60*60)
                    # print(machine.wake_reason())
                    if machine.wake_reason() == 4:
                        self.crawlerTSF.set()

    async def screen(self):
        print('screen init')

        while True:
            await uasyncio.sleep(0)
            index = 0
            try:
                for w in self.db.data.items():
                    index += 1

                    if self.count > 0:
                        self.count -= 1
                    else:
                        # print('load data')
                        gc.collect()
                        json = ujson.loads(w[1].decode('utf-8'))

                        # word and index
                        self.epd.fill(0xff)
                        self.epd.font_set(0x23,0,1,0)
                        self.epd.text(w[0], 0, 0, 0x00)                                                
                        self.epd.font_set(0x21,0,1,0)
                        self.epd.text(str(index),250-len(str(index))*6,110,0x00)

                        # phonetic
                        offset = 4
                        for c in json['p']:
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

                        # trans font selection
                        count = len(json['t'].encode())
                        length = len(json['t'])
                        y = (count - length)//2
                        x = length - y
                        count = x + 2 * y

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

                        # trans each line
                        curr = 0
                        for i in range(composeSet['height']):
                            line = ''
                            count = composeSet['width']*2
                            while curr < len(json['t']):
                                if len(json['t'][curr].encode()) == 3:
                                    count -= 2
                                else:
                                    count -= 1
                                if count < 0:
                                    break
                                line += json['t'][curr]
                                curr += 1
                            self.epd.text(line, 0, 25 + composeSet['size'] * i, 0x00)
                            if curr >= len(json['t']):
                                break
                            # print(line)

                        self.epd.display_Partial(self.epd.buffer)
                        self.pause = 10
                        machine.freq(80000000)

                        await self.epdTSF.wait() # critical point

                        machine.freq(240000000)
                        self.epd.TurnOnDisplayPart()
                        self.count = 0
                        
            except KeyboardInterrupt:
                break
            except BaseException as e:
                import sys
                sys.print_exception(e)

            # self.count = random.randint(100,5000)
