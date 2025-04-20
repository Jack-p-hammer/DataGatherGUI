import serial
import serial.tools.list_ports
import Support_Package as sp
serial_ports =  list(serial.tools.list_ports.comports())
import pandas as pd
import regex as re


def read_data(line):
    """Takes in ascii version of Arduino data line and returns dictionary with data names as keys and data values as values
    
    ARGS:
        line (str): ascii version of Arduino data line with format: "data_name1:data_value1, data_name2:data_value2, ..."
    RETURNS:
        data_dict (dict): dictionary with data names as keys and data values as values
    """
    
    data_dict = {} 
    split = line.split(",") # split line into list of data
    
    for data in split:
        data_name, data_value = data.split(":") # split data into name and value
        data_value = re.sub(r'\r\n', "", data_value)
        data_dict[data_name] = data_value
    print(data_dict)        
    df = pd.DataFrame(data_dict)
    return df


print(serial_ports[0].device)
def Connect(baud, port): # Requires testing/setup
    """Connects to Arduino via serial port
    ARGS:
    baud(int): baud rate of serial connection
    port(string): port of serial connection ex: "COM10"
    
    RETURNS:
    True if connection is successful, False if not
    """
    global ser
    try:
        ser = serial.Serial(port = port, baudrate = baud)
        print(f"Connecting to COM port: {port}")
        print("Connection successful")
        return True
    except:
        print("Connection issue")
        return False

def read_serial(): # Collects data from arduino
    """Reads data from Arduino via serial connection"""
    ser.write(b'g') # sends "g" to Arduino to request data... will be changed to bit code later (Look into converting to bits)
    arduinoData_string = str(ser.readline().decode('ascii'))
    print("Here: " + arduinoData_string)
    try:
        data_dict = read_data(arduinoData_string)
        return data_dict
    except:
        return None

    
Connect(9600, serial_ports[0].device)
read_serial()
read_serial()