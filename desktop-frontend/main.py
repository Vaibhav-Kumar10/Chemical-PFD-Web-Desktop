import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget

from src.db import create_db_table
import src.app_state as app_state
from src.screens import WelcomeScreen, LoginScreen, CreateAccScreen


def main():
    create_db_table("app_users.db")

    app = QApplication(sys.argv)

    stacked = QStackedWidget()
    stacked.setFixedHeight(800)
    stacked.setFixedWidth(1200)

    # Expose stacked widget globally for navigation/toast
    app_state.widget = stacked

    welcome = WelcomeScreen()
    login = LoginScreen()
    create = CreateAccScreen()

    stacked.addWidget(welcome)  # index 0
    stacked.addWidget(login)    # index 1
    stacked.addWidget(create)   # index 2

    stacked.setCurrentIndex(0)
    stacked.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
