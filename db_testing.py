import os
import json
import hashlib


class DbManager:
    def __init__(self, admin_username, admin_password):
        self.file_path = 'users.json'
        self.admin_username = admin_username
        self.admin_password = admin_password
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """
        Ensures that the user data file exists. If it doesn't, initializes it with admin login.
        """
        if not os.path.exists(self.file_path):
            admin_data = {
                self.hash_value(self.admin_username): self.hash_value(self.admin_password)
            }
            user_data = {}
            with open(self.file_path, 'w') as file:
                json.dump([admin_data, user_data], file, indent=4)  # Use indent to format JSON nicely
        else:
            # Check if admin credentials already exist
            admin_hashed_username = self.hash_value(self.admin_username)
            admin_hashed_password = self.hash_value(self.admin_password)

            with open(self.file_path, 'r') as file:
                users = json.load(file)

            # Verify if admin credentials match stored hashed admin credentials
            if admin_hashed_username not in users[0] or users[0][admin_hashed_username] != admin_hashed_password:
                raise ValueError("Admin credentials in file are incorrect or missing.")

    def hash_value(self, value):
        """
        Hashes the given value using SHA-256 twice for secure storage.
        """
        hashed_once = hashlib.sha256(value.encode('utf-8')).hexdigest()
        hashed_twice = hashlib.sha256(hashed_once.encode('utf-8')).hexdigest()
        return hashed_twice

    def store_user(self, username, password):
        """
        Stores a new user with hashed username and password in the JSON file.
        """
        users = self._read_users()
        hashed_username = self.hash_value(username)
        hashed_password = self.hash_value(password)

        if hashed_username in users[0] or hashed_username in users[
            1]:  # Check admin and user data for existing username
            print("Username already exists.")
            return False

        users[1][hashed_username] = hashed_password
        self._write_users(users)
        return True

    def authenticate_user(self, username, password):
        """
        Authenticates a user by checking hashed username and password in both admin and user data.
        """
        users = self._read_users()
        hashed_username = self.hash_value(username)

        if hashed_username in users[0]:  # Check admin data (index 0) first
            stored_password = users[0][hashed_username]
            if stored_password == self.hash_value(password):
                return True

        if hashed_username in users[1]:  # Check user data (index 1)
            stored_password = users[1][hashed_username]
            if stored_password == self.hash_value(password):
                return True

        return False

    def _read_users(self):
        """
        Reads user data from JSON file and returns a list containing admin and user dictionaries.
        """
        try:
            with open(self.file_path, 'r') as file:
                users = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            users = [{}, {}]  # Initialize with empty admin and user dictionaries

        return users

    def _write_users(self, users):
        """
        Writes updated user data (admin and user dictionaries) to the JSON file in a structured format.
        """
        with open(self.file_path, 'w') as file:
            json.dump(users, file, indent=4)  # Use indent to format JSON nicely

    def signup(self, admin_username_input, admin_password_input):
        """
        Allows a user to sign up by entering username and password.
        Requires entering the admin username and password to create an account.
        """

        # Hash input admin credentials for comparison
        admin_hashed_username_input = self.hash_value(admin_username_input)
        admin_hashed_password_input = self.hash_value(admin_password_input)

        # Read stored admin credentials from file
        users = self._read_users()
        admin_hashed_username = self.hash_value(self.admin_username)
        admin_hashed_password = self.hash_value(self.admin_password)

        # Validate admin credentials
        if admin_hashed_username_input != admin_hashed_username or admin_hashed_password_input != admin_hashed_password:
            # if credentials are incorrect
            return False

        return True

    def create_account(self, users):

        username = input("Enter username: ")
        password = input("Enter password: ")

        # Check if username already exists in admin or user data
        hashed_username = self.hash_value(username)
        if hashed_username in users[0] or hashed_username in users[1]:
            print("Username already exists.")
            return

        if self.store_user(username, password):
            print("Signup successful!")
        else:
            print("Signup failed. Username may already exist or admin credentials were incorrect.")

    def login(self, username, password):
        """
        Allows a user to log in by entering username and password.
        """

        if self.authenticate_user(username, password):
            print("Login successful!")
            return True
        else:
            print("Login failed. Incorrect username or password.")
            return False

    def run(self):
        """
        Runs a loop for user interaction: signup or login.
        """
        while True:
            if not os.path.exists(self.file_path):
                print("Admin login initialized. Please restart the program.")
                break

            choice = input("Do you want to (1) Signup or (2) Login? Enter 1 or 2: ")
            if choice == '1':
                self.signup()
            elif choice == '2':
                self.login()
            else:
                print("Invalid choice. Please enter 1 or 2.")


