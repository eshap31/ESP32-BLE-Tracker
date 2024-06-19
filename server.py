import threading

from RssiData import RssiData
from ServerCommunication import ServerCommunication
from CalculateCoords import CalculateCoords
from GuiFile import Gui

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

        # Gui
        self.gui_obj = None

        self.admin_username = None
        self.admin_password = None

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
        self.admin_username = 'admin'
        self.admin_password = 'adminpass'
        self.gui_obj = Gui(self.admin_username, self.admin_password, self.model_address)

        # RssiData
        self.rssi_data_obj = RssiData()

        # Server_Communication
        self.peripheral_device_count = 3  # amount of peripheral devices required
        self.server_object = ServerCommunication(self.peripheral_device_count, self.gui_obj, self.rssi_data_obj)
        server_thread = threading.Thread(target=self.server_object.start)
        self.threads.append(server_thread)

        # CalculateCoords
        self.coordinate_calculator = CalculateCoords(self.gui_obj, self.rssi_data_obj)
        # Coordinate_Calulator_Thread = threading.Thread(target=self.coordinate_calculator.start)
        Coordinate_Calulator_Thread = threading.Thread(target=self.coordinate_calculator.start)  # TODO change target back to start
        self.threads.append(Coordinate_Calulator_Thread)

        # start threads
        for t in self.threads:
            t.start()

        self.gui_obj.start()

        # wait for threads to finish
        for t in self.threads:
            t.join()


def main():
    # Manager
    manager = Manager()
    manager.start()


if __name__ == '__main__':
    main()
