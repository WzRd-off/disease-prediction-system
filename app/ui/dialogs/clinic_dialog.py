from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, 
    QMessageBox, QDialogButtonBox, QComboBox
)

class ClinicDialog(QDialog):
    def __init__(self, db_manager, clinic=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.clinic = clinic
        
        self.setWindowTitle("Додати клініку" if not self.clinic else "Редагувати клініку")
        self.setFixedSize(400, 400)
        
        layout = QVBoxLayout()
        
        # 1. Название
        layout.addWidget(QLabel("Назва клініки:"))
        self.inp_name = QLineEdit()
        layout.addWidget(self.inp_name)

        # 2. Локация (Заменяем QLineEdit на QComboBox)
        layout.addWidget(QLabel("Район (Local):"))
        self.combo_local = QComboBox()
        self._load_locals()
        layout.addWidget(self.combo_local)

        # 3. Адрес
        layout.addWidget(QLabel("Адреса:"))
        self.inp_address = QLineEdit()
        layout.addWidget(self.inp_address)

        # 4. Email
        layout.addWidget(QLabel("E-mail:"))
        self.inp_email = QLineEdit()
        layout.addWidget(self.inp_email)

        # 5. Телефон
        layout.addWidget(QLabel("Телефон:"))
        self.inp_phone = QLineEdit()
        layout.addWidget(self.inp_phone)
        
        # Кнопки
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Зберегти")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Скасувати")
        
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        self.setLayout(layout)

        if self.clinic:
            self._fill_data()

    def _load_locals(self):
        """Загружаем районы из БД"""
        locals_list = self.db_manager.get_all_locals()
        for loc in locals_list:
            # Формируем красивое название: Район (Область)
            region_name = loc['region_name'] if 'region_name' in loc.keys() and loc['region_name'] else "Unknown"
            display_text = f"{loc['local_name']} ({region_name})"
            self.combo_local.addItem(display_text, loc['local_id'])

    def validate_and_accept(self):
        if not self.inp_name.text().strip():
            QMessageBox.warning(self, "Помилка", "Назва не може бути порожньою")
            return
        
        if self.combo_local.currentIndex() == -1:
             QMessageBox.warning(self, "Помилка", "Оберіть район зі списку! Якщо список порожній - створіть район у Довідниках.")
             return

        self.accept()

    def get_data(self):
        return {
            'name': self.inp_name.text(),
            'local_id': self.combo_local.currentData(),
            'address': self.inp_address.text(),
            'email': self.inp_email.text(),
            'phone': self.inp_phone.text()
        }
    
    def _fill_data(self): 
        self.inp_name.setText(str(self.clinic['clinic_name']))
        self.inp_address.setText(str(self.clinic['address']))
        self.inp_email.setText(str(self.clinic['email']))
        self.inp_phone.setText(str(self.clinic['phone']))
        
        # Устанавливаем выбранный район
        local_id = self.clinic['local_id']
        if local_id:
             index = self.combo_local.findData(local_id)
             if index >= 0:
                 self.combo_local.setCurrentIndex(index)