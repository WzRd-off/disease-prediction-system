from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox,
    QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QHeaderView, QTableWidgetItem,
    QLineEdit, QInputDialog
)

from app.ui.dialogs.patient_dialog import PatientDialog
from app.ui.styles import BTN_SUCCESS, BTN_DANGER

class PatientsView(QWidget):
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.clinic_id = self.user['clinic_id']
        self.role = self.user['role'] # 'manager' or 'doctor'

        layout = QVBoxLayout()
        
        title = "База пацієнтів клініки" if self.role == 'manager' else "Мої пацієнти та пацієнти клініки"
        header = QLabel(f"{title} (Клініка ID: {self.clinic_id})")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        # Панель управления
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Новий пацієнт")
        self.btn_edit = QPushButton("Редагувати")
        self.btn_delete = QPushButton("Видалити")
        self.btn_refresh = QPushButton("Оновити")
        self.btn_add.setStyleSheet(BTN_SUCCESS)     
        self.btn_delete.setStyleSheet(BTN_DANGER)   

        
        self.btn_add.setStyleSheet("background-color: #27ae60; color: white;")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Таблица
        self.table = QTableWidget()
        cols = ["РНКОПП", "ПІБ", "Дата нар.", "Адреса", "Телефон", "Статус", "Лікар", "Коментар"]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Подключаем кнопки
        self.btn_add.clicked.connect(self.add_patient)
        self.btn_edit.clicked.connect(self.edit_patient)
        self.btn_delete.clicked.connect(self.delete_patient)
        self.btn_refresh.clicked.connect(self.refresh_table)
        

        self.setLayout(layout)

    def showEvent(self, event):
        self.refresh_table()
        super().showEvent(event)

    def refresh_table(self):
        self.table.setRowCount(0)
        # Загружаем пациентов этой клиники
        patients = self.db_manager.get_patients_by_clinic(self.clinic_id)
        
        for i, p in enumerate(patients):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(p['rnkop_code'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(p['full_name'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(p['birth_date'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(p['address'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(p['phone'])))
            
            # Статус (можно раскрасить)
            status_map = {
                'healthy': 'Здоровий',
                'sick': 'Хворіє',
                'chronic': 'Хронічні',
                'dead': 'Помер'
            }
            status_text = status_map.get(p['status'], p['status'])
            status_item = QTableWidgetItem(status_text)
            
            if p['status'] == 'healthy': status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif p['status'] == 'sick': status_item.setForeground(Qt.GlobalColor.red)
            elif p['status'] == 'chronic': status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif p['status'] == 'dead': status_item.setForeground(Qt.GlobalColor.black)
            
            self.table.setItem(i, 5, status_item)

            self.table.setItem(i, 6, QTableWidgetItem(str(p['doctor_name']) if p['doctor_name'] else "-"))
            self.table.setItem(i, 7, QTableWidgetItem(str(p['comments'])))

            # Сохраняем ID врача в строку для проверки прав
            self.table.item(i, 0).setData(Qt.ItemDataRole.UserRole, p['doctor_id'])

    def get_selected_rnkop(self):
        items = self.table.selectedItems()
        if not items: return None
        return self.table.item(items[0].row(), 0).text()

    def get_selected_doctor_id(self):
        items = self.table.selectedItems()
        if not items: return None
        # Мы сохранили ID врача в UserRole первой ячейки строки
        return self.table.item(items[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def add_patient(self):
        # Добавлять может и Менеджер, и Врач (но для своей клиники)
        dialog = PatientDialog(self.db_manager, self.clinic_id, parent=self)
        if dialog.exec():
            d = dialog.get_data()
            self.db_manager.add_patient(d['rnkop'], d['full_name'], d['birth_date'], d['address'], d['phone'], d['doctor_id'], d['comments'], d['status'])
            self.refresh_table()

    def edit_patient(self):
        rnkop = self.get_selected_rnkop()
        if not rnkop: return
        
        patients = self.db_manager.get_patients_by_clinic(self.clinic_id)
        target = next((p for p in patients if p['rnkop_code'] == rnkop), None)
        if not target: return

        # ЛОГИКА ПРАВ ДОСТУПА ДЛЯ ВРАЧА
        if self.role == 'doctor':
            current_doc_id = self.user['user_id']
            patient_doc_id = target['doctor_id']
            
            # Если пациент чужой -> можно править ТОЛЬКО комментарий
            if patient_doc_id != current_doc_id:
                text, ok = QInputDialog.getText(self, "Редагування коментаря", 
                    f"Ви не лікуючий лікар цього пацієнта.\nВи можете змінити лише коментар:", 
                    QLineEdit.EchoMode.Normal, str(target['comments']))
                if ok:
                    self.db_manager.update_patient_comment_only(rnkop, text)
                    self.refresh_table()
                return

        # Если Менеджер или Свой пациент -> Полное редактирование
        dialog = PatientDialog(self.db_manager, self.clinic_id, patient=target, parent=self)
        if dialog.exec():
            d = dialog.get_data()
            self.db_manager.update_patient(rnkop, d['full_name'], d['birth_date'], d['address'], d['phone'], d['doctor_id'], d['comments'], d['status'])
            self.refresh_table()

    def delete_patient(self):
        # Удалять может только менеджер (или админ, но его тут нет)
        if self.role != 'manager':
            QMessageBox.warning(self, "Відмова", "Видаляти пацієнтів може лише Менеджер.")
            return

        rnkop = self.get_selected_rnkop()
        if not rnkop: return
        
        if QMessageBox.question(self, "Видалити?", f"Видалити пацієнта {rnkop}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_patient(rnkop)
            self.refresh_table()