from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, 
    QLabel, QMessageBox, QDialogButtonBox, QComboBox
)

class ManagerDialog(QDialog):
    def __init__(self, db_manager, manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.manager = manager 
        
        self.setWindowTitle("Додати менеджера" if not self.manager else "Редагувати менеджера")
        self.setFixedSize(400, 450)
        
        layout = QVBoxLayout()
        
        # 1. Логин
        layout.addWidget(QLabel("Логін:"))
        self.inp_login = QLineEdit()
        self.inp_login.setMaxLength(30) # Ограничение: Максимум 30 символов
        # Ограничение: Только английские буквы, цифры и подчеркивание
        login_validator = QRegularExpressionValidator(QRegularExpression(r"^[a-zA-Z0-9_]+$"))
        self.inp_login.setValidator(login_validator)
        layout.addWidget(self.inp_login)

        # 2. Пароль
        layout.addWidget(QLabel("Пароль:"))
        self.inp_password = QLineEdit()
        self.inp_password.setMaxLength(50) # Ограничение: Максимум 50 символов
        # Пароль скрывать не будем для удобства ввода администратором, но можно добавить setEchoMode
        layout.addWidget(self.inp_password)

        # 3. ФИО
        layout.addWidget(QLabel("ПІБ:"))
        self.inp_full_name = QLineEdit()
        self.inp_full_name.setMaxLength(100) # Ограничение: Максимум 100 символов
        layout.addWidget(self.inp_full_name)

        # 4. Клиника
        layout.addWidget(QLabel("Клініка:"))
        self.combo_clinic = QComboBox()
        self._load_clinics()
        layout.addWidget(self.combo_clinic)

        # 5. Телефон
        layout.addWidget(QLabel("Номер Телефону:"))
        self.inp_phone = QLineEdit()
        self.inp_phone.setMaxLength(13) # Ограничение: Максимум 13 символов (+380...)
        self.inp_phone.setPlaceholderText("+380...")
        # Ограничение: Разрешены только цифры и знак '+' в начале
        phone_validator = QRegularExpressionValidator(QRegularExpression(r"^\+?[0-9]*$"))
        self.inp_phone.setValidator(phone_validator)
        layout.addWidget(self.inp_phone)
        
        # --- КНОПКИ ---
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Зберегти")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Скасувати")

        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)

        if self.manager:
            self._fill_data()

    def _load_clinics(self):
        clinics = self.db_manager.get_all_clinics()
        for clinic in clinics:
            self.combo_clinic.addItem(f"{clinic['clinic_name']} (ID: {clinic['clinic_id']})", clinic['clinic_id'])

    def validate_and_accept(self):
        # Защита от дурака: Проверка на пустоту и длину
        if len(self.inp_login.text().strip()) < 4:
            QMessageBox.warning(self, "Помилка", "Логін має бути не менше 4 символів")
            return

        if len(self.inp_password.text().strip()) < 4:
            QMessageBox.warning(self, "Помилка", "Пароль має містити щонайменше 4 символи")
            return

        if not self.inp_full_name.text().strip():
            QMessageBox.warning(self, "Помилка", "ПІБ не може бути порожнім")
            return

        if self.combo_clinic.currentIndex() == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть клініку зі списку!")
            return

        # Проверка длины телефона (минимум 10 цифр)
        phone_text = self.inp_phone.text().strip()
        if len(phone_text) < 10:
            QMessageBox.warning(self, "Помилка", "Некоректний номер телефону (мінімум 10 цифр)")
            return
        
        self.accept()

    def get_data(self):
        return {
            'login': self.inp_login.text(),
            'password': self.inp_password.text(),
            'full_name': self.inp_full_name.text(),
            'clinic_id': self.combo_clinic.currentData(), 
            'phone': self.inp_phone.text()
        }
    
    def _fill_data(self): 
        self.inp_login.setText(str(self.manager['login']))
        self.inp_password.setText(str(self.manager['password']))
        self.inp_full_name.setText(str(self.manager['full_name']))
        self.inp_phone.setText(str(self.manager['phone']))
        
        clinic_id = self.manager['clinic_id']
        index = self.combo_clinic.findData(clinic_id)
        if index >= 0:
            self.combo_clinic.setCurrentIndex(index)