from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QHeaderView, QTableWidgetItem,
    QComboBox, QDateEdit, QPushButton, QGroupBox,
    QSpinBox, QMessageBox
)
import pyqtgraph as pg
from app.ui.styles import BTN_SUCCESS
from app.ui.widgets.disease_selector import DiseaseSelector
from datetime import datetime, timedelta

class PredictionView(QWidget):
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        # Роль больше не сохраняем и не используем для логики отображения
        
        self.init_ui()

    def set_user_context(self, user):
        """Встановлюємо користувача (метод залишено для сумісності)"""
        self.user = user
        # Логіку приховування елементів за роллю видалено

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 1. ПАНЕЛЬ НАЛАШТУВАНЬ ПРОГНОЗУ (Зверху)
        filter_group = QGroupBox("Параметри Прогнозування")
        filter_layout = QHBoxLayout()

        # --- БЛОК 1: Локація ---
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
        
        # Видалено блок if self.role != 'admin', тепер фільтри доступні всім
            
        filter_layout.addLayout(loc_layout)

        # --- БЛОК 2: Період Прогнозу ---
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Дата початку (Сьогодні):"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate())
        self.date_from.setReadOnly(True)
        self.date_from.setEnabled(False)
        date_layout.addWidget(self.date_from)
        
        date_layout.addWidget(QLabel("Прогноз ДО дати:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate().addMonths(1))
        self.date_to.setMinimumDate(QDate.currentDate().addDays(1))
        date_layout.addWidget(self.date_to)
        filter_layout.addLayout(date_layout)

        # --- БЛОК 3: Хвороби ---
        cat_layout = QVBoxLayout()
        cat_layout.addWidget(QLabel("Категорія:"))
        self.combo_category = QComboBox()
        self.combo_category.addItem("Всі", None)
        self._load_categories()
        self.combo_category.currentIndexChanged.connect(self._on_category_changed)
        cat_layout.addWidget(self.combo_category)
        filter_layout.addLayout(cat_layout)

        disease_layout = QVBoxLayout()
        disease_layout.addWidget(QLabel("Хвороби (мульти):"))
        self.list_diseases = DiseaseSelector() # Використовуємо кастомний віджет
        self.list_diseases.setMinimumWidth(250)
        self.list_diseases.setMaximumHeight(150)
        self._load_diseases()
        disease_layout.addWidget(self.list_diseases)
        filter_layout.addLayout(disease_layout)
        
        # Кнопка Розрахувати
        self.btn_calculate = QPushButton("Розрахувати")
        self.btn_calculate.setStyleSheet(BTN_SUCCESS)
        self.btn_calculate.clicked.connect(self.calculate_prediction)
        
        btn_layout = QVBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_calculate)
        filter_layout.addLayout(btn_layout)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)

        # 2. ЦЕНТРАЛЬНА ЧАСТИНА (Графік + Таблиця)
        content_layout = QHBoxLayout()
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("Графік Прогнозу", color="k", size="12pt")
        self.plot_widget.setLabel('left', 'Кількість хворих')
        self.plot_widget.setLabel('bottom', 'Період (Час)')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.addLegend()
        content_layout.addWidget(self.plot_widget, stretch=2)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Дата", "Прогноз"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        content_layout.addWidget(self.table, stretch=1)

        main_layout.addLayout(content_layout)

        # 3. НИЖНЯ ПАНЕЛЬ
        self.lbl_summary = QLabel("Оберіть хвороби та дату закінчення прогнозу, потім натисніть 'Розрахувати'.")
        self.lbl_summary.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px; color: #7f8c8d;")
        main_layout.addWidget(self.lbl_summary)

        self.setLayout(main_layout)

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
        category_id = self.combo_category.currentData()
        
        if category_id:
            diseases = self.db_manager.get_diseases_by_category(category_id)
        else:
            diseases = self.db_manager.get_all_diseases()
            
        self.list_diseases.update_items(diseases)

    def _load_diseases(self):
        self._on_category_changed()

    def calculate_prediction(self):
        # 1. Збираємо вхідні дані
        disease_codes = self.list_diseases.get_selected_codes()
        
        if not disease_codes:
            QMessageBox.warning(self, "Увага", "Оберіть хоча б одну хворобу!")
            return

        # Розрахунок періоду
        start_qdate = self.date_from.date()
        end_qdate = self.date_to.date().toPyDate() # --- ИСПРАВЛЕНИЕ: Конвертация в Python date ---
        
        # Для расчета дней используем start_qdate (QDate), так как daysTo работает с QDate
        days_diff = start_qdate.daysTo(self.date_to.date()) 
        if days_diff <= 0:
            QMessageBox.warning(self, "Помилка", "Дата закінчення має бути пізніше сьогоднішньої!")
            return
            
        forecast_period_weeks = (days_diff + 6) // 7 
        history_weeks = 52 # Вы просили 52

        today = datetime.now().date()
        start_history_date = today - timedelta(weeks=history_weeks + 2) 
        
        placeholders = ','.join('?' * len(disease_codes))
        query = f"""
            SELECT h.visit_date, COUNT(h.history_id) as count
            FROM ill_history h
            JOIN diseases d ON h.ill_code = d.ccode
            WHERE h.visit_date >= ? AND d.ccode IN ({placeholders})
        """
        params = [start_history_date] + disease_codes
        
        # --- ФІЛЬТРАЦІЯ ЛОКАЦІЇ (УНІВЕРСАЛЬНА, БЕЗ РОЛЕЙ) ---
        reg_id = self.combo_region.currentData()
        loc_id = self.combo_local.currentData()
        
        if loc_id:
            # Якщо обрано район - фільтруємо по ньому
            query += " AND h.local_id = ?"
            params.append(loc_id)
        elif reg_id:
            # Якщо район не обрано, але обрано регіон - фільтруємо по регіону
            query += " AND h.local_id IN (SELECT local_id FROM locals WHERE region_id = ?)"
            params.append(reg_id)
        # Якщо нічого не обрано - беремо ВСІ дані по базі

        query += " GROUP BY h.visit_date ORDER BY h.visit_date ASC"
        
        raw_data = self.db_manager.execute_query(query, tuple(params), fetch_all=True)
        
        if not raw_data:
            self.lbl_summary.setText("Недостатньо історичних даних для прогнозу.")
            self.plot_widget.clear()
            self.table.setRowCount(0)
            return

        # 3. Обробка даних (Групування по тижнях)
        data_by_week = {}
        for row in raw_data:
            date_str = row['visit_date']
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            week_start = date_obj - timedelta(days=date_obj.weekday())
            
            if week_start not in data_by_week:
                data_by_week[week_start] = 0
            data_by_week[week_start] += row['count']

        sorted_history = sorted(data_by_week.items())
        
        if len(sorted_history) < 2:
            self.lbl_summary.setText("Замало даних (потрібно мінімум 2 тижні історії).")
            return

        # Если данных меньше чем history_weeks, берем все что есть
        slice_len = min(len(sorted_history), history_weeks)
        history_slice = sorted_history[-slice_len:] 
        
        dates = [x[0] for x in history_slice]
        counts = [x[1] for x in history_slice]
        
        # 4. Математичний розрахунок
        coeffs = []
        for i in range(1, len(counts)):
            prev = counts[i-1]
            curr = counts[i]
            if prev == 0: prev = 1
            coeffs.append(curr / prev)
            
        if not coeffs: coeffs = [1.0]

        x0 = sum(coeffs) / len(coeffs)
        
        weights = list(range(1, len(coeffs) + 1))
        weighted_sum = sum(x * w for x, w in zip(coeffs, weights))
        total_weight = sum(weights)
            
        k_b = weighted_sum / total_weight
        final_k = (x0 + k_b) / 2
        
        # 5. Генерація прогнозу
        last_value = counts[-1]
        
        forecast_dates = []
        forecast_values = []
        
        current_val = last_value
        current_date = dates[-1]
        
        for _ in range(forecast_period_weeks):
            current_val = current_val * final_k
            current_date = current_date + timedelta(weeks=1)
            
            # Теперь сравнение работает корректно (python date и python date)
            if current_date > end_qdate + timedelta(days=6):
                break

            forecast_dates.append(current_date)
            forecast_values.append(int(current_val))

        # 6. Візуалізація
        self.plot_widget.clear()
        self.plot_widget.addLegend()

        x_hist = range(len(counts))
        ticks = []
        for i, d in enumerate(dates):
            ticks.append((i, d.strftime("%d.%m")))
            
        self.plot_widget.plot(x_hist, counts, pen=pg.mkPen('b', width=2), symbol='o', name="Історія")
        
        x_fore = range(len(counts) - 1, len(counts) + len(forecast_values))
        y_fore = [counts[-1]] + forecast_values
        
        self.plot_widget.plot(x_fore, y_fore, pen=pg.mkPen('r', width=2, style=Qt.PenStyle.DashLine), symbol='x', name="Прогноз")

        for i, d in enumerate(forecast_dates):
            ticks.append((len(counts) + i, d.strftime("%d.%m")))

        ax = self.plot_widget.getAxis('bottom')
        ax.setTicks([ticks])

        self.table.setRowCount(0)
        for i, (d, v) in enumerate(zip(forecast_dates, forecast_values)):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(d.strftime("%Y-%m-%d")))
            self.table.setItem(i, 1, QTableWidgetItem(str(v)))

        trend_text = "Зростання" if final_k > 1 else "Спад"
        percent = abs(final_k - 1) * 100
        days_total = (forecast_dates[-1] - dates[-1]).days if forecast_dates else 0
        self.lbl_summary.setText(f"Прогноз на {days_total} днів. Тренд: {trend_text} на {percent:.1f}% щотижня.")