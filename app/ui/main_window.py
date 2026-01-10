from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox



class MainWindow(QMainWindow):
    def __init__(self, user, db_manager):
        super.__init__()
        self.db_manager = db_manager
        self.user_role = user['role']

        self.setFixedSize(1400,800)
        self.setWindowTitle("Система збору статистики та прогнозування захворюваності")

