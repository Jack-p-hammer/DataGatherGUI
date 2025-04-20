import pandas as pd
import numpy as np
import serial 
import time
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
        data_dict[data_name] = float(data_value)
    return data_dict

def write_append(data, csv, is_trial_name = False):
    """ Takes data list and appends to csv file as a row
    
    INPUTS:
        data: data to be added as a list, can be mixed type (for header)
        csv: file to be written too
    
    OUTPUTS:
        None
    """
    list_o_lists = []
    if type(data) == pd.core.frame.DataFrame:
        for row in data:
             list_o_lists.append(data[row].tolist())
    data = list_o_lists    
    new = pd.DataFrame(data).transpose()
    new.to_csv(csv, index=False, header=False, mode ="a")
    return None


def excel_transpose(csv):
    """Transposes entire excel sheet"""  
    current = pd.read_csv(csv, header= None).transpose()
    current.to_csv(csv, index=False, mode = "w", header=None)
    return None

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
        time.sleep(1.5)
        print("Connection successful")
        return True, ser
    except:
        print("Connection issue")
        return False
    
    
def get_data(serial_object, started = False): # Collects data from arduino
    """Reads data from Arduino via serial connection"""
    if started == True:
        serial_object.write('g\r'.encode())
        time.sleep(.5)
        arduinoData_string = str(ser.readline().decode('ascii'))
    else:

        serial_object.write('i\r'.encode()) # sends "g" to Arduino to request data... will be changed to bit code later (Look into converting to bits)
        time.sleep(.5)
        arduinoData_string = str(ser.readline().decode('ascii'))
    
    return read_data(arduinoData_string)