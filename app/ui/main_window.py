from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super.__init__()
        self.db_manager = db_manager
