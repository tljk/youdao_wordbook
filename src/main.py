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
import gc
import os
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
        self.nvs = esp32.NVS('Wordbook')
        try:
            self.count = self.nvs.get_i32('curr') - 1
        except:
            self.count = random.randint(100,5000) # the count number traverse to next word
        self.epd.Clear()
        self.epd.fill(0xff)
        
        self.crawlerTSF = uasyncio.ThreadSafeFlag()
        self.epdTSF = uasyncio.ThreadSafeFlag()
        self.lock = uasyncio.Lock()
        self.epdTSF.set()
        self.crawlerTSF.set()

        self.startup = True # force crawler retry when startup

        self.tick = 0
        self.b1 = Pin(12, Pin.IN, Pin.PULL_UP)
        self.b1.irq(trigger=Pin.IRQ_FALLING, handler=lambda t:self.press())
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
                        while not self.wifi.isconnected() and self.wifi.status() not in [15,203,200,204,205,201,202]:
                            await uasyncio.sleep(1)   # not in error status, wait
                            print(self.wifi.status())
                        if self.wifi.isconnected():
                            break
                
                if not self.wifi.isconnected():
                    print('wifi connect failed')
                else:
                    # time
                    import ntptime
                    ntptime.settime()
                    print(self.rtc.datetime())
                    print(os.statvfs('/'))

                    # cookie
                    res = request('GET','http://dict.youdao.com/wordbook/webapi/words', params=wbconfig.param, cookies=wbconfig.cookie)
                    await res.saveYoudao(self.db)

            except BaseException as e:
                import sys
                sys.print_exception(e)
                if self.startup:
                    self.crawlerTSF.set()
            else:
                self.startup = False

            self.db.flush()
            self.lock.release()
            self.wifi.active(False) 
            gc.collect()
    
    def press(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.tick) > 300: # debouncing
            self.epdTSF.set()
        # print(self.tick, now)
        self.tick = now

    async def hiber(self):
        while True:
            await uasyncio.sleep(5)
            if not self.lock.locked():
                print('sleep')
                self.epd.sleep()
                await uasyncio.sleep(0.5)
                machine.lightsleep(1000*60*60)
                # print(machine.wake_reason())
                if machine.wake_reason() == 4:
                    self.crawlerTSF.set()
                else:
                    self.epd.reset()

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
                        await self.epdTSF.wait() # critical point

                        machine.freq(240000000)
                        # print('load data')
                        gc.collect()
                        # print(gc.mem_free())
                        self.epd.frame(index, w[0], ujson.loads(w[1].decode('utf-8')))  
                        self.epd.display_Partial(self.epd.bufferTrans)

                        self.nvs.set_i32('curr',index)
                        self.nvs.commit()
                        self.count = 0
                        machine.freq(80000000)
                        
            except KeyboardInterrupt:
                break
            except BaseException as e:
                import sys
                sys.print_exception(e)

            # self.count = random.randint(100,5000)
