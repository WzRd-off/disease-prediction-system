from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QHeaderView, QTableWidgetItem
)

class AdminsView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        layout = QVBoxLayout()
        
        header = QLabel("Адміністратори Системи")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        self.table = QTableWidget()
        cols = ["ID", "Логін", "ПІБ", "Телефон"]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def showEvent(self, event):
        self.refresh_table()
        super().showEvent(event)

    def refresh_table(self):
        self.table.setRowCount(0)
        admins = self.db_manager.get_all_admins()
        
        for i, adm in enumerate(admins):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(adm['user_id'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(adm['login'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(adm['full_name'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(adm['phone'])))