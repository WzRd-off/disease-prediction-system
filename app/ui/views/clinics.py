from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox,
    QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QHeaderView, QTableWidgetItem
)

from app.ui.dialogs.clinic_dialog import ClinicDialog
from app.ui.styles import BTN_SUCCESS, BTN_DANGER


class ClinicsView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager 
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("Керування Клініками")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        # Панель кнопок
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Додати клініку")
        self.btn_edit = QPushButton("Редагувати")
        self.btn_delete = QPushButton("Видалити")
        self.btn_add.setStyleSheet(BTN_SUCCESS)     
        self.btn_delete.setStyleSheet(BTN_DANGER) 
        
        for btn in [self.btn_add, self.btn_edit, self.btn_delete]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_add.setStyleSheet("background-color: #27ae60; color: white; padding: 5px;")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6) 
        self.table.setHorizontalHeaderLabels(["ID", "Назва", "ID Району", "Адреса", "Email", "Телефон"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # События
        self.btn_add.clicked.connect(self.add_clinic)
        self.btn_edit.clicked.connect(self.edit_clinic)
        self.btn_delete.clicked.connect(self.delete_clinic)

        self.setLayout(layout)

    def showEvent(self, event):
        self.refresh_table()
        super().showEvent(event)

    def refresh_table(self):
        self.table.setRowCount(0)
        clinics = self.db_manager.get_all_clinics()
        
        if not clinics:
            return

        for row_idx, clinic in enumerate(clinics):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(clinic['clinic_id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(clinic['clinic_name'])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(clinic['local_id']) if clinic['local_id'] else "-"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(clinic['address'])))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(clinic['email'])))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(clinic['phone'])))

    def get_selected_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items: return None
        return int(self.table.item(selected_items[0].row(), 0).text())

    def add_clinic(self):
        dialog = ClinicDialog(self.db_manager, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            res = self.db_manager.add_clinic(
                data['name'], data['local_id'], data['address'], data['email'], data['phone']
            )
            if res:
                self.refresh_table()
                QMessageBox.information(self, "Успіх", f"Клініка '{data['name']}' додана! ID: {res}")
            else:
                QMessageBox.critical(self, "Помилка", "Не вдалося додати клініку.")

    def edit_clinic(self):
        clinic_id = self.get_selected_id()
        if not clinic_id: return
        
        all_clinics = self.db_manager.get_all_clinics()
        target = next((c for c in all_clinics if c['clinic_id'] == clinic_id), None)
        
        if target:
            dialog = ClinicDialog(self.db_manager, clinic=target, parent=self)
            if dialog.exec():
                data = dialog.get_data()
                self.db_manager.update_clinic(
                    clinic_id, data['name'], data['local_id'], data['address'], data['email'], data['phone']
                )
                self.refresh_table()

    def delete_clinic(self):
        clinic_id = self.get_selected_id()
        if not clinic_id: return
        
        reply = QMessageBox.question(
            self, "Видалити?", 
            "Ви впевнені? Якщо у клініки є історія хвороб, вона буде архівована, а не видалена.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = self.db_manager.delete_clinic(clinic_id)
            
            if result == 'deleted':
                QMessageBox.information(self, "Успіх", "Клініка була успішно видалена (історії не знайдено).")
            elif result == 'archived':
                QMessageBox.warning(self, "Архівація", "Клініка була переміщена в АРХІВ, оскільки містить історію хвороб.")
            else:
                QMessageBox.critical(self, "Помилка", "Не вдалося видалити клініку.")
                
            self.refresh_table()