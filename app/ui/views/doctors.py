from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox,
    QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QHeaderView, QTableWidgetItem
)

from app.ui.dialogs.doctor_dialog import DoctorDialog

class DoctorsView(QWidget):
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.clinic_id = self.user['clinic_id'] # ID клиники менеджера

        layout = QVBoxLayout()
        
        header = QLabel(f"Керування лікарями (Клініка ID: {self.clinic_id})")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Додати лікаря")
        self.btn_edit = QPushButton("Редагувати")
        self.btn_delete = QPushButton("Видалити")
        self.btn_add.setStyleSheet("background-color: #27ae60; color: white;")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5) 
        self.table.setHorizontalHeaderLabels(["ID", "Логін", "Пароль", "ПІБ", "Телефон"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_doctor)
        self.btn_edit.clicked.connect(self.edit_doctor)
        self.btn_delete.clicked.connect(self.delete_doctor)

        self.setLayout(layout)

    def showEvent(self, event):
        self.refresh_table()
        super().showEvent(event)

    def refresh_table(self):
        self.table.setRowCount(0)
        # Получаем врачей ТОЛЬКО этой клиники
        doctors = self.db_manager.get_users_by_role_and_clinic('doctor', self.clinic_id)
        
        for i, doc in enumerate(doctors):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(doc['user_id'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(doc['login'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(doc['password'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(doc['full_name'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(doc['phone'])))

    def get_selected_id(self):
        items = self.table.selectedItems()
        if not items: return None
        return int(self.table.item(items[0].row(), 0).text())

    def add_doctor(self):
        dialog = DoctorDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            # Добавляем врача в ту же клинику, где и менеджер
            self.db_manager.add_user(data['login'], data['password'], data['full_name'], self.clinic_id, data['phone'], 'doctor')
            self.refresh_table()

    def edit_doctor(self):
        doc_id = self.get_selected_id()
        if not doc_id: return
        doctors = self.db_manager.get_users_by_role_and_clinic('doctor', self.clinic_id)
        target = next((d for d in doctors if d['user_id'] == doc_id), None)
        
        if target:
            dialog = DoctorDialog(doctor=target, parent=self)
            if dialog.exec():
                data = dialog.get_data()
                self.db_manager.update_user(doc_id, data['login'], data['password'], data['full_name'], self.clinic_id, data['phone'])
                self.refresh_table()

    def delete_doctor(self):
        doc_id = self.get_selected_id()
        if not doc_id: return
        if QMessageBox.question(self, "?", "Видалити лікаря?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_user(doc_id)
            self.refresh_table()