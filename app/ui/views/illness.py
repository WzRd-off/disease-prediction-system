from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox, QHBoxLayout, 
    QLabel, QPushButton, QTableWidget, QHeaderView, QTableWidgetItem
)
from app.ui.dialogs.illness_dialog import IllnessDialog

class IllnessView(QWidget):
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.clinic_id = self.user['clinic_id']

        layout = QVBoxLayout()
        
        header = QLabel("Історія Хвороб (Прийоми)")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Новий запис (Прийом)")
        self.btn_edit = QPushButton("Редагувати")
        self.btn_delete = QPushButton("Видалити")
        
        self.btn_add.setStyleSheet("background-color: #27ae60; color: white;")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Таблица
        self.table = QTableWidget()
        cols = ["ID", "Дата", "Пацієнт", "Хвороба", "Статус", "Хронічне", "Місце", "Призначення"]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Події
        self.btn_add.clicked.connect(self.add_record)
        self.btn_edit.clicked.connect(self.edit_record)
        self.btn_delete.clicked.connect(self.delete_record)

        self.setLayout(layout)

    def showEvent(self, event):
        self.refresh_table()
        super().showEvent(event)

    def refresh_table(self):
        self.table.setRowCount(0)
        history = self.db_manager.get_ill_history_by_doctor_clinic(self.clinic_id)
        
        for i, row in enumerate(history):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row['history_id'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row['visit_date'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row['patient_name'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row['ill_name'])))
            
            # Статус
            st_item = QTableWidgetItem(str(row['status']))
            if row['status'] == 'помер': st_item.setForeground(Qt.GlobalColor.red)
            elif row['status'] == 'одужав': st_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(i, 4, st_item)

            self.table.setItem(i, 5, QTableWidgetItem("Так" if row['is_chronic'] else "Ні"))
            
            # Локация (Район + Область)
            loc_text = f"{row['local_name']} ({row['region_name']})"
            self.table.setItem(i, 6, QTableWidgetItem(loc_text))
            
            self.table.setItem(i, 7, QTableWidgetItem(str(row['prescription'])))

    def get_selected_id(self):
        items = self.table.selectedItems()
        if not items: return None
        return int(self.table.item(items[0].row(), 0).text())

    def add_record(self):
        dialog = IllnessDialog(self.db_manager, self.clinic_id, parent=self)
        if dialog.exec():
            d = dialog.get_data()
            self.db_manager.add_ill_history(
                d['patient_code'], d['local_id'], d['ill_code'], 
                d['is_chronic'], d['visit_date'], d['status'], d['prescription']
            )
            
            # ВАЖЛИВО З ТЗ: Якщо статус "помер", оновлюємо статус пацієнта
            if d['status'] == 'помер':
                self.db_manager.update_patient_comment_only(d['patient_code'], "ПОМЕР (Архів)") 
                # Тут можна було б і статус в patient оновити, якщо ми додали це поле.
                # Але оскільки add_patient приймає status, то update теж може.
                # Логіку зміни статусу пацієнта можна доробити.

            self.refresh_table()

    def edit_record(self):
        hist_id = self.get_selected_id()
        if not hist_id: return
        
        history_list = self.db_manager.get_ill_history_by_doctor_clinic(self.clinic_id)
        target = next((h for h in history_list if h['history_id'] == hist_id), None)
        
        if target:
            dialog = IllnessDialog(self.db_manager, self.clinic_id, history=target, parent=self)
            if dialog.exec():
                d = dialog.get_data()
                self.db_manager.update_ill_history(
                    hist_id, d['patient_code'], d['local_id'], d['ill_code'], 
                    d['is_chronic'], d['visit_date'], d['status'], d['prescription']
                )
                self.refresh_table()

    def delete_record(self):
        hist_id = self.get_selected_id()
        if not hist_id: return
        
        if QMessageBox.question(self, "?", "Видалити запис?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_ill_history(hist_id)
            self.refresh_table()