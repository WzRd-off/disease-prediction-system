from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QHeaderView, QTableWidgetItem,
    QTabWidget, QInputDialog, QMessageBox
)

from app.ui.dialogs.local_dialog import LocalDialog
from app.ui.dialogs.disease_dialog import DiseaseDialog
from app.ui.styles import BTN_SUCCESS, BTN_DANGER

class DirectoriesView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Довідники системи"))
        
        # Вкладки
        self.tabs = QTabWidget()
        self.tab_regions = QWidget()
        self.tab_locals = QWidget()
        self.tab_categories = QWidget() # New
        self.tab_diseases = QWidget()   # New
        
        self.tabs.addTab(self.tab_categories, "Категорії Хвороб")
        self.tabs.addTab(self.tab_diseases, "Хвороби (МКХ)")
        self.tabs.addTab(self.tab_regions, "Регіони")
        self.tabs.addTab(self.tab_locals, "Райони")
        
        self.init_categories_tab()
        self.init_diseases_tab()
        self.init_regions_tab()
        self.init_locals_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def showEvent(self, event):
        self.refresh_all_tabs()
        super().showEvent(event)
    
    def refresh_all_tabs(self):
        self.refresh_regions()
        self.refresh_locals()
        self.refresh_categories()
        self.refresh_diseases()

    # --- 1. КАТЕГОРИИ ---
    def init_categories_tab(self):
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Додати Категорію")
        btn_add.clicked.connect(self.add_category)
        btn_del = QPushButton("Видалити")
        btn_del.clicked.connect(self.delete_category)
        btn_add.setStyleSheet(BTN_SUCCESS)     
        btn_del.setStyleSheet(BTN_DANGER) 
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        btn_layout.addStretch()
        
        self.table_cats = QTableWidget()
        self.table_cats.setColumnCount(2)
        self.table_cats.setHorizontalHeaderLabels(["ID", "Назва Категорії"])
        self.table_cats.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_cats.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_cats.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.table_cats)
        self.tab_categories.setLayout(layout)

    def refresh_categories(self):
        self.table_cats.setRowCount(0)
        cats = self.db_manager.get_all_ill_categories()
        for i, c in enumerate(cats):
            self.table_cats.insertRow(i)
            self.table_cats.setItem(i, 0, QTableWidgetItem(str(c['category_id'])))
            self.table_cats.setItem(i, 1, QTableWidgetItem(str(c['category_name'])))

    def add_category(self):
        name, ok = QInputDialog.getText(self, "Нова категорія", "Введіть назву:")
        if ok and name:
            self.db_manager.add_ill_category(name)
            self.refresh_categories()

    def delete_category(self):
        row = self.table_cats.currentRow()
        if row < 0: return
        cat_id = self.table_cats.item(row, 0).text()
        
        if QMessageBox.question(self, "Увага", "Видалити категорію?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_ill_category(cat_id)
            self.refresh_categories()

    # --- 2. БОЛЕЗНИ ---
    def init_diseases_tab(self):
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Додати Хворобу")
        btn_add.clicked.connect(self.add_disease)
        btn_del = QPushButton("Видалити")
        btn_del.clicked.connect(self.delete_disease)
        btn_add.setStyleSheet(BTN_SUCCESS)     
        btn_del.setStyleSheet(BTN_DANGER) 
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        btn_layout.addStretch()
        
        self.table_diseases = QTableWidget()
        self.table_diseases.setColumnCount(3)
        self.table_diseases.setHorizontalHeaderLabels(["Код (МКХ)", "Назва", "Категорія"])
        self.table_diseases.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_diseases.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_diseases.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.table_diseases)
        self.tab_diseases.setLayout(layout)

    def refresh_diseases(self):
        self.table_diseases.setRowCount(0)
        dis = self.db_manager.get_all_diseases()
        for i, d in enumerate(dis):
            self.table_diseases.insertRow(i)
            self.table_diseases.setItem(i, 0, QTableWidgetItem(str(d['ccode'])))
            self.table_diseases.setItem(i, 1, QTableWidgetItem(str(d['ill_name'])))
            
            cat_name = d['category_name'] if 'category_name' in d.keys() else str(d['category_id'])
            self.table_diseases.setItem(i, 2, QTableWidgetItem(str(cat_name)))

    def add_disease(self):
        if not self.db_manager.get_all_ill_categories():
            QMessageBox.warning(self, "Помилка", "Спочатку додайте хоча б одну категорію!")
            return

        dialog = DiseaseDialog(self.db_manager, self)
        if dialog.exec():
            data = dialog.get_data()
            if data['ccode'] and data['name']:
                # Проверка на дубликат кода
                try:
                    self.db_manager.add_disease(data['ccode'], data['name'], data['category_id'])
                    self.refresh_diseases()
                except Exception as e:
                    QMessageBox.critical(self, "Помилка БД", f"Можливо, такий код вже існує.\n{e}")

    def delete_disease(self):
        row = self.table_diseases.currentRow()
        if row < 0: return
        ccode = self.table_diseases.item(row, 0).text()
        
        if QMessageBox.question(self, "Видалити?", f"Видалити хворобу {ccode}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_disease(ccode)
            self.refresh_diseases()

    # --- 3. РЕГИОНЫ ---
    def init_regions_tab(self):
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Додати Регіон")
        btn_add.clicked.connect(self.add_region)
        btn_del = QPushButton("Видалити")
        btn_del.clicked.connect(self.delete_region)
        btn_add.setStyleSheet(BTN_SUCCESS)     
        btn_del.setStyleSheet(BTN_DANGER) 
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        btn_layout.addStretch()
        
        self.table_regions = QTableWidget()
        self.table_regions.setColumnCount(2)
        self.table_regions.setHorizontalHeaderLabels(["ID", "Назва Регіону"])
        self.table_regions.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_regions.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_regions.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.table_regions)
        self.tab_regions.setLayout(layout)

    def refresh_regions(self):
        self.table_regions.setRowCount(0)
        regions = self.db_manager.get_all_regions()
        for i, r in enumerate(regions):
            self.table_regions.insertRow(i)
            self.table_regions.setItem(i, 0, QTableWidgetItem(str(r['region_id'])))
            self.table_regions.setItem(i, 1, QTableWidgetItem(str(r['region_name'])))

    def add_region(self):
        name, ok = QInputDialog.getText(self, "Новий регіон", "Введіть назву регіону:")
        if ok and name:
            self.db_manager.add_region(name)
            self.refresh_regions()

    def delete_region(self):
        row = self.table_regions.currentRow()
        if row < 0: return
        reg_id = self.table_regions.item(row, 0).text()
        
        reply = QMessageBox.question(self, "Увага", 
            "Видалення регіону видалить і всі райони в ньому!\nПродовжити?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_region(reg_id)
            self.refresh_all_tabs()

    # --- 4. РАЙОНЫ (LOCALS) ---
    def init_locals_tab(self):
        layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Додати Район")
        btn_add.clicked.connect(self.add_local)
        btn_del = QPushButton("Видалити")
        btn_del.clicked.connect(self.delete_local)
        btn_add.setStyleSheet(BTN_SUCCESS)     
        btn_del.setStyleSheet(BTN_DANGER) 
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        btn_layout.addStretch()
        
        self.table_locals = QTableWidget()
        self.table_locals.setColumnCount(3)
        self.table_locals.setHorizontalHeaderLabels(["ID", "Назва Району", "Регіон"])
        self.table_locals.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_locals.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_locals.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.table_locals)
        self.tab_locals.setLayout(layout)

    def refresh_locals(self):
        self.table_locals.setRowCount(0)
        locals_list = self.db_manager.get_all_locals()
        for i, l in enumerate(locals_list):
            self.table_locals.insertRow(i)
            self.table_locals.setItem(i, 0, QTableWidgetItem(str(l['local_id'])))
            self.table_locals.setItem(i, 1, QTableWidgetItem(str(l['local_name'])))
            reg_name = l['region_name'] if 'region_name' in l.keys() else str(l['region_id'])
            self.table_locals.setItem(i, 2, QTableWidgetItem(str(reg_name)))

    def add_local(self):
        if not self.db_manager.get_all_regions():
            QMessageBox.warning(self, "Помилка", "Спочатку створіть хоча б один регіон!")
            return

        dialog = LocalDialog(self.db_manager, self)
        if dialog.exec():
            data = dialog.get_data()
            if data['name'] and data['region_id']:
                self.db_manager.add_local(data['name'], data['region_id'])
                self.refresh_locals()

    def delete_local(self):
        row = self.table_locals.currentRow()
        if row < 0: return
        loc_id = self.table_locals.item(row, 0).text()
        
        if QMessageBox.question(self, "Видалити?", "Видалити цей район?", 
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_local(loc_id)
            self.refresh_locals()