# *****************************************************************************
# * | File        :   Pico_ePaper-2.13_V3.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-11-01
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from machine import Pin, SPI
import framebuf
import utime
import network
import uasyncio
import machine
from micropython import const

byte_filp = [0x0, 0x80, 0x40, 0xc0, 0x20, 0xa0, 0x60, 0xe0, 0x10, 0x90, 0x50, 0xd0, 0x30, 0xb0, 0x70, 0xf0, 0x8, 0x88, 0x48, 0xc8, 0x28, 0xa8, 0x68, 0xe8, 0x18, 0x98, 0x58, 0xd8, 0x38, 0xb8, 0x78, 0xf8, 0x4, 0x84, 0x44, 0xc4, 0x24, 0xa4, 0x64, 0xe4, 0x14, 0x94, 0x54, 0xd4, 0x34, 0xb4, 0x74, 0xf4, 0xc, 0x8c, 0x4c, 0xcc, 0x2c, 0xac, 0x6c, 0xec, 0x1c, 0x9c, 0x5c, 0xdc, 0x3c, 0xbc, 0x7c, 0xfc, 0x2, 0x82, 0x42, 0xc2, 0x22, 0xa2, 0x62, 0xe2, 0x12, 0x92, 0x52, 0xd2, 0x32, 0xb2, 0x72, 0xf2, 0xa, 0x8a, 0x4a, 0xca, 0x2a, 0xaa, 0x6a, 0xea, 0x1a, 0x9a, 0x5a, 0xda, 0x3a, 0xba, 0x7a, 0xfa, 0x6, 0x86, 0x46, 0xc6, 0x26, 0xa6, 0x66, 0xe6, 0x16, 0x96, 0x56, 0xd6, 0x36, 0xb6, 0x76, 0xf6, 0xe, 0x8e, 0x4e, 0xce, 0x2e, 0xae, 0x6e, 0xee, 0x1e, 0x9e, 0x5e, 0xde, 0x3e, 0xbe, 0x7e, 0xfe, 0x1, 0x81, 0x41, 0xc1, 0x21, 0xa1, 0x61, 0xe1, 0x11, 0x91, 0x51, 0xd1, 0x31, 0xb1, 0x71, 0xf1, 0x9, 0x89, 0x49, 0xc9, 0x29, 0xa9, 0x69, 0xe9, 0x19, 0x99, 0x59, 0xd9, 0x39, 0xb9, 0x79, 0xf9, 0x5, 0x85, 0x45, 0xc5, 0x25, 0xa5, 0x65, 0xe5, 0x15, 0x95, 0x55, 0xd5, 0x35, 0xb5, 0x75, 0xf5, 0xd, 0x8d, 0x4d, 0xcd, 0x2d, 0xad, 0x6d, 0xed, 0x1d, 0x9d, 0x5d, 0xdd, 0x3d, 0xbd, 0x7d, 0xfd, 0x3, 0x83, 0x43, 0xc3, 0x23, 0xa3, 0x63, 0xe3, 0x13, 0x93, 0x53, 0xd3, 0x33, 0xb3, 0x73, 0xf3, 0xb, 0x8b, 0x4b, 0xcb, 0x2b, 0xab, 0x6b, 0xeb, 0x1b, 0x9b, 0x5b, 0xdb, 0x3b, 0xbb, 0x7b, 0xfb, 0x7, 0x87, 0x47, 0xc7, 0x27, 0xa7, 0x67, 0xe7, 0x17, 0x97, 0x57, 0xd7, 0x37, 0xb7, 0x77, 0xf7, 0xf, 0x8f, 0x4f, 0xcf, 0x2f, 0xaf, 0x6f, 0xef, 0x1f, 0x9f, 0x5f, 0xdf, 0x3f, 0xbf, 0x7f, 0xff]

WF_PARTIAL_2IN13_V3= [
    0x0,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x80,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x14,0x0,0x0,0x0,0x0,0x0,0x0,  
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,
    0x22,0x17,0x41,0x00,0x32,0x36,
]

WS_20_30_2IN13_V3 = [ 
    0x80,0x4A,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x4A,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x80,0x4A,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x4A,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0xF,0x0,0x0,0x0,0x0,0x0,0x0,    
    0xF,0x0,0x0,0xF,0x0,0x0,0x2,    
    0xF,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,  
    0x22,0x17,0x41,0x0,0x32,0x36  
]

EPD_WIDTH       = const(122)
EPD_HEIGHT      = const(250)

RST_PIN         = const(26)
DC_PIN          = const(27)
CS_PIN          = const(15)
BUSY_PIN        = const(25)
SCK_PIN         = const(13)
MOSI_PIN        = const(14)

