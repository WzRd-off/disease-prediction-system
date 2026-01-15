from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QHeaderView, QTableWidgetItem,
    QComboBox, QDateEdit, QPushButton, QGroupBox
)
import pyqtgraph as pg
from app.ui.styles import BTN_SUCCESS
from app.ui.widgets.disease_selector import DiseaseSelector 

class StatisticView(QWidget):
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.role = self.user['role']
        self.clinic_id = self.user['clinic_id']

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 1. ПАНЕЛЬ ФІЛЬТРІВ (Зверху)
        filter_group = QGroupBox("Фільтри")
        filter_layout = QHBoxLayout()

        # БЛОК 1: Дата
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Від:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.date_from)
        
        date_layout.addWidget(QLabel("До:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_to)
        filter_layout.addLayout(date_layout)

        # БЛОК 2: Локація (для адміна)
        if self.role == 'admin':
            loc_layout = QVBoxLayout()
            loc_layout.addWidget(QLabel("Регіон:"))
            self.combo_region = QComboBox()
            self.combo_region.addItem("Всі", None)
            self._load_regions()
            self.combo_region.currentIndexChanged.connect(self._on_region_changed)
            loc_layout.addWidget(self.combo_region)

            loc_layout.addWidget(QLabel("Район:"))
            self.combo_local = QComboBox()
            self.combo_local.addItem("Всі", None)
            loc_layout.addWidget(self.combo_local)
            filter_layout.addLayout(loc_layout)

        # БЛОК 3: Категорія
        cat_layout = QVBoxLayout()
        cat_layout.addWidget(QLabel("Категорія:"))
        self.combo_category = QComboBox()
        self.combo_category.addItem("Всі", None)
        self._load_categories()
        self.combo_category.currentIndexChanged.connect(self._on_category_changed)
        cat_layout.addWidget(self.combo_category)
        # Додамо розтяжку, щоб кнопки не прилипали
        cat_layout.addStretch() 
        filter_layout.addLayout(cat_layout)

        # БЛОК 4: Хвороби (НОВИЙ ВІДЖЕТ)
        disease_layout = QVBoxLayout()
        disease_layout.addWidget(QLabel("Хвороби:"))
        
        # Використовуємо наш новий селектор
        self.disease_selector = DiseaseSelector()
        self.disease_selector.setMinimumWidth(250) # Трохи ширше для зручності
        self.disease_selector.setMaximumHeight(150) # Обмежимо висоту, щоб не розтягувало вікно
        self._load_diseases() # Завантаження початкових даних
        
        disease_layout.addWidget(self.disease_selector)
        filter_layout.addLayout(disease_layout)

        # Кнопка Оновити
        btn_layout = QVBoxLayout()
        self.btn_refresh = QPushButton("Показати")
        self.btn_refresh.setStyleSheet(BTN_SUCCESS)
        self.btn_refresh.clicked.connect(self.refresh_stats)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        filter_layout.addLayout(btn_layout)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)

        # 2. ЦЕНТРАЛЬНА ЧАСТИНА
        content_layout = QHBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Група", "Кількість"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        content_layout.addWidget(self.table, stretch=1)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("Статистика", color="k", size="12pt")
        self.plot_widget.setLabel('left', 'Кількість')
        self.plot_widget.setLabel('bottom', 'Категорії / Хвороби')
        content_layout.addWidget(self.plot_widget, stretch=2)

        main_layout.addLayout(content_layout)

        # 3. НИЖНЯ ПАНЕЛЬ
        self.lbl_total = QLabel("Всього записів: 0")
        self.lbl_total.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(self.lbl_total)

        self.setLayout(main_layout)

    # --- МЕТОДИ ЗАВАНТАЖЕННЯ ---
    def _load_regions(self):
        regions = self.db_manager.get_all_regions()
        for r in regions:
            self.combo_region.addItem(r['region_name'], r['region_id'])

    def _on_region_changed(self):
        self.combo_local.clear()
        self.combo_local.addItem("Всі", None)
        region_id = self.combo_region.currentData()
        if region_id:
            locals_list = self.db_manager.get_locals_by_region(region_id)
            for l in locals_list:
                self.combo_local.addItem(l['local_name'], l['local_id'])

    def _load_categories(self):
        cats = self.db_manager.get_all_ill_categories()
        for c in cats:
            self.combo_category.addItem(c['category_name'], c['category_id'])

    def _on_category_changed(self):
        # При зміні категорії оновлюємо список у нашому новому віджеті
        category_id = self.combo_category.currentData()
        
        if category_id:
            diseases = self.db_manager.get_diseases_by_category(category_id)
        else:
            diseases = self.db_manager.get_all_diseases()
            
        # Викликаємо метод оновлення у віджета
        self.disease_selector.update_items(diseases)

    def _load_diseases(self):
        self._on_category_changed()

    # --- ЛОГІКА ---
    def refresh_stats(self):
        d_from = self.date_from.date().toString("yyyy-MM-dd")
        d_to = self.date_to.date().toString("yyyy-MM-dd")
        cat_id = self.combo_category.currentData()
        category_ids = [cat_id] if cat_id else None
        
        # ОТРИМУЄМО ДАНІ З НОВОГО ВІДЖЕТА
        disease_codes = self.disease_selector.get_selected_codes()
        if not disease_codes:
            disease_codes = None # Якщо нічого не обрано, значить "Всі" з відображених

        if self.role == 'admin':
            reg_id = self.combo_region.currentData()
            loc_id = self.combo_local.currentData()
            stats_data = self.db_manager.get_statistics_admin(d_from, d_to, reg_id, loc_id, category_ids, disease_codes)
            graph_data = self.db_manager.get_top_diseases_admin(d_from, d_to)
        else:
            stats_data = self.db_manager.get_statistics_clinic(self.clinic_id, d_from, d_to, category_ids, disease_codes)
            graph_data = self.db_manager.get_top_categories_clinic(self.clinic_id, d_from, d_to)

        # Оновлення таблиці
        self.table.setRowCount(0)
        total_count = 0
        for i, row in enumerate(stats_data):
            self.table.insertRow(i)
            if self.role == 'admin':
                label = f"{row['category_name']} ({row['region_name']})"
            else:
                label = row['category_name']
            self.table.setItem(i, 0, QTableWidgetItem(label))
            self.table.setItem(i, 1, QTableWidgetItem(str(row['count'])))
            total_count += row['count']
        self.lbl_total.setText(f"Всього за обраний період: {total_count}")

        # Оновлення графіка
        self.plot_widget.clear()
        if graph_data:
            counts = [row['count'] for row in graph_data]
            labels = [row['label'] for row in graph_data]
            x = range(len(counts))
            bar_item = pg.BarGraphItem(x=x, height=counts, width=0.6, brush='#3498db')
            self.plot_widget.addItem(bar_item)
            ax = self.plot_widget.getAxis('bottom')
            ax.setTicks([list(zip(x, labels))])