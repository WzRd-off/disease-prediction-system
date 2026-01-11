from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, 
    QMessageBox, QDialogButtonBox, QComboBox, QDateEdit
)
from PyQt6.QtCore import QDate

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
        layout.addWidget(self.inp_rnkop)

        # ПІБ
        layout.addWidget(QLabel("ПІБ:"))
        self.inp_name = QLineEdit()
        layout.addWidget(self.inp_name)

        # Дата рождения
        layout.addWidget(QLabel("Дата народження:"))
        self.inp_birth = QDateEdit()
        self.inp_birth.setCalendarPopup(True)
        self.inp_birth.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.inp_birth)

        # Адрес
        layout.addWidget(QLabel("Адреса:"))
        self.inp_address = QLineEdit()
        layout.addWidget(self.inp_address)

        # Телефон
        layout.addWidget(QLabel("Телефон:"))
        self.inp_phone = QLineEdit()
        layout.addWidget(self.inp_phone)

        # Врач (ComboBox)
        layout.addWidget(QLabel("Лікуючий лікар:"))
        self.combo_doctor = QComboBox()
        self._load_doctors()
        layout.addWidget(self.combo_doctor)

        # Комментар
        layout.addWidget(QLabel("Коментар (Особливості):"))
        self.inp_comments = QLineEdit()
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
            self.inp_rnkop.setReadOnly(True) # Нельзя менять ID

    def _load_doctors(self):
        doctors = self.db_manager.get_users_by_role_and_clinic('doctor', self.clinic_id)
        for doc in doctors:
            self.combo_doctor.addItem(f"{doc['full_name']} (Login: {doc['login']})", doc['user_id'])

    def validate_and_accept(self):
        if not self.inp_rnkop.text().strip():
            QMessageBox.warning(self, "Помилка", "РНКОПП обов'язковий")
            return
        if not self.inp_name.text().strip():
            QMessageBox.warning(self, "Помилка", "ПІБ обов'язкове")
            return
        if self.combo_doctor.currentIndex() == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть лікаря (Потрібно спочатку додати лікарів у систему)")
            return
        self.accept()

    def get_data(self):

        current_status = 'healthy'
        if self.patient:
            current_status = self.patient['status']

        return {
            'rnkop': self.inp_rnkop.text(),
            'full_name': self.inp_name.text(),
            'birth_date': self.inp_birth.date().toString("yyyy-MM-dd"),
            'address': self.inp_address.text(),
            'phone': self.inp_phone.text(),
            'doctor_id': self.combo_doctor.currentData(),
            'status': current_status, # Автоматический статус (новый=healthy, старый=сохраняется)
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
        
        # Установка врача
        index_doc = self.combo_doctor.findData(self.patient['doctor_id'])
        if index_doc >= 0:
            self.combo_doctor.setCurrentIndex(index_doc)