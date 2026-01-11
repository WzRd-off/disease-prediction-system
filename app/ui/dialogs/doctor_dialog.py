from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, 
    QMessageBox, QDialogButtonBox
)

class DoctorDialog(QDialog):
    def __init__(self, doctor=None, parent=None):
        super().__init__(parent)
        self.doctor = doctor
        
        self.setWindowTitle("Додати лікаря" if not self.doctor else "Редагувати лікаря")
        self.setFixedSize(350, 350)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Логін:"))
        self.inp_login = QLineEdit()
        layout.addWidget(self.inp_login)

        layout.addWidget(QLabel("Пароль:"))
        self.inp_password = QLineEdit()
        layout.addWidget(self.inp_password)

        layout.addWidget(QLabel("ПІБ:"))
        self.inp_full_name = QLineEdit()
        layout.addWidget(self.inp_full_name)

        layout.addWidget(QLabel("Телефон:"))
        self.inp_phone = QLineEdit()
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
        if not self.inp_login.text().strip():
            QMessageBox.warning(self, "Помилка", "Логін обов'язковий")
            return
        if not self.inp_password.text().strip():
            QMessageBox.warning(self, "Помилка", "Пароль обов'язковий")
            return
        if not self.inp_full_name.text().strip():
            QMessageBox.warning(self, "Помилка", "ПІБ обов'язкове")
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