from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QCheckBox, 
    QScrollArea, QFrame, QLabel
)
from PyQt6.QtCore import Qt
from app.ui.styles import SEARCH_INPUT_STYLE, CHECKBOX_STYLE

class DiseaseSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.checkboxes = [] # Список активних чекбоксів
        self.init_ui()

    def init_ui(self):
        # Основний лейаут
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # 1. Поле пошуку
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук хвороби...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet(SEARCH_INPUT_STYLE)
        self.search_input.textChanged.connect(self.filter_items)
        
        layout.addWidget(self.search_input)

        # 2. Область прокрутки
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        # Трохи стилю для скролу, щоб виглядав як контейнер
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid #bdc3c7; border-radius: 5px; background: white; }")

        # Контейнер для чекбоксів
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: white;")
        self.items_layout = QVBoxLayout(self.scroll_content)
        self.items_layout.setContentsMargins(10, 10, 10, 10)
        self.items_layout.setSpacing(5)
        self.items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

    def update_items(self, diseases):
        """
        Оновлює список хвороб.
        diseases: список словників [{'ill_name': '...', 'ccode': '...'}, ...]
        """
        # Очищаємо старі чекбокси
        self.checkboxes = []
        # Видаляємо віджети з лейауту
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Додаємо нові
        for d in diseases:
            name = d['ill_name']
            code = d['ccode']
            
            cb = QCheckBox()
            # Форматування тексту (як у прикладі)
            cb.setText(f"{name} ({code})")
            cb.setStyleSheet(CHECKBOX_STYLE)
            
            # Зберігаємо дані в об'єкті
            cb.setProperty("ill_name", name.lower())
            cb.setProperty("ccode", code) # Важливо для пошуку
            cb.setProperty("code_val", code) # Важливо для отримання результату
            
            self.items_layout.addWidget(cb)
            self.checkboxes.append(cb)

    def filter_items(self, text):
        """Фільтрує чекбокси за введеним текстом"""
        search_text = text.lower().strip()
        
        for cb in self.checkboxes:
            name = cb.property("ill_name")
            code = cb.property("ccode").lower()
            
            # Шукаємо і в назві, і в коді
            if not search_text or search_text in name or search_text in code:
                cb.setVisible(True)
            else:
                cb.setVisible(False)

    def get_selected_codes(self):
        """Повертає список кодів (ccode) обраних хвороб"""
        selected = []
        for cb in self.checkboxes:
            if cb.isChecked():
                selected.append(cb.property("code_val"))
        return selected