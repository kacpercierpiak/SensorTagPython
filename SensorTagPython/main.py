import asyncio
import threading
import time
import curses
from os import name, system
from bleak import discover,BleakClient
from sensor_calcs import *

stdscr = curses.initscr()
curses.noecho()

class gatt_set:
    def __init__(self, data, config, extra = ''):        
        self.data = data
        self.config = config
        self.extra = extra

global sensor_data
sensor_data = {}
sensor_data['sensor_tag'] = ''
sensor_data['key'] = 'None'
sensor_data['temp'] = 0
sensor_data['humid'] = 0
sensor_data['bar'] = 0
sensor_data['accel'] = [0.0,0.0,0.0]
sensor_data['gyro'] = [0.0,0.0,0.0]
sensor_data['magn'] = [0.0,0.0,0.0]

gatt_services = dict({
   'Temp': gatt_set('f000aa01-0451-4000-b000-000000000000','f000aa02-0451-4000-b000-000000000000'),
   'Accel': gatt_set('f000aa11-0451-4000-b000-000000000000','f000aa12-0451-4000-b000-000000000000','f000aa13-0451-4000-b000-000000000000'),
   'Humid': gatt_set('f000aa21-0451-4000-b000-000000000000','f000aa22-0451-4000-b000-000000000000'),
   'Mag': gatt_set('f000aa31-0451-4000-b000-000000000000','f000aa32-0451-4000-b000-000000000000','f000aa33-0451-4000-b000-000000000000'),
   'Barometer': gatt_set('f000aa41-0451-4000-b000-000000000000','f000aa42-0451-4000-b000-000000000000','f000aa43-0451-4000-b000-000000000000'),
   'Gyro': gatt_set('f000aa51-0451-4000-b000-000000000000','f000aa52-0451-4000-b000-000000000000'),
   'Key': gatt_set('0000ffe1-0000-1000-8000-00805f9b34fb','')
   }) 

def print_info(info):
    stdscr.clear()
    stdscr.addstr(str(info))
    stdscr.refresh()  


def draw():     
    while True:        
        info = "SensorTag: " + sensor_data['sensor_tag'] + '\n'
        info += "Key status: " + sensor_data['key'] + '\n'
        info += "Temp: %.2f" % sensor_data['temp'] + '\n'
        info += "Humid: %.2f" % sensor_data['humid'] + '\n'
        info += "Accell: [%.2f, %.2f, %.2f]" % (sensor_data['accel'][0],sensor_data['accel'][1],sensor_data['accel'][2]) + '\n'
        info += "Gyro: [%.2f, %.2f, %.2f]" % (sensor_data['gyro'][0],sensor_data['gyro'][1],sensor_data['gyro'][2]) + '\n'
        info += "Magn: [%.2f, %.2f, %.2f]" % (sensor_data['magn'][0],sensor_data['magn'][1],sensor_data['magn'][2]) + '\n'
        print_info(info)
        time.sleep(0.1)   

def notification_handler(sender, data):
    if sender == 36: # Temp
        sensor_data['temp'] = temp_calc(data)
    elif sender == 44: # Accel
        sensor_data['accel'] = accel_calc(data)
    elif sender == 55: # Humid
        sensor_data['humid'] = humid_calc(data)
    elif sender == 63: # Magn
        sensor_data['magn'] = magn_calc(data)
    elif sender == 74: # Barometer
        sensor_data['bar'] = bar_calc(data)
    elif sender == 86: # Gyro
        sensor_data['gyro'] = gyro_calc(data)
    elif sender == 94: # Key
        sensor_data['key'] = key_calc(data)

async def main(): 
    sensor_data['sensor_tag'] = 'Discover devices'
    devices = await discover()
    for d in devices:
        if d.name == 'SensorTag':
            sensor_data['sensor_tag'] = d.address
            async with BleakClient(d.address) as client:
                client.pair()
                for service in gatt_services:                 
                    if service == 'Gyro':
                        await client.write_gatt_char(gatt_services[service].config,[0x07])
                    else:
                        char_conf = gatt_services[service].config
                        if char_conf != '':
                            await client.write_gatt_char(char_conf,[0x01]) 
                            
                    await client.start_notify(gatt_services[service].data, notification_handler)   
                    
                while(True):                
                    await asyncio.sleep(1.0)                    

if __name__ == "__main__":    
    x = threading.Thread(target=draw)
    x.start()
    asyncio.run(main())  