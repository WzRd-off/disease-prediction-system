from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QDialogButtonBox

class ManagerDialog(QDialog):
    def __init__(self, db_manager, manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.manager = manager
        self.setWindowTitle("Додати інвертор" if not self.manager else "Редагувати інвертор")
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout()
        
        self.inp_login = QLineEdit()
        layout.addWidget(QLabel("Логін:"))
        self.inp_login = QLineEdit(self.manager['login'])
        layout.addWidget(self.inp_login)

        self.inp_password = QLineEdit()
        layout.addWidget(QLabel("Пароль:"))
        self.inp_password = QLineEdit(self.manager['password'])
        layout.addWidget(self.inp_password)

        self.inp_full_name = QLineEdit()
        layout.addWidget(QLabel("ПІБ:"))
        self.inp_full_name = QLineEdit(self.manager['full_name'])
        layout.addWidget(self.inp_full_name)

        self.inp_clinic_id = QLineEdit()
        layout.addWidget(QLabel("Номер клініки:"))
        self.inp_clinic_id = QLineEdit(self.manager['clinic_id'])
        layout.addWidget(self.inp_clinic_id)

        self.inp_phone = QLineEdit()
        layout.addWidget(QLabel("Номер Телефону:"))
        self.inp_phone = QLineEdit(self.manager['phone'])
        layout.addWidget(self.inp_phone)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)

        if self.manager:
            self._fill_data()

    def validate_and_accept(self):
        if not self.inp_login.text().strip():
            QMessageBox.warning(self, "Помилка", "Ім'я користувача не може бути порожнім")
            return

        if not self.inp_password.text().strip():
            QMessageBox.warning(self, "Помилка", "Пароль не може бути порожнім")
            return
        
        if len(self.inp_password.text()) < 5:
            QMessageBox.warning(self, "Помилка", "Пароль має містити щонайменше 6 символів")
            return

        if not self.inp_full_name.text().strip():
            QMessageBox.warning(self, "Помилка", "ПІБ не може бути порожнім")
            return

        if not self.inp_clinic_id.text().strip():
            QMessageBox.warning(self, "Помилка", "Номер клініки не може бути порожнім")
            return
        if not self.inp_clinic_id.text().isdigit():
            QMessageBox.warning(self, "Помилка", "Номер клініки має бути числом")
            return

        if not self.inp_phone.text().strip():
            QMessageBox.warning(self, "Помилка", "Номер телефону не може бути порожнім")
            return
        
        self.accept()

    def get_data(self):
        return {
            'login': self.inp_login.text(),
            'password': self.inp_password.text(),
            'full_name': self.inp_full_name.text(),
            'clinic_id': self.inp_clinic_id.text(),
            'phone': self.inp_phone.text()
        }
    
    def _fill_data(self): 
        self.inp_login.setText(self.manager['login'])
        self.inp_password.setText(self.manager['password'])
        self.inp_full_name.setText(self.manager['full_name'])
        self.inp_clinic_id.setText(self.manager['clinic_id'])
        self.inp_phone.setText(self.manager['phone'])

