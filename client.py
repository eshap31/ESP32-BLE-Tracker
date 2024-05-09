import socket
import network
import time
from micropython import const
import bluetooth
import ujson 
import _thread
import sys
import gc

"""
    This is a client script is part of a client server dialogue, where the client is the esp32, and the server is a computer running python.
    What goes on in the script:
    - esp32 connects to desired network (should be the same network that the computer (server) is connected to)
    - esp32 connects to the server, using sockets, and sends a hello message
"""

class Protocol:
    LENGTH_FIELD_SIZE = 5

    @staticmethod
    def create_msg(data):
        """
        Create a valid protocol message, with length field
        """
        length = str(len(str(data)))
        print(f'length of data: {length}')
        zfill_length = Protocol.custom_zfill(length)
        message = zfill_length.encode() + data
        return message

    @staticmethod
    def create_serialized_data(dictionary):
        """
        serializes the dictionary into json format, then calls the Protocol.create_message() func to format the data
        for sending
        """
        return Protocol.create_msg(ujson.dumps(dictionary))

    @staticmethod
    def get_msg(my_client):
        """
        Extract message from protocol, without the length field
        If length field does not include a number, returns False, "Error"
        :rtype: (bool, str)
        """
        len_word = my_client.recv(Protocol.LENGTH_FIELD_SIZE).decode()
        if Protocol.is_integer(len_word):
            message = my_client.recv(int(len_word)).decode()
            return True, message
        else:
            return False, "Error"

    @staticmethod
    def get_serialized_data(my_client):
        data = Protocol.get_msg(my_client)
        if data[0]:
            return True, ujson.loads(data[1])
        else:
            return False, 'Error'
        
    @staticmethod    
    def is_integer(s):
        try:
            int(s)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def custom_zfill(s):
        # Calculate how many zeros we need to prepend
        needed_zeros = Protocol.LENGTH_FIELD_SIZE - len(s)
        if needed_zeros > 0:
            # Prepend the zeros to the string
            return '0' * needed_zeros + s
        else:
            # If the string is already the required length or longer, return it unchanged
            return s


class ConnectToWifi:
    """
        - this class connects an esp32 to a wifi.
        - uses network library, and time.
    """
    
    @staticmethod
    def start(ssid, password):
        # create instance of station
        sta_if = network.WLAN(network.STA_IF)

        # activate the station
        sta_if.active(True)
           
        while True:
            time.sleep(2)
            try:  # if not already connected to network
                sta_if.connect(ssid, password)
                
                if sta_if.isconnected():# check if the connection is established
                    # check ip address
                    print(f"connected to {ssid}.\n{sta_if.ifconfig()}")  # (<IP address>, <subnet mask>, <Gateway>, <DNS>)
                    return

                else:
                    print('not able to connect to network, trying again...')

            except Exception as e:
                if sta_if.isconnected():
                    print(f"already connected to: {ssid}. \n{sta_if.ifconfig()}")
                    return
                else:
                    print(f'error: {e}')
        

class BleScanner:
    def __init__(self, ms_scan):
        """ bluetooth scanning variables: """
        # self.central_devices = central_devices_list  # list that holds all of the central device addresses
        self.bt = bluetooth.BLE()
        self.ms_scan = ms_scan
        self._IRQ_SCAN_RESULT = const(5)
        self._IRQ_SCAN_DONE = const(6)
        """ data organization: """
        self.devs = [{}, {}]  # list of two dictionaries that hold data about devices
        self.curr = 0  # index of the most updated dictionary of the two in the self.devs list
        self.back = 1  # index of the second most up to date dictionary in the self.devs dictionary
        self.ttl = 5
        
    def Get_Back(self):
        back_dict = self.devs[self.back]
        self._Swap_Curr()
        gc.collect()
        return back_dict
    
    def _Swap_Curr(self):
        self.back = self.curr
        self.curr = (self.curr + 1) % 2
        
    def bt_irq(self, event, data): # called when ble event occures
        """ update self.devs[self.curr] dictionary """
        if event == self._IRQ_SCAN_RESULT:
            # A single scan result.
            addr_type, addr, connectable, rssi, adv_data = data
            decoded_address = ':'.join(['%02X' % i for i in addr])
            
            # check if the device was already picked up
            if self.devs[self.curr].get(decoded_address) is None:  # new device
                self.devs[self.curr][decoded_address] = (rssi, self.ttl)  # update the curr dictionary
            
            else:  # device already been picked up
                ttl = self.devs[self.curr][decoded_address][1]
                if ttl == 0:  # take out of the dictionary
                    self.devs[self.curr].pop(decoded_address)  # remove device from dictionary, because ttl got to 0
                else:
                    ttl -= 1
                    self.devs[self.curr][decoded_address] = (rssi, ttl)  # update the curr dictionary, add check ttl
                
                
        elif event == self._IRQ_SCAN_DONE:
            """
                when scan is completed, start a new one
            """
            # Scan duration finished or manually stopped.
            self.bt.gap_scan(self.ms_scan, 10000, 10000)  # start a new scan
        
    def start(self): 
        self.bt.irq(self.bt_irq)
        self.bt.active(True)
        print("BLE Active:", self.bt.active())
        print('starting scan...')
        self.bt.gap_scan(self.ms_scan, 10000, 10000)
        time.sleep_ms(self.ms_scan)
        

