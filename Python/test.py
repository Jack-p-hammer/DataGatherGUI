import Support_Package as sp
import pandas as pd
import serial.tools.list_ports

serial_ports =  list(serial.tools.list_ports.comports())
print(serial_ports)
port = 'COM9'
baud = 9600
print("Starting")
Connected, ser = sp.Connect(baud, port) # returns true if connected and false if not


ser.write('i\r'.encode())

arduinoData_string = str(ser.readline().decode('ascii'))
print(f"deeeeeeeeeeeeez: {arduinoData_string}")