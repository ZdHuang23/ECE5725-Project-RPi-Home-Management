import requests
import os
import threading
import time
import RPi.GPIO as GPIO
import board
import digitalio
from astral import LocationInfo
from datetime import datetime
from astral.sun import sun
import adafruit_dht
import re

DURATION = 5

# a class that controls all GPIOs
class GPIO_helper():
    GPIO.setmode(GPIO.BCM)

    servo1_pin = 6

    GPIO.setup(servo1_pin, GPIO.OUT)

    pwm1 = GPIO.PWM(servo1_pin, 50)

    pwm1.start(0)

    fan_pin = 4

    GPIO.setup(fan_pin, GPIO.OUT)
    GPIO.output(fan_pin, GPIO.LOW)

    humid_pin = 20

    GPIO.setup(humid_pin, GPIO.OUT)
    GPIO.output(humid_pin, GPIO.LOW)

    pir_sensor1 = digitalio.DigitalInOut(board.D23)
    pir_sensor1.direction = digitalio.Direction.INPUT

    pir_sensor2 = digitalio.DigitalInOut(board.D12)
    pir_sensor2.direction = digitalio.Direction.INPUT

    pir_sensor3 = digitalio.DigitalInOut(board.D16)
    pir_sensor3.direction = digitalio.Direction.INPUT

    led_pin_1 = 19
    led_pin_2 = 21
    led_pin_3 = 5
    GPIO.setup(led_pin_1, GPIO.OUT)
    GPIO.setup(led_pin_2, GPIO.OUT)
    GPIO.setup(led_pin_3, GPIO.OUT)


    dhtDevice = dht_start()
    temperature, humidity = 0, 0
    dht_lock = threading.Lock()
    def __init__(self):
        return
    def curtain_open(self):
        threading._start_new_thread(self.curtain_open_helper,())

    def curtain_close_helper(self):
        try:
            self.pwm1.ChangeDutyCycle(8.5)

            time.sleep(1)

            self.pwm1.ChangeDutyCycle(0)
            print("curtain closed")

        except KeyboardInterrupt:
            self.pwm1.stop()
            self.GPIO.cleanup()

    def curtain_close(self):
        threading._start_new_thread(self.curtain_close_helper,())

    def curtain_open_helper(self):
        try:
            self.pwm1.ChangeDutyCycle(6.5)

            time.sleep(1.1)

            self.pwm1.ChangeDutyCycle(0)
            print("curtain open")

        except KeyboardInterrupt:
            self.pwm1.stop()
            self.GPIO.cleanup()
            
    def humid_on(self):
        time.sleep(0.3)
        threading._start_new_thread(self.humid_on_helper,())

    def humid_on_helper(self):
        print("humid on")
        GPIO.output(self.humid_pin, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(self.humid_pin, GPIO.LOW)
        time.sleep(0.3)
        GPIO.output(self.humid_pin, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(self.humid_pin, GPIO.LOW)
        
    def humid_off(self):
        time.sleep(0.3)
        threading._start_new_thread(self.humid_off_helper,())

    def humid_off_helper(self):
        print("humid off")
        GPIO.output(self.humid_pin, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(self.humid_pin, GPIO.LOW)

    def light1last(self):
        threading._start_new_thread(self.light1_duration,())

    def light2last(self):
        threading._start_new_thread(self.light2_duration,())

    def light1_duration(self):
        self.light_on(1)
        time.sleep(DURATION)
        self.light_off(1)

    def light2_duration(self):
        self.light_on(2)
        time.sleep(DURATION)
        self.light_off(2)

    def light3_duration(self):
        self.light_on(3)
        time.sleep(DURATION)
        self.light_off(3)


    def light_on(self,index):
        if index == 1:
            # print("light1 on")
            GPIO.output(self.led_pin_1, GPIO.HIGH)
        elif index == 2:
            # print("light2 on")
            GPIO.output(self.led_pin_2, GPIO.HIGH)
        elif index ==3 :
            GPIO.output(self.led_pin_3, GPIO.HIGH)

        
    def light_off(self,index):
        if index == 1:
            # print("light1 off")
            GPIO.output(self.led_pin_1, GPIO.LOW)
        elif index == 2:
            # print("light2 off")
            GPIO.output(self.led_pin_2, GPIO.LOW)
        elif index ==3 :
            GPIO.output(self.led_pin_3, GPIO.LOW)

    def fan_on(self):
        print("fan on")
        GPIO.output(self.fan_pin, GPIO.HIGH)

    def fan_off(self):
        print("fan off")
        GPIO.output(self.fan_pin, GPIO.LOW)

    def motiondect1(self):
        return self.pir_sensor1.value
    
    def motiondect2(self):
        return self.pir_sensor2.value
    
    def motiondect3(self):
        return self.pir_sensor3.value
    
    def humitemp(self):
        #self.dht_lock.acquire()
        a,b = self.temperature, self.humidity
        #self.dht_lock.release()
        if a == None :
            a = 999
        if b == None :
            b = 999
        return a,b

    def dht_init(self):
        threading._start_new_thread(self.dht_helper,())

    def dht_helper(self):
        while True:
            try:
                # Print the values to the serial port
                #self.dht_lock.acquire()
                self.temperature = self.dhtDevice.temperature
                self.humidity = self.dhtDevice.humidity
                #self.dht_lock.release()
                time.sleep(0.1)
            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                time.sleep(0.1)
                continue
            except Exception as error:
                self.dhtDevice.exit()
                raise error
    
def speak(text):
    print(text)
    os.system("echo "+text+" > speechfifo")

# request current weahter from api
def get_weather(api_key, lat, lon):
    url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={lat},{lon}'
    response = requests.get(url)

    # 检查请求是否成功
    if response.status_code == 200:
        # 解析JSON响应
        weather_data = response.json()
        return weather_data
    else:
        print(f"Error: Unable to fetch weather data. Status code: {response.status_code}")
        return None

def acquire_Ithaca_weather():
    api_key = 'YOUR API KEY'
    latitude, longitude = 42.443962, -76.501884 
    weather_data = get_weather(api_key, latitude, longitude)
    return weather_data['current']['temp_c'], weather_data['current']['condition']['text']

def sunrise():
    city = LocationInfo("Ithaca", "US", "US/Eastern", 42.443962, -76.501884)
    s = sun(city.observer, date=datetime.now(), tzinfo=city.timezone)
    return s['sunrise'].strftime('%H:%M:%S')


def sunset():
    city = LocationInfo("Ithaca", "US", "US/Eastern", 42.443962, -76.501884)
    s = sun(city.observer, date=datetime.now(), tzinfo=city.timezone)
    return s['sunset'].strftime('%H:%M:%S')

def extract_number(filename):
    parts = re.findall(r'\d+', filename)
    return int(parts[0]) if parts else None


def dht_start():
    while True:
        try:
            sensor = adafruit_dht.DHT11(board.D26)
            return sensor
        except Exception as e:
            print(f"Failed to initialize DHT11 sensor: {e}. Retrying...")
            time.sleep(0.5)  # Wait for 2 seconds before retrying