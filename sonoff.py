# Basic Sonoff Program
# Connect to my Local Wifi & MQTT server

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = 'Apple Network Extreme'
password = 'bleelady'
mqtt_server = '192.168.1.152' # Replace with the IP or URI of the MQTT server you use
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'robotlab' # This is the topic you want to subscribe to
topic_pub = b'robotlab' # This is the topic you want to publish to
servo_pin = machine.PWM(machine.Pin(2))
relay_pin = 12
button_pin = 0
led_pin = 13
print("Sonoff Device Online")

class State():
    
    def init():
        self.on = False
    
    @property
    def state(self):
        return self.on
    
    @state.setter
    def state(self, value:bool):
        self.on = value
        
output = State()
output.state = False

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())

def led_off():
    led = machine.Pin(led_pin, machine.Pin.OUT)
    led.value(1)


def led_on():
    led = machine.Pin(led_pin, machine.Pin.OUT)
    led.value(0)

def relay_off():
    led = machine.Pin(relay_pin, machine.Pin.OUT)
    led.value(1)

def relay_on():
    relay = machine.Pin(relay_pin, machine.Pin.OUT)
    relay.value(0)

def led_flash(times:int=3):
    for n in range(times):
        led_on()
        time.sleep(0.1)
        led_off()
        time.sleep(0.1)

relay_off()
led_flash(5)

def sub_cb(topic, msg):
    print((topic, msg))
    if topic == topic_sub:
        print("Device Message",msg)
        if msg == b"1":
            output.state = True
            print("Turning ON device")
            led_flash(1)
            led_on()
            relay_on()
        if msg == b"0":
            output.state = False
            print("Turning OFF device")
            led_flash(2)
            led_off()
            relay_off()
        if msg not in [b"0",b"1"]:
            led_flash(1)
            print("Device State = ", output.state)
            if output.state:
                led_on()
            else:
                led_off()

def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

def restart_reconnect():
    print('Failed toconnect to MQTT broker, Reconnecting...')
    time.sleep(10)
    machine.reset()
    
def button_pressed()->bool:
    button = machine.Pin(button_pin, machine.Pin.IN)
    #print(button.value())
    if button.value() == 0:
        print("button pressed")
        return True
    if button.value() == 1:
        
        return False

def state_toggle():
    if output.state == True:
        output.state = False
    else:
        output.state == True
    #if output.state == True:
        #led_on()
        #relay_on()
    #if output.state == False:
        #led_off()
        #relay_off()

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_reconnect()
    
while True:
    try:
        client.check_msg()
        # client.publish(topic_pub, msg)
        if button_pressed():
            state_toggle()
            if output.state == False:
                msg = "0"
            if output.state == True:
                msg = "1"
            client.publish(topic_pub, msg)
            time.sleep(1)
            

    except OSError as e:
        restart_reconnect()

