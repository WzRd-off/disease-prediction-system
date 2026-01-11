from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox,
    QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QHeaderView, QTableWidgetItem
)

from app.ui.dialogs.manager_dialog import ManagerDialog
from app.ui.styles import BTN_SUCCESS, BTN_DANGER

class ManagersView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        layout = QVBoxLayout()
        
        header = QLabel("Керування менеджерами")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Додати менеджера")
        self.btn_edit = QPushButton("Редагувати")
        self.btn_delete = QPushButton("Видалити")
        self.btn_add.setStyleSheet(BTN_SUCCESS)     
        self.btn_delete.setStyleSheet(BTN_DANGER) 
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6) 
        self.table.setHorizontalHeaderLabels(["ID", "Логін", "Пароль", "ПІБ", "ID клініки", "Номер телефон"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_man)
        self.btn_edit.clicked.connect(self.edit_man)
        self.btn_delete.clicked.connect(self.delete_man)

        self.setLayout(layout)

    def showEvent(self, event):
        self.refresh_table()
        super().showEvent(event)

    def refresh_table(self):
        self.table.setRowCount(0)
        managers = self.db_manager.get_all_managers()
        
        for row_idx, manager in enumerate(managers):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(manager['user_id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(manager['login'])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(manager['password'])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(manager['full_name'])))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(manager['clinic_id'])))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(manager['phone'])))

    def get_selected_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items: return None
        return int(self.table.item(selected_items[0].row(), 0).text())

    def add_man(self):
        dialog = ManagerDialog(self.db_manager, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            self.db_manager.add_manager(data['login'], data['password'], data['full_name'], data['clinic_id'], data['phone'])
            self.refresh_table()

    def edit_man(self):
        manager_id = self.get_selected_id()
        if not manager_id: return
        all_managers = self.db_manager.get_all_managers()
        target = next((i for i in all_managers if i['user_id'] == manager_id), None)
        if target:
            dialog = ManagerDialog(self.db_manager, manager=target, parent=self)
            if dialog.exec():
                data = dialog.get_data()
                self.db_manager.update_manager(manager_id, data['login'], data['password'], data['full_name'], data['clinic_id'], data['phone'])
                self.refresh_table()

    def delete_man(self):
        manager_id = self.get_selected_id()
        if not manager_id: return
        if QMessageBox.question(self, "?", "Видалити?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_manager(manager_id)
            self.refresh_table()