import threading

from GuiManager import GuiManager
from RssiData import RssiData
from ServerCommunication import ServerCommunication
from CalculateCoords import CalculateCoords
from gui_creation import Home_Screen

"""
Central device bluetooth mac address:
- 1C:9D:C2:35:A8:52 - solo 1
"""


class Manager:
    def __init__(self):
        # ServerCommunication
        self.peripheral_device_count = None
        self.server_object = None

        # _______________________
        # ModelPlugNPlay
        self.model_address = None

        # Main Screen
        self.main_screen_obj = None

        # Home Screen
        self.home_screen_obj = None
        # _______________________

        # RssiData
        self.rssi_data_obj = None

        # CalculateCoords
        self.coordinate_calculator = None

        # threads
        self.threads = []

    def start(self):
        # 1. GuiManager
        self.model_address = 'Models/eitams_room_model.json'
        self.home_screen_obj = Home_Screen('admin', 'adminpass')
        self.main_screen_obj = GuiManager(self.model_address, self.home_screen_obj.root)

        # RssiData
        self.rssi_data_obj = RssiData()

        # Serve r_Communication
        self.peripheral_device_count = 3  # amount of peripheral devices required
        self.server_object = ServerCommunication(self.peripheral_device_count, self.main_screen_obj, self.rssi_data_obj)
        server_thread = threading.Thread(target=self.server_object.start)
        self.threads.append(server_thread)

        # CalculateCoords
        self.coordinate_calculator = CalculateCoords(self.main_screen_obj, self.rssi_data_obj)
        # Coordinate_Calulator_Thread = threading.Thread(target=self.coordinate_calculator.start)
        Coordinate_Calulator_Thread = threading.Thread(target=self.coordinate_calculator.update_rssi_data_list)  # TODO
        self.threads.append(Coordinate_Calulator_Thread)

        # start threads
        for t in self.threads:
            t.start()

        self.home_screen_obj.start()

        # wait for threads to finish
        for t in self.threads:
            t.join()


def main():
    # Manager
    manager = Manager()
    manager.start()


if __name__ == '__main__':
    main()
