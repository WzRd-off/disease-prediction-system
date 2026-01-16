from PyQt6.QtCore import QDate, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, 
    QMessageBox, QDialogButtonBox, QComboBox, QDateEdit
)

class PatientDialog(QDialog):
    def __init__(self, db_manager, clinic_id, patient=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.clinic_id = clinic_id
        self.patient = patient
        
        self.setWindowTitle("Картка пацієнта")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout()
        
        # РНКОПП
        layout.addWidget(QLabel("РНКОПП (Код пацієнта):"))
        self.inp_rnkop = QLineEdit()
        self.inp_rnkop.setMaxLength(10) # Ограничение: Строго 10 символов
        # Ограничение: Только цифры
        self.inp_rnkop.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[0-9]*$")))
        self.inp_rnkop.setPlaceholderText("10 цифр")
        layout.addWidget(self.inp_rnkop)

        # ПІБ
        layout.addWidget(QLabel("ПІБ:"))
        self.inp_name = QLineEdit()
        self.inp_name.setMaxLength(100) # Ограничение: Макс 100 символов
        layout.addWidget(self.inp_name)

        # Дата рождения
        layout.addWidget(QLabel("Дата народження:"))
        self.inp_birth = QDateEdit()
        self.inp_birth.setCalendarPopup(True)
        self.inp_birth.setDisplayFormat("yyyy-MM-dd")
        self.inp_birth.setMaximumDate(QDate.currentDate()) # Ограничение: Нельзя родиться в будущем
        layout.addWidget(self.inp_birth)

        # Адрес
        layout.addWidget(QLabel("Адреса:"))
        self.inp_address = QLineEdit()
        self.inp_address.setMaxLength(150) # Ограничение: Макс 150 символов
        layout.addWidget(self.inp_address)

        # Телефон
        layout.addWidget(QLabel("Телефон:"))
        self.inp_phone = QLineEdit()
        self.inp_phone.setMaxLength(13) # Ограничение: Макс 13 символов
        self.inp_phone.setPlaceholderText("+380...")
        self.inp_phone.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\+?[0-9]*$")))
        layout.addWidget(self.inp_phone)

        # Врач (ComboBox)
        layout.addWidget(QLabel("Лікуючий лікар:"))
        self.combo_doctor = QComboBox()
        self._load_doctors()
        layout.addWidget(self.combo_doctor)

        # Коментар
        layout.addWidget(QLabel("Коментар (Особливості):"))
        self.inp_comments = QLineEdit()
        self.inp_comments.setMaxLength(255) # Ограничение: Макс 255 символов
        layout.addWidget(self.inp_comments)
        
        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Зберегти")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Скасувати")
        
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)

        if self.patient:
            self._fill_data()
            self.inp_rnkop.setReadOnly(True) # Нельзя менять ID после создания

    def _load_doctors(self):
        doctors = self.db_manager.get_users_by_role_and_clinic('doctor', self.clinic_id)
        for doc in doctors:
            self.combo_doctor.addItem(f"{doc['full_name']} (Login: {doc['login']})", doc['user_id'])

    def validate_and_accept(self):
        # Защита от дурака
        if len(self.inp_rnkop.text().strip()) != 10:
            QMessageBox.warning(self, "Помилка", "РНКОПП має складатись рівно з 10 цифр")
            return
        if not self.inp_name.text().strip():
            QMessageBox.warning(self, "Помилка", "ПІБ обов'язкове")
            return
        if self.combo_doctor.currentIndex() == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть лікаря")
            return
        self.accept()

    def get_data(self):
        current_status = 'healthy'
        if self.patient:
            current_status = self.patient.get('status', 'healthy')

        return {
            'rnkop': self.inp_rnkop.text(),
            'full_name': self.inp_name.text(),
            'birth_date': self.inp_birth.date().toString("yyyy-MM-dd"),
            'address': self.inp_address.text(),
            'phone': self.inp_phone.text(),
            'doctor_id': self.combo_doctor.currentData(),
            'status': current_status, 
            'comments': self.inp_comments.text()
        }
    
    def _fill_data(self):
        self.inp_rnkop.setText(str(self.patient['rnkop_code']))
        self.inp_name.setText(str(self.patient['full_name']))
        
        qdate = QDate.fromString(str(self.patient['birth_date']), "yyyy-MM-dd")
        self.inp_birth.setDate(qdate)
        
        self.inp_address.setText(str(self.patient['address']))
        self.inp_phone.setText(str(self.patient['phone']))
        self.inp_comments.setText(str(self.patient['comments']))
        
        index_doc = self.combo_doctor.findData(self.patient['doctor_id'])
        if index_doc >= 0:
            self.combo_doctor.setCurrentIndex(index_doc)