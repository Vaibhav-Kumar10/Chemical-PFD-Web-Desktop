import sqlite3

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog

import src.app_state as app_state
from src.theme import apply_theme_to_screen, apply_theme_to_all
from src.navigation import slide_to_index
from src.toast import show_toast


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("ui/welcomescreen.ui", self)

        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)

        if hasattr(self, "themeToggle"):
            self.themeToggle.clicked.connect(self.toggle_theme)
            self.update_theme_button()

        apply_theme_to_screen(self)

    def gotologin(self):
        slide_to_index(1, direction=1)

    def gotocreate(self):
        slide_to_index(2, direction=1)

    def toggle_theme(self):
        new_theme = "dark" if app_state.current_theme == "light" else "light"
        apply_theme_to_all(new_theme)
        self.update_theme_button()

    def update_theme_button(self):
        if not hasattr(self, "themeToggle"):
            return
        self.themeToggle.setText("Dark mode" if app_state.current_theme == "light" else "Light mode")


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("ui/login.ui", self)

        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
        self.error.setWordWrap(True)

        if hasattr(self, "backToWelcome"):
            self.backToWelcome.clicked.connect(self.gotowelcome)

        if hasattr(self, "themeToggle"):
            self.themeToggle.clicked.connect(self.toggle_theme)
            self.update_theme_button()

        apply_theme_to_screen(self)

    def gotowelcome(self):
        slide_to_index(0, direction=-1)

    def toggle_theme(self):
        new_theme = "dark" if app_state.current_theme == "light" else "light"
        apply_theme_to_all(new_theme)
        self.update_theme_button()

    def update_theme_button(self):
        if not hasattr(self, "themeToggle"):
            return
        self.themeToggle.setText("Dark mode" if app_state.current_theme == "light" else "Light mode")

    def loginfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()

        if len(user) == 0 or len(password) == 0:
            self.error.setText("Please input all fields.")
            return

        conn = sqlite3.connect("app_users.db")
        cur = conn.cursor()
        query = "SELECT password FROM login_info WHERE username = ?"
        cur.execute(query, (user,))
        result = cur.fetchone()
        conn.close()

        if result is None:
            self.error.setText("Invalid username or password")
            return

        result_pass = result[0]
        if result_pass == password:
            print("Successfully logged in.")
            self.error.setText("")
            show_toast("Logged in successfully!")
            # later: slide_to_index(3) for a dashboard
        else:
            self.error.setText("Invalid username or password")


class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("ui/createacc.ui", self)

        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)

        self.error.setWordWrap(True)
        self.backToLogin.clicked.connect(self.gotologin)

        if hasattr(self, "themeToggle"):
            self.themeToggle.clicked.connect(self.toggle_theme)
            self.update_theme_button()

        apply_theme_to_screen(self)

    def gotologin(self):
        slide_to_index(1, direction=-1)

    def toggle_theme(self):
        new_theme = "dark" if app_state.current_theme == "light" else "light"
        apply_theme_to_all(new_theme)
        self.update_theme_button()

    def update_theme_button(self):
        if not hasattr(self, "themeToggle"):
            return
        self.themeToggle.setText("Dark mode" if app_state.current_theme == "light" else "Light mode")

    def signupfunction(self):
        user = self.emailfield.text()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()

        if len(user) == 0 or len(password) == 0 or len(confirmpassword) == 0:
            self.error.setText("Please fill in all inputs.")
            return

        if password != confirmpassword:
            self.error.setText("Passwords do not match.")
            return

        conn = sqlite3.connect("app_users.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO login_info (username, password) VALUES (?, ?)",
                (user, password)
            )
            conn.commit()
            conn.close()

            show_toast("Account created successfully!")
            slide_to_index(0, direction=-1)

        except sqlite3.IntegrityError:
            self.error.setText("ERROR: That username is already taken. Please choose another.")
            conn.close()
        except Exception as e:
            self.error.setText(f"An unexpected database error occurred: {e}")
            conn.close()
