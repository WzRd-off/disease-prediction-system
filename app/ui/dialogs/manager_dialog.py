from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, 
    QLabel, QMessageBox, QDialogButtonBox, QComboBox
)

class ManagerDialog(QDialog):
    def __init__(self, db_manager, manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.manager = manager # Если None = создание, если dict = редактирование
        
        self.setWindowTitle("Додати менеджера" if not self.manager else "Редагувати менеджера")
        self.setFixedSize(400, 400)
        
        layout = QVBoxLayout()
        
        # 1. Логин
        layout.addWidget(QLabel("Логін:"))
        self.inp_login = QLineEdit()
        layout.addWidget(self.inp_login)

        # 2. Пароль
        layout.addWidget(QLabel("Пароль:"))
        self.inp_password = QLineEdit()
        layout.addWidget(self.inp_password)

        # 3. ФИО
        layout.addWidget(QLabel("ПІБ:"))
        self.inp_full_name = QLineEdit()
        layout.addWidget(self.inp_full_name)

        # 4. Клиника (Заменяем QLineEdit на QComboBox)
        layout.addWidget(QLabel("Клініка:"))
        self.combo_clinic = QComboBox()
        self._load_clinics()
        layout.addWidget(self.combo_clinic)

        # 5. Телефон
        layout.addWidget(QLabel("Номер Телефону:"))
        self.inp_phone = QLineEdit()
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
        """Загружаем список клиник в ComboBox"""
        clinics = self.db_manager.get_all_clinics()
        for clinic in clinics:
            # Отображаем название, но храним ID как hidden data
            self.combo_clinic.addItem(f"{clinic['clinic_name']} (ID: {clinic['clinic_id']})", clinic['clinic_id'])

    def validate_and_accept(self):
        if not self.inp_login.text().strip():
            QMessageBox.warning(self, "Помилка", "Ім'я користувача не може бути порожнім")
            return

        if not self.inp_password.text().strip():
            QMessageBox.warning(self, "Помилка", "Пароль не може бути порожнім")
            return
        
        if len(self.inp_password.text()) < 4:
            QMessageBox.warning(self, "Помилка", "Пароль має містити щонайменше 4 символи")
            return

        if not self.inp_full_name.text().strip():
            QMessageBox.warning(self, "Помилка", "ПІБ не може бути порожнім")
            return

        if self.combo_clinic.currentIndex() == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть клініку зі списку! Якщо список порожній - створіть клініку.")
            return

        if not self.inp_phone.text().strip():
            QMessageBox.warning(self, "Помилка", "Номер телефону не може бути порожнім")
            return
        
        self.accept()

    def get_data(self):
        """Возвращает введенные данные в виде словаря"""
        return {
            'login': self.inp_login.text(),
            'password': self.inp_password.text(),
            'full_name': self.inp_full_name.text(),
            'clinic_id': self.combo_clinic.currentData(), # Берем ID из данных элемента
            'phone': self.inp_phone.text()
        }
    
    def _fill_data(self): 
        """Заполняет поля данными из self.manager"""
        self.inp_login.setText(str(self.manager['login']))
        self.inp_password.setText(str(self.manager['password']))
        self.inp_full_name.setText(str(self.manager['full_name']))
        self.inp_phone.setText(str(self.manager['phone']))
        
        # Выбираем правильную клинику в списке
        clinic_id = self.manager['clinic_id']
        index = self.combo_clinic.findData(clinic_id)
        if index >= 0:
            self.combo_clinic.setCurrentIndex(index)