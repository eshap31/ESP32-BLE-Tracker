from customtkinter import *
from PIL import Image


# color: 96036d

class Home_Screen:
    def __init__(self):
        # window initialization
        self.root = CTk()
        self.root.geometry('600x600')
        self.root.title('Home Screen')
        self.root.resizable(False, False)  # make it so that you cant resize the window
        #self.root.configure(fg_color='#96036d')  # set background
        set_default_color_theme(
            'dark-blue')  # TODO change color theme to custom one: https://customtkinter.tomschimansky.com/documentation/color

        # logo
        logo_image = CTkImage(dark_image=Image.open("gui/logo.png"),
                              size=(350, 350))
        self.logo_label = CTkLabel(self.root, image=logo_image, text='')
        self.logo_label.place(x=125, y=50)
        self.create_buttons()

    def create_buttons(self):
        # signup - have to enter the admin password to create a new account
        # create the buttons
        login_button = CTkButton(self.root, text='Login', height=30, width=50, command=self.login)
        signup_button = CTkButton(self.root, text='Signup', height=30, width=50, command=self.signup)

        github_logo_image = CTkImage(dark_image=Image.open("gui/github_logo.png"), size=(30, 30))
        github_button = CTkButton(self.root, image=github_logo_image, command=self.open_github, width=30, height=30, fg_color='gray95', hover_color='gray95', text='')

        # place the buttons
        login_button.place(x=225, y=435)
        signup_button.place(x=325, y=435)
        github_button.place(x=520, y=10)

    def login(self):
        print('login')
        # TODO change to actuall login

    def signup(self):
        print('signup')
        # TODO change to actuall login

    def open_github(self):
        import webbrowser
        webbrowser.open_new("https://github.com/eshap31")


    def start(self):
        self.root.mainloop()


def main():
    gui = Home_Screen()
    gui.start()


if __name__ == '__main__':
    main()
