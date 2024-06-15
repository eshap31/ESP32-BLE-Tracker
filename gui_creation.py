from customtkinter import *
from PIL import Image
from db_testing import DbManager


# color: 96036d

class Home_Screen:
    def __init__(self):
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

        # DbManager
        self.db_manager = DbManager('admin', 'adminpass')

    def create_buttons(self):
        # signup - have to enter the admin password to create a new account
        # create the buttons
        self.login_button = CTkButton(self.root, text='Login', height=30, width=50, hover_color='#3a3a5e',
                                      fg_color='white',
                                      command=self.login, text_color='black')
        self.signup_button = CTkButton(self.root, text='Signup', height=30, width=50, command=self.signup,
                                       hover_color='#3a3a5e', fg_color='white', text_color='black')

        self.github_logo_image = CTkImage(dark_image=Image.open("images/github_logo.png"), size=(30, 30))
        self.github_button = CTkButton(self.root, image=self.github_logo_image, command=Home_Screen.open_github,
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
            self.enter_button.configure(text='Create account', width=90, command=lambda: self.check_created_user(self.username_entry.get(), self.password_entry.get()))

            self.placed_widgets.extend(
                [self.username_entry, self.password_entry, self.enter_button, self.change_screens_button])
            self.packed_widgets.extend([self.signup_label])

            self.signup_label.pack(side='top', pady=45)
            self.username_entry.place(x=185, y=150)
            self.password_entry.place(x=185, y=215)
            self.enter_button.place(x=255, y=280)
            self.change_screens_button.place(x=200, y=330)

    def check_created_user(self, username, password):  # checks if the username that the admin put in is available
        status = self.db_manager.create_account(username, password)  # try to create the account with the inputted credentials
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
        waiting_for_system_label = CTkLabel(self.root, text='Waiting for peripheral devices to connect\rand for the central device to start advertising...\r\nStart tracking when you are ready, and when system is ready.', text_color='white', font=('Helvetica', 20))
        waiting_for_system_label.pack(side='top', pady=75)

    def start(self):
        # initialize window
        self.root = CTk()
        self.root.geometry('600x600')
        self.root.configure(fg_color='#051D41')
        self.root.title('Home Screen')
        self.root.resizable(False, False)  # make it so that you cant resize the window
        self.root.iconbitmap('images/favicon.ico')
        set_default_color_theme('dark-blue')
        # TODO change color theme to custom one: https://customtkinter.tomschimansky.com/documentation/color

        # logo
        logo_image = CTkImage(dark_image=Image.open("images/logo.png"),
                              size=(350, 350))
        self.logo_label = CTkLabel(self.root, image=logo_image, text='')
        self.logo_label.place(x=125, y=50)
        self.placed_widgets.append(self.logo_label)
        self.create_buttons()

        self.root.mainloop()


def main():
    gui = Home_Screen()
    gui.start()


if __name__ == '__main__':
    main()
