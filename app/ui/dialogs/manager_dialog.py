from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox

class ManagerDialog(QDialog):
    def __init__(self, db_manager, manager_target=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self.setWindowTitle("Додати інвертор" if not manager_target else "Редагувати інвертор")
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout()
        
        self.inp_old = QLineEdit()
        self.inp_old.setPlaceholderText("Поточний пароль")
        self.inp_old.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.inp_new = QLineEdit()
        self.inp_new.setPlaceholderText("Новий пароль")
        self.inp_new.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.inp_confirm = QLineEdit()
        self.inp_confirm.setPlaceholderText("Підтвердження пароля")
        self.inp_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_save = QPushButton("Змінити")
        btn_save.clicked.connect(self.save_password)
        
        layout.addWidget(QLabel("Введіть дані:"))
        layout.addWidget(self.inp_old)
        layout.addWidget(self.inp_new)
        layout.addWidget(self.inp_confirm)
        layout.addWidget(btn_save)
        
        self.setLayout(layout)

    def get_data(self):
        pass