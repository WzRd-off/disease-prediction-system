from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, 
    QMessageBox, QDialogButtonBox, QComboBox, QDateEdit, QCheckBox, QTextEdit
)
from PyQt6.QtCore import QDate

class IllnessDialog(QDialog):
    def __init__(self, db_manager, clinic_id, history=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.clinic_id = clinic_id
        self.history = history
        
        self.setWindowTitle("Запис історії хвороби" if not self.history else "Редагування запису")
        self.setFixedSize(450, 600)
        
        layout = QVBoxLayout()
        
        # Пациент (ComboBox)
        layout.addWidget(QLabel("Пацієнт:"))
        self.combo_patient = QComboBox()
        self._load_patients()
        layout.addWidget(self.combo_patient)

        # Хвороба (ComboBox)
        layout.addWidget(QLabel("Хвороба (МКХ):"))
        self.combo_disease = QComboBox()
        self._load_diseases()
        layout.addWidget(self.combo_disease)

        # Локация (Де захворів)
        layout.addWidget(QLabel("Місце звернення (Район):"))
        self.combo_local = QComboBox()
        self._load_locals()
        layout.addWidget(self.combo_local)

        # Дата звернення
        layout.addWidget(QLabel("Дата звернення:"))
        self.inp_date = QDateEdit()
        self.inp_date.setCalendarPopup(True)
        self.inp_date.setDate(QDate.currentDate())
        self.inp_date.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.inp_date)

        # Хронічна?
        self.chk_chronic = QCheckBox("Хронічне захворювання")
        layout.addWidget(self.chk_chronic)

        # Статус
        layout.addWidget(QLabel("Статус перебігу:"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["хворіє", "одужав", "помер"])
        layout.addWidget(self.combo_status)

        # Призначення (Багаторядкове)
        layout.addWidget(QLabel("Призначення лікаря:"))
        self.txt_prescription = QTextEdit()
        layout.addWidget(self.txt_prescription)
        
        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)

        if self.history:
            self._fill_data()
            # Пациента менять нельзя при редактировании истории (логично)
            self.combo_patient.setEnabled(False) 

    def _load_patients(self):
        # Завантажуємо пацієнтів клініки
        patients = self.db_manager.get_patients_by_clinic(self.clinic_id)
        for p in patients:
            self.combo_patient.addItem(f"{p['full_name']} ({p['rnkop_code']})", p['rnkop_code'])

    def _load_diseases(self):
        # Потрібні хвороби. Якщо їх немає, список буде порожнім.
        diseases = self.db_manager.get_all_diseases()
        if not diseases:
            self.combo_disease.addItem("Спочатку додайте хвороби у Довідники!", None)
            return
        for d in diseases:
            self.combo_disease.addItem(f"{d['ill_name']} ({d['ccode']})", d['ccode'])

    def _load_locals(self):
        locals_list = self.db_manager.get_all_locals()
        for loc in locals_list:
            region = loc['region_name'] if 'region_name' in loc.keys() else "Unknown"
            self.combo_local.addItem(f"{loc['local_name']} ({region})", loc['local_id'])

    def validate_and_accept(self):
        if self.combo_patient.currentIndex() == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть пацієнта!")
            return
        if self.combo_disease.currentData() is None:
            QMessageBox.warning(self, "Помилка", "Оберіть хворобу!")
            return
        if self.combo_local.currentIndex() == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть місце звернення!")
            return
        
        self.accept()

    def get_data(self):
        return {
            'patient_code': self.combo_patient.currentData(),
            'ill_code': self.combo_disease.currentData(),
            'local_id': self.combo_local.currentData(),
            'visit_date': self.inp_date.date().toString("yyyy-MM-dd"),
            'is_chronic': self.chk_chronic.isChecked(),
            'status': self.combo_status.currentText(),
            'prescription': self.txt_prescription.toPlainText()
        }
    
    def _fill_data(self):
        # Встановлюємо пацієнта
        index_p = self.combo_patient.findData(self.history['patient_code'])
        if index_p >= 0: self.combo_patient.setCurrentIndex(index_p)

        # Встановлюємо хворобу
        index_d = self.combo_disease.findData(self.history['ill_code'])
        if index_d >= 0: self.combo_disease.setCurrentIndex(index_d)

        # Встановлюємо локацію
        index_l = self.combo_local.findData(self.history['local_id'])
        if index_l >= 0: self.combo_local.setCurrentIndex(index_l)

        # Дата
        qdate = QDate.fromString(str(self.history['visit_date']), "yyyy-MM-dd")
        self.inp_date.setDate(qdate)

        # Чекбокс
        self.chk_chronic.setChecked(bool(self.history['is_chronic']))

        # Статус
        index_s = self.combo_status.findText(self.history['status'])
        if index_s >= 0: self.combo_status.setCurrentIndex(index_s)

        # Призначення
        self.txt_prescription.setText(str(self.history['prescription']))