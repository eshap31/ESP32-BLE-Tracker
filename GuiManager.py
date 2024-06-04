from customtkinter import *
import json

class GuiManager:
    # in charge of ModelPlugNPlay and the gui
    def __init__(self, address):
        # ready variables
        self.server_ready = False
        self.coordinate_calculator_ready = False

        # model
        self.model_address = address
        self.edges = []
        self.beacons = []
        self.mac_list = []  # list of all the beacon's wifi mac address

        # map
        self.map_dimensions = None
        self.resized_model_address = 'resized_model.json'
        self.map_canvas = None
        self.canvas_width = None
        self.canvas_height = None

        # info screen
        self.info_screen_dimensions = []  # size of the information screen
        self.info_screen_coordinates = {}  # coordinates that represent where the information screen is located
        self.info_screen_canvas = None  # this is where I will create the information screen

        # window
        self.window_dimensions = []
        self.root = CTk()

    def get_map_size(self):
        """
        - Calculates the map dimensions
        """
        # Initialize the tkinter root window
        root = CTk()

        # Get the screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Create the size of the map
        window_width = screen_width * 0.65
        window_height = screen_height * 0.9
        self.info_screen_dimensions.append(int(screen_width * 0.3))

        return window_width, window_height

    def get_max_coords(self):
        """
        - Using all the edges, this function returns the biggest x value and the biggest y value
        - The coordinates that are returned represent the maximum coordinates of the model
        """
        max_coordinates = [0, 0]
        for e in self.edges:
            start = e['start']
            end = e['end']
            for i in range(0, 2):
                if start[i] > max_coordinates[i]:
                    max_coordinates[i] = start[i]
                if end[i] > max_coordinates[i]:
                    max_coordinates[i] = end[i]
        return max_coordinates

    def create_map_size(self, orig_coords, model_coords):
        """
        - function gets the original map coordinates, and the maximum model coordinates
        - using the model width ratio, the function resizes the original map so that it has the same width ratio as the
          model
        """
        orig_ratio = orig_coords[0] / orig_coords[1]
        model_ratio = model_coords[0] / model_coords[1]

        if orig_ratio > model_ratio:  # if the original map is wider than the model, we have to make the original ratio slimmer
            new_height = orig_coords[1]  # height stays the same
            new_width = min(new_height / model_ratio, new_height * model_ratio)
        else:  # if the model is wider than the original map
            new_width = orig_coords[0]  # width stays the same
            new_height = min(new_width / model_ratio, new_width * model_ratio)  # height gets smaller
        new_ratio = new_width / model_coords[
            0]  # multiply each edge/beacon coordinate by this number to get the new coordinates
        self.map_dimensions = (int(new_width), int(new_height))
        return new_ratio

    def model_to_map(self, ratio):
        """
        - function gets the ratio between the model and the map
        - function changes the coordinates of the edges and beacons to fit the map, using the ratio
        """
        # using the ratio, create the new coordinates
        new_edges = []
        for edge in self.edges:
            edge['start'] = [int(num * ratio) for num in edge['start']]
            edge['end'] = [int(num * ratio) for num in edge['end']]
            new_edges.append(edge)
        self.edges = new_edges

        new_beacons = []
        for beacon in self.beacons:
            beacon['coordinates'] = [int(num * ratio) for num in beacon['coordinates']]
            new_beacons.append(beacon)
        self.beacons = new_beacons

        # create resized_model.json file, using new_edges and new_beacons lists
        with open('resized_model.json', 'w') as file:
            json.dump({'edges': self.edges, 'beacons': self.beacons}, file, indent=4)

    def initialize_map(self):
        # extract edges and beacons from model
        with open(self.model_address, 'r') as model:
            data = json.load(model)
        self.edges = data['edges']
        self.beacons = data['beacons']
        self.mac_list = [beacon['mac_address'] for beacon in self.beacons]
        print(self.mac_list)

        width, height = self.get_map_size()
        print(width, height)
        max_coordinates = self.get_max_coords()
        print(max_coordinates)
        ratio = self.create_map_size((width, height), max_coordinates)
        print(f'ratio: {ratio}')
        self.model_to_map(ratio)
        print(f'map dimensions: {self.map_dimensions}')

    def calculate_window_dimensions(self):
        """
        - calculates the dimensions of the information screen, and the total window
        - the information screen has the same height as the map screen, but a different width
        - give the window a title, and dimensions
        """
        height = self.map_dimensions[1]  # stays the same height
        self.info_screen_dimensions.append(height)
        self.window_dimensions = [self.info_screen_dimensions[0] + self.map_dimensions[0], height]
        print(f'window dimensions: {self.window_dimensions}')

    def initialize_window(self):
        """
        - set the window title, size, and theme
        - create a canvas for the map, and place it, and create a the info screen and place it
        """
        self.root.title('Main Screen')
        self.root.geometry(f'{self.window_dimensions[0]}x{self.window_dimensions[1]}')
        self.root.resizable(False, False)
        set_default_color_theme('dark-blue')

        # initialize map canvas, that will fit the maps portion of the window
        self.map_canvas = CTkCanvas(self.root, width=self.map_dimensions[0], height=self.map_dimensions[1])
        self.map_canvas.pack(side='left', fill='both', expand=True)

        # initialize info screen canvas, that will fit the info screen's portion of the window
        self.info_screen_canvas = CTkCanvas(self.root, width=self.info_screen_dimensions[0],
                                            height=self.info_screen_dimensions[1], bg='#95036d')
        self.info_screen_canvas.pack(side='right', fill='both', expand=True)

        # update both canvases
        self.map_canvas.update()
        self.info_screen_canvas.update()

        # Get the initial canvas size
        self.canvas_width = self.map_canvas.winfo_width()
        self.canvas_height = self.map_canvas.winfo_height()
        print(f'map canvas dimensions: {self.canvas_width}x{self.canvas_height}')

    def resize_model_to_canvas(self):
        """
        - according to the canvas height and width, change all the coordinates of the edges, and beacons, so that the
          scale doesn't change
        - put resized coordinates into resized_model.json, and update self.beacons and self.edges
        """
        new_edges = []
        for edge in self.edges:
            for i in range(0, 2):
                if i == 0:
                    word = 'start'
                else:
                    word = 'end'
                edge[word][0], edge[word][1] = (edge[word][0] / self.map_dimensions[0]) * self.canvas_width, (
                        edge[word][1] / self.map_dimensions[1]) * self.canvas_height
            new_edges.append(edge)

        self.edges = new_edges

        new_beacons = []
        for beacon in self.beacons:
            beacon['coordinates'][0], beacon['coordinates'][1] = int((beacon['coordinates'][0] / self.map_dimensions[
                0]) * self.canvas_width), int((beacon['coordinates'][1] / self.map_dimensions[1]) * self.canvas_height)
            new_beacons.append(beacon)

        self.beacons = new_beacons

        # create resized_model.json file, using new_edges and new_beacons lists
        with open('resized_model.json', 'w') as file:
            json.dump({'edges': self.edges, 'beacons': self.beacons}, file, indent=4)

    def draw_edges(self):
        """
        - draw edges on screen
        """
        for edge in self.edges:
            x1, y1 = edge['start'][0], edge['start'][1]
            x2, y2 = edge['end'][0], edge['end'][1]
            self.map_canvas.create_line(x1, y1, x2, y2, fill='black', width=5)

    def draw_circle(self, x, y, r, fill_color):
        """
        - this function draws a circle according to the parameters given
        """
        self.map_canvas.create_oval(x - r, y - r, x + r, y + r, width=2, fill=fill_color)

    def draw_beacons(self):
        """
        - draw the beacons on the screen as circles
        - beacons are initially white, and only the 3 closest beacons to the central device will be in red
        """
        for beacon in self.beacons:
            x, y = beacon['coordinates'][0], beacon['coordinates'][1]
            r = 15  # set radius size
            self.draw_circle(x, y, r, 'white')

    def draw_info_screen(self):
        """
        - draw the initial info screen
        """
        return

    def create_window(self):
        self.calculate_window_dimensions()
        self.initialize_window()
        self.resize_model_to_canvas()
        self.draw_edges()
        self.draw_beacons()
        self.draw_info_screen()

    def start(self):
        # onboard model, and modify fit computer
        self.initialize_map()

        # create window - place beacons, edges, and add divider between map and info screens
        self.create_window()

        self.ready = True

        # test it out
        self.root.mainloop()