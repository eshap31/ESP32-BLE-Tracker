import time


class CalculateCoords:
    def __init__(self, gui_obj, rssi_data_obj):
        self.gui_obj = gui_obj

        # rssi data
        self.rate = 1  # every 1 second, the self.curr and self.back will be updated
        self.rssi_data_obj = rssi_data_obj
        self.back_lst = None

        # trilateration
        self.n = 3.5  # environment variable - play around with it
        self.tx_power = -45  # one meter rssi of the solo

    def get_top_three_rssi(self, back_lst):
        """
        - goes over the self.back_lst - which looks like this: [(mac address, rssi), ...]
        - gets the top three rssi's, and the beacon mac address that scanned
        - calls the calculate_distances function
        """
        print(f'in top three rssi, back list {back_lst}')
        # TODO update the information screen, with values in back_lst
        top_three = []

        for key, val in back_lst.items():
            # add to list
            top_three.append((key, val))
            # sort the list, biggest will be first
            top_three.sort(key=lambda item: item[1], reverse=True)
            # if there are more than three values in the list, remove the smallest one:
            if len(top_three) > 3:
                top_three.pop()

        self.calculate_distances(top_three)

    def get_coordinates(self, mac_addr):
        """
        - returns the coordinates for the peripheral device with the certain mac address
        """
        for beacon in self.gui_obj.beacons:
            if beacon['mac_address'] == mac_addr:
                return beacon['coordinates']

    def calculate_distances(self, rssi_list):
        """
        - rssi_list: [mac_addr:rssi, mac_addr:rssi, ...]
        - Convert RSSI to distance using the Log-Distance Path Loss Model.
        - does this for the top three rssi values
        """
        reference_points = []  # list of tuples of the relevant beacon coordinates
        distances = []
        for t in rssi_list:
            # distance calculation
            rssi = t[1]
            distance = (10 ** ((self.tx_power - rssi) / (10 * self.n))) * self.gui_obj.ratio  # fit to map dimensions
            # getting the coordinates of the peripheral device that made the scan
            mac_addr = t[0]
            peripheral_coordinates = self.get_coordinates(mac_addr)
            reference_points.append(peripheral_coordinates)
            distances.append(distance)

        self.trilaterate(reference_points, distances)

    def trilaterate(self, reference_points, distances):
        """
        Trilateration function to calculate the estimated location of the central device.

        Parameters:
        - reference_points: List of tuples (x, y) representing the known positions of BLE peripherals.
        - distances: List of distances from the central device to each BLE peripheral.

        Returns:
        - Tuple (x, y): Estimated coordinates of the central device...
        """
        if self.gui_obj.can_display_central:
            print('trilaterating')
            A = 2 * (reference_points[1][0] - reference_points[0][0])
            B = 2 * (reference_points[1][1] - reference_points[0][1])
            C = (distances[0]) ** 2 - (distances[1]) ** 2 - reference_points[0][0] ** 2 + reference_points[1][0] ** 2 - \
                reference_points[0][1] ** 2 + reference_points[1][1] ** 2

            D = 2 * (reference_points[2][0] - reference_points[1][0])
            E = 2 * (reference_points[2][1] - reference_points[1][1])
            F = (distances[1]) ** 2 - (distances[2]) ** 2 - reference_points[1][0] ** 2 + reference_points[2][0] ** 2 - \
                reference_points[1][1] ** 2 + reference_points[2][1] ** 2

            x = (C * E - F * B) / (E * A - B * D)
            y = (C * D - A * F) / (B * D - A * E)
            if self.gui_obj.canvas_width > x > 0 and 0 < y < self.gui_obj.canvas_height:
                print(f'coordinates are: {x, y}')
                self.gui_obj.draw_central(x, y)

    def update_rssi_data_list(self):
        # """  testing start """
        # while not self.gui_obj.coordinate_calculator_ready:
        #     time.sleep(0.1)
        # self.gui_obj.ready_to_track()  # allow user to start tracking
        # """ testing end """

        self.gui_obj.ready_to_track()

        while True:
            time.sleep(self.rate)
            back_lst = self.rssi_data_obj.Get_Back()
            if len(back_lst.keys()) >= 3:
                self.get_top_three_rssi(back_lst)
            else:
                continue

    def start(self):
        while not self.gui_obj.coordinate_calculator_ready:
            time.sleep(0.01)
        print('can start calculating')
        self.update_rssi_data_list()
