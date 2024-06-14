from customtkinter import *
from PIL import Image


# color: 96036d
# TODO change widgets to self
# TODO add "Already have an account? Login" button
# TODO destroy buttons when going from login to signup screens
# TODO start working with an sql database
# TODO add create account screen that is opened only when correct admin credentials are entered

class Home_Screen:
    def __init__(self):
        self.root = None

        self.login_button = None
        self.github_button = None
        self.signup_button = None
        self.github_logo_image = None
        self.logo_label = None

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

        # place the buttons
        self.login_button.place(x=225, y=375)
        self.signup_button.place(x=325, y=375)
        self.github_button.place(x=520, y=10)

    def login(self):
        print('login')
        # TODO change to actual login
        self.destroy_home_screen()
        # create widgets
        username_entry = CTkEntry(self.root, placeholder_text='Username', width=230, fg_color='white',
                                  placeholder_text_color='gray', text_color='black')
        password_entry = CTkEntry(self.root, placeholder_text='Password', width=230, fg_color='white',
                                  placeholder_text_color='gray', text_color='black')
        login_button = CTkButton(self.root, text='Login', height=30, width=50, hover_color='#3a3a5e', fg_color='white',
                                 command=self.check_user_login, text_color='black')
        change_screens_button = CTkButton(self.root, text='Dont have an account? Register', height=30, width=200,
                                          hover_color='#3a3a5e', fg_color='white',
                                          command=self.signup, text_color='black')

        # place on screen
        username_entry.place(x=185, y=150)
        password_entry.place(x=185, y=215)
        login_button.place(x=275, y=280)
        change_screens_button.place(x=200, y=330)

    def signup(self):
        print('signup')
        # TODO change to actuall login
        self.destroy_home_screen()

        # create widgets
        signup_label = CTkLabel(self.root, text='Enter admin credentials\rin order to create an account',
                                font=('Helvetica', 20))
        username_entry = CTkEntry(self.root, placeholder_text='admin username', width=230, fg_color='white',
                                  placeholder_text_color='gray', text_color='black')
        password_entry = CTkEntry(self.root, placeholder_text='admin password', width=230, fg_color='white',
                                  placeholder_text_color='gray', text_color='black')
        login_button = CTkButton(self.root, text='Enter', height=30, width=50, hover_color='#3a3a5e', fg_color='white',
                                 command=self.check_admin_login, text_color='black')

        # place on screen
        signup_label.pack(side='top', pady=45)
        username_entry.place(x=185, y=150)
        password_entry.place(x=185, y=215)
        login_button.place(x=275, y=280)

    def check_user_login(self):
        print('checking user login')

    def check_admin_login(self):
        print('checking admin login')
        #TODO check if correct admin username and password, if yes, go to create account, if not display message

    def check_created_info(self):  # checks if the username that the admin put in is available
        print('checking created login info')

    @staticmethod
    def open_github():
        import webbrowser
        webbrowser.open_new("https://github.com/eshap31")

    def destroy_home_screen(self):
        self.logo_label.destroy()
        self.signup_button.destroy()
        self.login_button.destroy()
        # self.github_button.destroy()

    def start(self):
        # initialize window
        self.root = CTk()
        self.root.geometry('600x600')
        self.root.configure(fg_color='#051D41')
        self.root.title('Home Screen')
        self.root.resizable(False, False)  # make it so that you cant resize the window
        self.root.iconbitmap('images/favicon.ico')
        set_default_color_theme(
            'dark-blue')  # TODO change color theme to custom one: https://customtkinter.tomschimansky.com/documentation/color

        # logo
        logo_image = CTkImage(dark_image=Image.open("images/logo.png"),
                              size=(350, 350))
        self.logo_label = CTkLabel(self.root, image=logo_image, text='')
        self.logo_label.place(x=125, y=50)
        self.create_buttons()

        self.root.mainloop()


def main():
    gui = Home_Screen()
    gui.start()


if __name__ == '__main__':
    main()
