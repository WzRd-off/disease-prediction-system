from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, 
    QMessageBox, QDialogButtonBox
)

class DoctorDialog(QDialog):
    def __init__(self, doctor=None, parent=None):
        super().__init__(parent)
        self.doctor = doctor
        
        self.setWindowTitle("Додати лікаря" if not self.doctor else "Редагувати лікаря")
        self.setFixedSize(350, 400)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Логін:"))
        self.inp_login = QLineEdit()
        self.inp_login.setMaxLength(30) # Ограничение: Макс 30 символов
        # Ограничение: Только английские буквы и цифры
        self.inp_login.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[a-zA-Z0-9_]+$")))
        layout.addWidget(self.inp_login)

        layout.addWidget(QLabel("Пароль:"))
        self.inp_password = QLineEdit()
        self.inp_password.setMaxLength(50) # Ограничение: Макс 50 символов
        layout.addWidget(self.inp_password)

        layout.addWidget(QLabel("ПІБ:"))
        self.inp_full_name = QLineEdit()
        self.inp_full_name.setMaxLength(100) # Ограничение: Макс 100 символов
        layout.addWidget(self.inp_full_name)

        layout.addWidget(QLabel("Телефон:"))
        self.inp_phone = QLineEdit()
        self.inp_phone.setMaxLength(13) # Ограничение: Макс 13 символов
        self.inp_phone.setPlaceholderText("+380...")
        # Ограничение: Только цифры и плюс
        self.inp_phone.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\+?[0-9]*$")))
        layout.addWidget(self.inp_phone)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Зберегти")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Скасувати")
        
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)

        if self.doctor:
            self._fill_data()

    def validate_and_accept(self):
        # Защита от дурака
        if len(self.inp_login.text().strip()) < 4:
            QMessageBox.warning(self, "Помилка", "Логін має бути не менше 4 символів")
            return
        if len(self.inp_password.text().strip()) < 4:
            QMessageBox.warning(self, "Помилка", "Пароль має бути не менше 4 символів")
            return
        if not self.inp_full_name.text().strip():
            QMessageBox.warning(self, "Помилка", "ПІБ обов'язкове")
            return
        if len(self.inp_phone.text().strip()) < 10:
            QMessageBox.warning(self, "Помилка", "Телефон занадто короткий")
            return
            
        self.accept()

    def get_data(self):
        return {
            'login': self.inp_login.text(),
            'password': self.inp_password.text(),
            'full_name': self.inp_full_name.text(),
            'phone': self.inp_phone.text()
        }
    
    def _fill_data(self):
        self.inp_login.setText(str(self.doctor['login']))
        self.inp_password.setText(str(self.doctor['password']))
        self.inp_full_name.setText(str(self.doctor['full_name']))
        self.inp_phone.setText(str(self.doctor['phone']))