class EPD_2in13_V3(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)

        self.sck_pin =  Pin(SCK_PIN, Pin.OUT)
        self.mosi_pin =  Pin(MOSI_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        self.full_lut = WF_PARTIAL_2IN13_V3
        self.partial_lut = WS_20_30_2IN13_V3
        
        self.spi = SPI(1, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), baudrate=26000000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.digital_write(self.cs_pin, 1)
        self.digital_write(self.sck_pin, 0)

        self.buf_width = (self.width + 7) // 8
        self.offset = self.buf_width * 8 - self.width

        self.buffer = bytearray(self.height * self.buf_width)
        super().__init__(self.buffer, self.height, self.width, framebuf.MONO_VLSB)

        self.switch = True
        self.init()

    '''
    function :Change the pin state
    parameter:
        pin : pin
        value : state
    '''
    def digital_write(self, pin, value):
        pin.value(value)

    '''
    function : Read the pin state 
    parameter:
        pin : pin
    '''
    def digital_read(self, pin):
        return pin.value()

    '''
    function : The time delay function
    parameter:
        delaytime : ms
    '''
    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)
        
    '''
    function : Write data to SPI
    parameter:
        data : data
    '''
    def spi_writebyte(self, data):
        self.spi.write(bytearray([data]))
        # for i in range(8):
        #     if data & 0x80 == 0:
        #         self.digital_write(self.mosi_pin,0)
        #     else:
        #         self.digital_write(self.mosi_pin,1)

        #     data <<= 1

        #     self.digital_write(self.sck_pin,1)
        #     self.digital_write(self.sck_pin,0)

    '''
    function :Hardware reset
    parameter:
    '''
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)   

    '''
    function :send command
    parameter:
     command : Command register
    '''
    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte(command)
        self.digital_write(self.cs_pin, 1)
    
    '''
    function :send data
    parameter:
     data : Write data
    '''
    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte(data)
        self.digital_write(self.cs_pin, 1)
    
    '''
    function :Wait until the busy_pin goes LOW
    parameter:
    '''
    def ReadBusy(self):
        # print('busy')
        self.delay_ms(10)
        while(self.digital_read(self.busy_pin) == 1):      # 0: idle, 1: busy
            self.delay_ms(10)    
        # print('busy release')
    
    '''
    function : Turn On Display
    parameter:
    '''
    def TurnOnDisplay(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20)  #  Activate Display Update Sequence    
        self.ReadBusy()
    
    '''
    function : Turn On Display Part
    parameter:
    '''
    def TurnOnDisplayPart(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0x0F)     # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence 
        self.ReadBusy()
    
    '''
    function : Set lut
    parameter:
        lut : lut data
    '''
    def LUT(self, lut):
        self.send_command(0x32)
        for i in range(0,153):
            self.send_data(lut[i])
        self.ReadBusy()
    
    '''
    function : Send lut data and configuration
    parameter:
        lut : lut data 
    '''
    def LUT_by_host(self, lut):
        self.LUT(lut)             # lut
        self.send_command(0x3F)
        self.send_data(lut[153])
        self.send_command(0x03)   # gate voltage
        self.send_data(lut[154])
        self.send_command(0x04)   # source voltage
        self.send_data(lut[155])  # VSH
        self.send_data(lut[156])  # VSH2
        self.send_data(lut[157])  # VSL
        self.send_command(0x2C)   # VCOM
        self.send_data(lut[158])
    
    '''
    function : Setting the display window
    parameter:
        Xstart : X-axis starting position
        Ystart : Y-axis starting position
        Xend : End position of X-axis
        Yend : End position of Y-axis
    '''
    def SetWindows(self, Xstart, Ystart, Xend, Yend):
        self.send_command(0x44)                #  SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data((Xstart >> 3) & 0xFF)
        self.send_data((Xend >> 3) & 0xFF)
        
        self.send_command(0x45)                #  SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(Ystart & 0xFF)
        self.send_data((Ystart >> 8) & 0xFF)
        self.send_data(Yend & 0xFF)
        self.send_data((Yend >> 8) & 0xFF)
        
    '''
    function : Set Cursor
    parameter:
        Xstart : X-axis starting position
        Ystart : Y-axis starting position
    '''
    def SetCursor(self, Xstart, Ystart):
        self.send_command(0x4E)             #  SET_RAM_X_ADDRESS_COUNTER
        self.send_data(Xstart & 0xFF)
        
        self.send_command(0x4F)             #  SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(Ystart & 0xFF)
        self.send_data((Ystart >> 8) & 0xFF)

    '''
    function : Initialize the e-Paper register
    parameter:
    '''
    def init(self):
        self.reset()
        self.delay_ms(100)
        
        self.ReadBusy()
        self.send_command(0x12)  # SWRESET
        self.ReadBusy()
        
        self.send_command(0x01)  # Driver output control 
        self.send_data(0xf9)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x11)  #data entry mode 
        self.send_data(0x03)
        
        self.SetWindows(0, 0, self.width-1, self.height-1)
        self.SetCursor(0, 0)
        
        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x05)
        
        self.send_command(0x21) # Display update control
        self.send_data(0x00)
        self.send_data(0x80)
        
        self.send_command(0x18) # Read built-in temperature sensor
        self.send_data(0x80)
        
        self.ReadBusy()
        self.LUT_by_host(self.partial_lut)

        self.font_load("GB2312-24.fon")

        print('epd init')
       
    '''
    function : Clear screen
    parameter:
    if self.width % 8 == 0: 
            for j in range(0, self.height):
                for i in range(0, int(self.width // 8)):
                    self.send_data(0xFF)
        else:
            for j in range(0, self.height):
                for i in range(0, int(self.width // 8) + 1):
                    self.send_data(0xFF)
    '''
    def Clear(self):
        self.send_command(0x24)
        for i in range(self.buf_width*self.height):
            self.send_data(0xFF)
        self.send_command(0x26)
        for i in range(self.buf_width*self.height):
            self.send_data(0xFF)
        self.TurnOnDisplay()    
    
    '''
    function : Sends the image buffer in RAM to e-Paper and displays
    parameter:
        image : Image data
    '''
    def display(self, image):
        self.send_command(0x24)
        for j in range(self.height-1,-1,-1):
            for i in range(self.buf_width):
                self.send_data(byte_filp[image[j + i * self.height]])
        self.TurnOnDisplay()
    
    '''
    function : Refresh a base image
    parameter:
        image : Image data
    '''
    def Display_Base(self, image):
        self.send_command(0x24)
        for j in range(self.height-1,-1,-1):
            for i in range(self.buf_width):
                self.send_data(byte_filp[image[j + i * self.height]])
                
        self.send_command(0x26)
        for j in range(self.height-1,-1,-1):
            for i in range(self.buf_width):
                self.send_data(byte_filp[image[j + i * self.height]])
        self.TurnOnDisplay()
        
    '''
    function : Sends the image buffer in RAM to e-Paper and partial refresh
    parameter:
        image : Image data
    '''    
    async def display_Partial(self, image):
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(1)
        self.digital_write(self.reset_pin, 1)

        self.LUT_by_host(self.full_lut)
        
        self.send_command(0x37)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x40)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
       
        self.send_command(0x3C)
        self.send_data(0x80)
        
        self.send_command(0x22)
        self.send_data(0xC0)
        self.send_command(0x20)
        self.ReadBusy()
        
        # self.SetWindows(0,0,self.width-1,self.height-1)
        # self.SetCursor(0,0)

        print('send frame buffer')
        self.send_command(0x24)
        for j in range(self.height-1,-1,-1):
            for i in range(self.buf_width):
                self.send_data(byte_filp[image[j + i * self.height]])

        machine.freq(80000000)
        print('next frame ready')     
        while not self.switch:
            await uasyncio.sleep(0)             
        self.TurnOnDisplayPart()
        self.switch = False
    
    '''
    function : Enter sleep mode
    parameter:
    '''
    def sleep(self):
        self.send_command(0x10) #enter deep sleep
        self.send_data(0x01)
        self.delay_ms(100)
        
        