class Networking:
    def __init__(self, esp32_peripheral, rate):
        self.port = 4500
        self.server_ip = '172.16.1.118'
        self.client_socket = None
        
        self.scanner = esp32_peripheral
        self.rate = rate
        self.stop = True
        self.lock = _thread.allocate_lock()
        
    def wait_for_server_msg(self):  # wait for stop message from server
        while True:
            """ change """
            data = self.client_socket.recv(1024)
            data = data.decode()
            """ """
            with self.lock:  # allow syncronization, and prevent race conditions
                if data == 'stop':
                    self.stop = True
                else:  # data is start
                    self.stop = False
                
    def send_data(self):  # updates the self.scanner.Get_Back()
        # run a timer that will call: self.scanner.Get_Back(), every rate amount of seconds
        while True:
            time.sleep(self.rate)
            with self.lock:  # use with statement, which automatically handles aquire and release
                if self.stop == True:
                    print('server told me to stop')
                    continue
            print('getting back')
            back = self.scanner.Get_Back()
            if back == {}:
                print('empty')
                continue
            data = Protocol.create_serialized_data(back)
            print('got data')
            self.client_socket.send(data)
            print('sent')
            #print(f'sent: {back}')
           
    def start(self):
        # socket setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.port))
        print('connected')
        
        data = Protocol.get_msg(self.client_socket)
        print(data[1])
        verif = Protocol.create_msg('peripheral device') # send the server verification message
        self.client_socket.send(verif)
        data = Protocol.get_msg(self.client_socket)
        if data[0]:  # if the server sent 'start'
            self.stop = False  # the server has sent permission to start
            print('moving on to the scanning and sending fase')
            _thread.start_new_thread(self.scanner.start, ())  # start the scanner from here, and create a seperate thread for it
            print('1')
            _thread.start_new_thread(self.wait_for_server_msg, ())  # start the wait_for_stop func from here, and create a seperate thread for it
            print('2')
            _thread.start_new_thread(self.send_data, ())  # start the send_data func from here, and create a seperate thread for it"""
            print('3')
        
        
        
class CoordinatorClass:  # main class, that manages everything
    def __init__(self, ssid, password, client):
        self.esp32_client = client
        self.ssid = ssid
        self.password = password
        
    def start(self):
        ConnectToWifi.start(self.ssid, self.password)
        self.esp32_client.start()
        
    
def main():
    # wifi info
    ssid = 'Adassim'
    password = '20406080'
    #ssid = 'Needham'
    #password = 'gr2Hoyer'
    
    # test BleScanner class
    ms_scan = 10000  # (ms) - Scan for 10s (at 100% duty cycle)
    # central_devices_list = {"30:30:F9:77:0E:42": -31}
    esp32_peripheral = BleScanner(ms_scan)
    
    # test Networking class
    rate = 4
    esp32_client = Networking(esp32_peripheral, rate)
    
    # create Client object
    coordinator = CoordinatorClass(ssid, password, esp32_client)
    coordinator.start()
    

main()
