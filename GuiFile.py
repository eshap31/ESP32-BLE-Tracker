import copy
import time

from customtkinter import *
from PIL import Image
from db_manager import DbManager
import json


class Gui:
    def __init__(self, admin_username, admin_password, model_address):
        # user initialization

        # user initialization
        self.start_tracking_button = None
        self.enter_button = None
        self.change_screens_button = None
        self.password_entry = None
        self.username_entry = None
        self.signup_label = None
        self.login_label = None

        self.root = None
        self.login_button = None
        self.github_button = None
        self.signup_button = None
        self.github_logo_image = None
        self.logo_label = None

        self.placed_widgets = []  # list of temporary widgets that will be destroyed every time you move onto a new screen
        self.packed_widgets = []
        self.user_ready = False

        # DbManager
        self.db_manager = DbManager(admin_username, admin_password)

        # tracking screen and model
        self.server_ready = False
        self.coordinate_calculator_ready = False

        # model
        self.model_address = model_address
        self.edges = []
        self.beacons = []
        self.original_edges = []
        self.original_beacons = []
        self.mac_list = []  # list of all the beacon's Wi-Fi mac address
        self.ratio = None

        # map
        self.map_dimensions = None
        self.resized_model_address = 'resized_model.json'
        self.map_canvas = None
        self.canvas_width = None
        self.canvas_height = None
        self.central_circle_id = None  # holds the central device circle object

        self.central_image = CTkImage(dark_image=Image.open('images/central.png'), size=(30, 30))
        self.central_label = None
        self.can_display_central = False

        # info screen
        self.info_screen_dimensions = []  # size of the information screen
        self.info_screen_coordinates = {}  # coordinates that represent where the information screen is located
        self.info_screen_canvas = None  # this is where I will create the information screen

        self.logout_button = None

        # window
        self.window_dimensions = []

        self.one_meter_rssi_dict = {}

    # user initialization  -------------------------------
    def create_buttons(self):
        # signup - have to enter the admin password to create a new account
        # create the buttons
        self.login_button = CTkButton(self.root, text='Login', height=30, width=50, hover_color='#3a3a5e',
                                      fg_color='white',
                                      command=self.login, text_color='black')
        self.signup_button = CTkButton(self.root, text='Signup', height=30, width=50, command=self.signup,
                                       hover_color='#3a3a5e', fg_color='white', text_color='black')

        self.github_logo_image = CTkImage(dark_image=Image.open("images/github_logo.png"), size=(30, 30))
        self.github_button = CTkButton(self.root, image=self.github_logo_image, command=Gui.open_github,
                                       width=30, height=30,
                                       text='', hover_color='#3a3a5e', fg_color='white', text_color='black')
        # TODO change github logo to a different color
        self.placed_widgets.extend([self.login_button, self.signup_button])

        # place the buttons
        self.login_button.place(x=225, y=375)
        self.signup_button.place(x=325, y=375)
        self.github_button.place(x=520, y=10)

    def login(self):
        self.destroy_home_screen()
        # create widgets
        self.login_label = CTkLabel(self.root, text='Login',
                                    font=('Helvetica', 20))
        self.username_entry = CTkEntry(self.root, placeholder_text='Username', width=230, fg_color='white',
                                       placeholder_text_color='gray', text_color='black')
        self.password_entry = CTkEntry(self.root, placeholder_text='Password', width=230, fg_color='white',
                                       placeholder_text_color='gray', text_color='black')
        self.login_button = CTkButton(self.root, text='Login', height=30, width=50, hover_color='#3a3a5e',
                                      fg_color='white',
                                      command=lambda: self.check_user_login(self.username_entry.get(),
                                                                            self.password_entry.get()),
                                      text_color='black')
        self.change_screens_button = CTkButton(self.root, text='Dont have an account? Register', height=30, width=200,
                                               hover_color='#3a3a5e', fg_color='white',
                                               command=self.signup, text_color='black')

        self.placed_widgets.extend(
            [self.username_entry, self.password_entry, self.login_button, self.change_screens_button])
        self.packed_widgets.extend([self.login_label])

        # place on screen
        self.login_label.pack(side='top', pady=45)
        self.username_entry.place(x=185, y=150)
        self.password_entry.place(x=185, y=215)
        self.login_button.place(x=275, y=280)
        self.change_screens_button.place(x=200, y=330)

    def signup(self):
        self.destroy_home_screen()

        # create widgets
        self.signup_label = CTkLabel(self.root, text='Enter admin credentials\rin order to create an account',
                                     font=('Helvetica', 20))
        self.username_entry = CTkEntry(self.root, placeholder_text='admin username', width=230, fg_color='white',
                                       placeholder_text_color='gray', text_color='black')
        self.password_entry = CTkEntry(self.root, placeholder_text='admin password', width=230, fg_color='white',
                                       placeholder_text_color='gray', text_color='black')
        self.enter_button = CTkButton(self.root, text='Enter', height=30, width=50, hover_color='#3a3a5e',
                                      fg_color='white',
                                      command=lambda: self.check_admin_login(self.username_entry.get(),
                                                                             self.password_entry.get()),
                                      text_color='black')
        self.change_screens_button = CTkButton(self.root, text='Already have an account? Login', height=30, width=200,
                                               hover_color='#3a3a5e', fg_color='white',
                                               command=self.login, text_color='black')

        self.placed_widgets.extend(
            [self.username_entry, self.password_entry, self.enter_button, self.change_screens_button])
        self.packed_widgets.extend([self.signup_label])

        # place on screen
        self.signup_label.pack(side='top', pady=45)
        self.username_entry.place(x=185, y=150)
        self.password_entry.place(x=185, y=215)
        self.enter_button.place(x=275, y=280)
        self.change_screens_button.place(x=200, y=330)

    def check_user_login(self, username, password):
        status = self.db_manager.login(username, password)
        if status:
            self.user_in()
        else:
            self.login_label.pack_forget()
            self.packed_widgets = []
            self.login_label.configure(text='Incorrect username or password', text_color='red')
            self.packed_widgets.extend([self.login_label])
            self.login_label.pack(side='top', pady=45)

    def check_admin_login(self, username, password):
        status = self.db_manager.signup(username, password)
        if not status:  # if the admin credentials are incorrect
            self.signup_label.pack_forget()
            self.signup_label.configure(text='admin credentials are incorrect, try again', text_color='red')
            self.packed_widgets.extend([self.signup_label])
            self.signup_label.pack(side='top', pady=35)
        else:  # if the admin credentials are correct
            self.destroy_home_screen()
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.username_entry.configure(placeholder_text='Username')
            self.password_entry.configure(placeholder_text='Password')
            self.signup_label.configure(text='Choose a username and a password', text_color='white')
            self.enter_button.configure(text='Create account', width=90,
                                        command=lambda: self.check_created_user(self.username_entry.get(),
                                                                                self.password_entry.get()))

            self.placed_widgets.extend(
                [self.username_entry, self.password_entry, self.enter_button, self.change_screens_button])
            self.packed_widgets.extend([self.signup_label])

            self.signup_label.pack(side='top', pady=45)
            self.username_entry.place(x=185, y=150)
            self.password_entry.place(x=185, y=215)
            self.enter_button.place(x=255, y=280)
            self.change_screens_button.place(x=200, y=330)

    def check_created_user(self, username, password):  # checks if the username that the admin put in is available
        status = self.db_manager.create_account(username,
                                                password)  # try to create the account with the inputted credentials
        if not status:
            self.signup_label.pack_forget()
            self.packed_widgets = []
            self.signup_label.configure(text='Username already taken, try another', text_color='red')
            self.packed_widgets.extend([self.signup_label])
            self.signup_label.pack(side='top', pady=45)

        else:
            self.user_in()

    @staticmethod
    def open_github():
        import webbrowser
        webbrowser.open_new("https://github.com/eshap31")

    def destroy_home_screen(self):
        for widget in self.placed_widgets:
            widget.place_forget()
        self.placed_widgets = []

        for widget in self.packed_widgets:
            widget.pack_forget()
        self.packed_widgets = []

    def user_in(self):
        self.destroy_home_screen()
        waiting_for_system_label = CTkLabel(self.root,
                                            text='Waiting for peripheral devices to connect\rand for the central device to start advertising...\r\nStart tracking when you are ready, and when system is ready.',
                                            text_color='white', font=('Helvetica', 20))
        self.logout_button = CTkButton(self.root, text='Log out', width=50, hover_color='#3a3a5e', fg_color='white', text_color='black')

        self.user_ready = True
        print('user in is true')
        waiting_for_system_label.pack(side='top', pady=75)
        self.logout_button.place(x=20, y=10)

    def start(self):
        # initialize window
        self.root = CTk()
        self.initialize_map()
        self.root.geometry('600x600')
        self.root.configure(fg_color='#051D41')
        self.root.title('Home Screen')
        self.root.resizable(False, False)  # make it so that you cant resize the window
        self.root.iconbitmap('images/favicon.ico')
        set_default_color_theme('dark-blue')

        # logo
        logo_image = CTkImage(dark_image=Image.open("images/logo.png"),
                              size=(350, 350))
        self.logo_label = CTkLabel(self.root, image=logo_image, text='')
        self.logo_label.place(x=125, y=50)
        self.placed_widgets.append(self.logo_label)
        self.create_buttons()

        self.server_ready = True

        self.root.mainloop()

    # tracking window -----------------
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
        self.ratio = new_ratio

    def model_to_map(self):
        """
        - function gets the ratio between the model and the map
        - function changes the coordinates of the edges and beacons to fit the map, using the ratio
        """
        # using the ratio, create the new coordinates
        self.edges = [
        {'start': [int(num * self.ratio) for num in edge['start']], 'end': [int(num * self.ratio) for num in edge['end']]}
        for edge in self.edges
        ]

        self.beacons = [
        {'coordinates': [int(num * self.ratio) for num in beacon['coordinates']], 'mac_address': beacon['mac_address']}
        for beacon in self.beacons
        ]

        # create resized_model.json file, using new_edges and new_beacons lists
        with open('resized_model.json', 'w') as file:
            json.dump({'edges': self.edges, 'beacons': self.beacons}, file, indent=4)

    def initialize_map(self):
        # extract edges and beacons from model
        with open(self.model_address, 'r') as model:
            data = json.load(model)

        self.original_edges = copy.deepcopy(data['edges'])
        self.original_beacons = copy.deepcopy(data['beacons'])
        self.edges = copy.deepcopy(data['edges'])
        self.beacons = copy.deepcopy(data['beacons'])

        print(self.original_beacons)
        self.mac_list = [beacon['mac_address'] for beacon in self.beacons]
        print(self.mac_list)

        width, height = self.get_map_size()
        print(width, height)
        max_coordinates = self.get_max_coords()
        print(max_coordinates)
        self.create_map_size((width, height), max_coordinates)
        print(f'ratio: {self.ratio}')
        self.model_to_map()
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
                                            height=self.info_screen_dimensions[1], bg='#051D41')
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
            beacon['coordinates'][0], beacon['coordinates'][1] = int(
                (beacon['coordinates'][0] / self.map_dimensions[
                    0]) * self.canvas_width), int(
                (beacon['coordinates'][1] / self.map_dimensions[1]) * self.canvas_height)
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
            r = 8  # set radius size
            self.draw_circle(x, y, r, 'white')

    # def draw_central(self, x, y, r, fill_color):
    #     """
    #     Draws or updates a circle on the canvas according to the parameters given.
    #     """
    #     if self.central_circle_id is None:
    #         # Create the circle if it doesn't exist
    #         self.central_circle_id = self.map_canvas.create_oval(x - r, y - r, x + r, y + r, width=2,
    #                                                              fill=fill_color)
    #     else:
    #         # Update the circle's coordinates if it exists
    #         self.map_canvas.coords(self.central_circle_id, x - r, y - r, x + r, y + r)
    #         self.map_canvas.itemconfig(self.central_circle_id, fill=fill_color)  # Update the color if needed

    def draw_central(self, x, y, realx, realy):
        if self.can_display_central:
            if self.central_label is None:
                self.central_label = CTkLabel(self.root, image=self.central_image, fg_color='transparent', text='')
            self.central_label.place(x=x, y=y)


    # def update_central_position(self, x, y, r, fill_color):
    #     if self.user_ready:
    #         self.map_canvas.after(0, self.draw_central, x, y, r, fill_color)

    def ready_to_track(self):
        while not self.user_ready:  # wait until user has logged in, and then display button
            time.sleep(0.01)
        print('ready_to_track')
        self.start_tracking_button = CTkButton(self.root, text='Start', height=30, width=50, hover_color='#3a3a5e',
                                               fg_color='white',
                                               text_color='black', command=self.tracking_initialize)
        self.start_tracking_button.place(x=275, y=300)

    def draw_info_screen(self):
        """
        - draw the initial info screen
        """
        # TODO work on the information screen graphics
        label = CTkLabel(self.info_screen_canvas, text='Info Screen', font=('Helvetica', 20), width=100)
        coordinate_label = CTkLabel(self.info_screen_canvas, text='Central Device Coordinates:', font=('Helvetica', 16))

        label.place(x=180, y=40)
        coordinate_label.place(x=50, y=180)

    def create_window(self):
        self.calculate_window_dimensions()
        self.initialize_window()
        self.resize_model_to_canvas()
        self.draw_edges()
        self.draw_beacons()
        self.draw_info_screen()

    def tracking_initialize(self):
        # destroy old window
        self.start_tracking_button.destroy()
        self.root.destroy()

        # create tje mew window
        self.root = CTk()

        self.root.iconbitmap('images/favicon.ico')

        # onboard model, and modify fit computer
        self.initialize_map()

        # create window - place beacons, edges, and add divider between map and info screens
        self.create_window()

        self.can_display_central = True

        # test it out
        self.root.mainloop()