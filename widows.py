import time
import network
from umqttsimple import MQTTClient
import network
# 导入httpclient
import lib_urequest
# 导入json库
from umqttsimple import MQTTClient
import ujson
from machine import Pin
from machine import Timer
from time import sleep_ms
from machine import PWM
import time
import re

from HCSR04 import HCSR04 #子文件夹下的调用方式
from machine import Pin,SoftI2C,Timer
from ssd1306 import SSD1306_I2C

i2c = SoftI2C(sda=Pin(1), scl=Pin(2))
oled = SSD1306_I2C(128, 64, i2c, addr=0x3c)
p3 = PWM(Pin(3))
p3.freq(50)
duty_num = 1638
p3.duty_u16(1638)
LED=Pin(7,Pin.OUT) 
LED.value(0)
zhuangtai='guan'
word_list1=['Sunny','Clear','Cloudy','Partly','Cloudy','Partly Cloudy','Mostly Cloudy','Overcast']
word_list2=['Light Rain','Light Snow','Foggy,Windy']
word_list3=['Hot','Cold','Tornado','Tropical Storm','Hurricane','Blustery','Haze,Shower','Thundershower','Thundershower with Hail','Moderate Rain','Heavy Rain','Storm','Severe Storm','Ice Rain','Moderate Snow','Heavy Snow','Snowstorm','Dust','Sand','Duststorm','Sandstorm']
word_list4=['18','19','20','21','22','23','00','01','02','03','04','05','06']

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('Redmi K30 5G', '88888888')
        i = 1
        while not wlan.isconnected():
            print("正在链接...{}".format(i))
            i += 1
            time.sleep(1)
    print('network config:', wlan.ifconfig())


def sub_cb(topic, msg): # 回调函数，收到服务器消息后会调用这个函数
    print(topic, msg)

def get_time(time_str):
    time_str = time_str.strip()
    time_str = time_str.split('T')[1]
    time_str = time_str.split('+')[0]
    time_str = time_str.split(':')[0:2]
    return time_str[0]


# 1. 联网'
do_connect()
# 2. 创建mqt
c = MQTTClient("umqtt_client", "47.113.205.8")  # 建立一个MQTT客户端
c.set_callback(sub_cb)  # 设置回调函数
c.connect()  # 建立连接
c.subscribe(b"ledctl")  # 监控ledctl这个通道，接收控制命令

def fun(tim):
    global zhuangtai
    global LED
    global duty_num
    resp = lib_urequest.get('https://api.seniverse.com/v3/weather/now.json?key=SBBRd0X8fidhmnBv2&location=tianjin&language=en&unit=c')
#resp= lib_urequest.get('https://api.seniverse.com/v3/weather/hourly.json?key=SBBRd0X8fidhmnBv2&location=tokyo&language=en&unit=c&start=0&hours=24')
# 打印请求结果
    print(type(resp.text),resp.text)
# json字符串转为python列表类型
    json_str1 = ujson.loads(resp.text)
    print(json_str1['results'][0]['location']['name'])
    print(json_str1['results'][0]['now']['text'])
    print(json_str1['results'][0]['now']['temperature'])
    print(json_str1['results'][0]['last_update'])
   
    get_time(str(json_str1['results'][0]['last_update']))
    print(get_time((json_str1['results'][0]['last_update'])))
#def fun(tim):
    oled.fill(0) # 清屏,背景黑色
    oled.text('City: '+str(json_str1['results'][0]['location']['name']),0,0)
    oled.text('Now : '+str(json_str1['results'][0]['now']['text']),0,20)
    oled.text('Now TEMP: '+str(json_str1['results'][0]['now']['temperature'])+'C',0,10)
    oled.text('Made by 24-606',0,30)
   
    oled.show()
    
    
    
    if json_str1['results'][0]['now']['text'] in word_list1:
        time.sleep_ms(500)
        duty_num = 1638
        p3.duty_u16(duty_num)
        zhuangtai='kai'
    
    if json_str1['results'][0]['now']['text'] in word_list2:
        print('AAA')
        time.sleep_ms(500)
        duty_num = 3114
        p3.duty_u16(duty_num)
        zhuangtai='banguan'
    
    if json_str1['results'][0]['now']['text'] in word_list3:
   
        time.sleep_ms(500)
        duty_num = 4915
        p3.duty_u16(duty_num)
        zhuangtai='guan'
        
    if get_time((json_str1['results'][0]['last_update'])) in word_list4:
        LED.value(1)
    elif json_str1['results'][0]['now']['text']:
        time.sleep_ms(500)
        duty_num = 3114
    print(zhuangtai)
    c.publish(b'red',zhuangtai)



#def fun(tim):
    #oled.fill(0) # 清屏,背景黑色
    #oled.text('City: '+str(json_str1['results'][0]['location']['name']),0,0)
    #oled.text('Now : '+str(json_str1['results'][0]['now']['text']),0,20)
    # oled.text('Now TEMP: '+str(json_str1['results'][0]['now']['temperature'])+'C',0,10)
    #oled.text('Made By SLAREDGE',0,30)
    # oled.show()

#开启 RTOS 定时器
tim = Timer(1)
tim.init(period=10000, mode=Timer.PERIODIC, callback=fun) #周

while True:
    c.check_msg()
    time.sleep(1)