if __name__=='__main__':
    epd = EPD_2in13_V3()
    epd.Clear()
    epd.fill(0xff)

    epd.text("meticulous", 0, epd.offset, 0x00)
    epd.text("adj. ", 0, epd.offset+25, 0x00)
    epd.text("一丝不苟的，注意细节的", 0, epd.offset+50, 0x00)
    epd.display_Partial(epd.buffer)
    epd.delay_ms(2000)
    
    epd.vline(10, 90, 60, 0x00)
    epd.vline(90, 90, 60, 0x00)
    epd.hline(10, 90, 80, 0x00)
    epd.hline(10, 150, 80, 0x00)
    epd.line(10, 90, 90, 150, 0x00)
    epd.line(90, 90, 10, 150, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(2000)
    
    epd.rect(10, 180, 50, 40, 0x00)
    epd.fill_rect(60, 180, 50, 40, 0x00)
    epd.Display_Base(epd.buffer)
    epd.delay_ms(2000)
    
    epd.init()
    for i in range(0, 10):
        epd.fill_rect(40, 230, 40, 10, 0xff)
        epd.text(str(i), 60, 230, 0x00)
        epd.display_Partial(epd.buffer)
        
    print("sleep")
    epd.init()
    epd.Clear()
    epd.delay_ms(2000)
    epd.sleep()
