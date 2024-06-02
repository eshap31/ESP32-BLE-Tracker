import usocket as socket
import network
import time
from micropython import const
import bluetooth
import ujson 
import _thread
import sys
import gc
import ubinascii

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
        try:
            len_word, server_addr = my_client.recvfrom(Protocol.LENGTH_FIELD_SIZE).decode()
            if Protocol.is_integer(len_word):
                message, server_addr = my_client.recvfrom(int(len_word)).decode()
                return True, message
            else:
                return False, "Error"
        except OSError as e:
                if e.errno == errno.ECONNABORTED:
                    print(f'found os error :{e}')
                else:
                    print(f'found a different error: {e}')

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
    def get_mac_address(wifi):
        # Get the MAC address
        mac = wifi.config('mac')

        # Format the MAC address
        mac_str = ubinascii.hexlify(mac, ':').decode().upper()
        
        return mac_str

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
                    return ConnectToWifi.get_mac_address(sta_if)

                else:
                    print('not able to connect to network, trying again...')

            except Exception as e:
                if sta_if.isconnected():
                    print(f"already connected to: {ssid}. \n{sta_if.ifconfig()}")
                    return ConnectToWifi.get_mac_address(sta_if)
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
        self.server_tuple = (self.server_ip, self.port)
        self.client_socket = None
        self.mac_address = None
        
        self.scanner = esp32_peripheral
        self.rate = rate
        self.stop = True
        self.lock = _thread.allocate_lock()
        
    def wait_for_server_msg(self):  # wait for stop message from server
        while True:
            """ change """
            try:
                data, addr = self.client_socket.recvfrom(1024)
                data = data.decode()
            except OSError as e:
                if e.errno == errno.ECONNABORTED:
                    print(f'found os error :{e}')
                else:
                    print(f'found a different error: {e}')
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
            try:           
                self.client_socket.sendto(data, self.server_tuple)
            except OSError as e:
                if e.errno == errno.ECONNABORTED:
                    print(f'error with sending data: {e}')
                else:
                    print(f'found a different error: {e}')
            print('sent')
            #print(f'sent: {back}')

    def start(self, mac_address):
        self.mac_address = mac_address

        # UDP socket setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        print(f'sending: {self.mac_address} as verification field')
        verif = Protocol.create_msg(self.mac_address) # create packet
        self.client_socket.sendto(verif, self.server_tuple)  # send the mac address
        print('sent')
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
    def __init__(self):
        self.esp32_client = None
        self.ssid = None
        self.password = None
        
    def start(self):
        #wifi info
        self.ssid = 'Adassim'
        self.password = '20406080'
        #self.ssid = 'Needham'
        #self.password = 'gr2Hoyer'

        #BleScanner class
        ms_scan = 10000  # (ms) - Scan for 10s (at 100% duty cycle)
        esp32_scanner = BleScanner(ms_scan)

        #Networking class
        rate = 1
        self.esp32_client = Networking(esp32_scanner, rate)

        mac_address = ConnectToWifi.start(self.ssid, self.password)
        self.esp32_client.start(mac_address)
        
    
def main():
    # create Client object
    coordinator = CoordinatorClass()
    coordinator.start()
    

main()
