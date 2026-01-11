# Цветовая палитра
COLORS = {
    'primary': '#2980b9',       # Синий
    'secondary': '#2c3e50',     # Темно-синий (фон меню)
    'accent': '#1abc9c',        # Бирюзовый
    'success': '#27ae60',       # Зеленый
    'danger': '#c0392b',        # Красный
    'warning': '#f39c12',       # Оранжевый
    'background': '#ecf0f1',    # Светло-серый фон
    'card_bg': '#ffffff',       # Белый фон карточек
    'text': '#2c3e50',          # Темно-серый текст
    'text_light': '#ecf0f1',    # Светлый текст (на темном фоне)
    'border': '#bdc3c7'         # Серые границы
}

# Основной стиль приложения (QSS)
APP_STYLE = f"""
    /* Глобальные настройки */
    QWidget {{
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: 14px;
        color: {COLORS['text']};
    }}

    /* Главное окно */
    QMainWindow {{
        background-color: {COLORS['background']};
    }}

    /* Поля ввода (QLineEdit, QDateEdit, QComboBox) */
    QLineEdit, QDateEdit, QComboBox, QTextEdit {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 5px;
        padding: 8px; /* Больше воздуха */
        selection-background-color: {COLORS['primary']};
    }}
    QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QTextEdit:focus {{
        border: 2px solid {COLORS['primary']};
    }}

    /* Выпадающий список */
    QComboBox::drop-down {{
        border: 0px;
        width: 20px;
    }}
    
    /* Кнопки (QPushButton) */
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 8px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #3498db; /* Светлее */
    }}
    QPushButton:pressed {{
        background-color: #1a5276; /* Темнее */
    }}
    
    /* Таблицы (QTableWidget) */
    QTableWidget {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        gridline-color: #ecf0f1;
        selection-background-color: #d6eaf8; /* Очень светло-голубой */
        selection-color: {COLORS['text']};
        alternate-background-color: #f8f9f9; /* Чередование строк */
    }}
    QHeaderView::section {{
        background-color: {COLORS['secondary']};
        color: white;
        padding: 8px;
        border: none;
        font-weight: bold;
    }}

    /* Табы (QTabWidget) */
    QTabWidget::pane {{
        border: 1px solid {COLORS['border']};
        background: {COLORS['card_bg']};
    }}
    QTabBar::tab {{
        background: #bdc3c7;
        padding: 10px 20px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {COLORS['card_bg']};
        border-bottom: 2px solid {COLORS['primary']};
        font-weight: bold;
    }}

    /* Группы (QGroupBox) */
    QGroupBox {{
        border: 1px solid {COLORS['border']};
        border-radius: 5px;
        margin-top: 20px; /* Отступ для заголовка */
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
        color: {COLORS['secondary']};
    }}
    
    /* Прокрутка (QScrollBar) */
    QScrollBar:vertical {{
        background: #f1f1f1;
        width: 12px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #bdc3c7;
        min-height: 20px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #a6acaf;
    }}
"""

# Специфические стили для кнопок (можно применять через setStyleSheet)
BTN_SUCCESS = f"""
    QPushButton {{
        background-color: {COLORS['success']};
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
    }}
    QPushButton:hover {{ background-color: #2ecc71; }}
"""

BTN_DANGER = f"""
    QPushButton {{
        background-color: {COLORS['danger']};
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
    }}
    QPushButton:hover {{ background-color: #e74c3c; }}
"""

BTN_SECONDARY = f"""
    QPushButton {{
        background-color: #95a5a6;
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
    }}
    QPushButton:hover {{ background-color: #7f8c8d; }}
"""

# Стиль для Сайдбара (Боковой панели)
SIDEBAR_STYLE = f"""
    QFrame {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text_light']};
        border: none;
    }}
    QLabel {{
        color: {COLORS['text_light']};
    }}
    QPushButton {{
        background-color: transparent;
        color: {COLORS['text_light']};
        text-align: left;
        padding: 15px 20px;
        border: none;
        border-left: 4px solid transparent;
        border-radius: 0px;
        font-size: 15px;
    }}
    QPushButton:hover {{
        background-color: #34495e;
        border-left: 4px solid {COLORS['accent']};
    }}
    QPushButton:checked {{
        background-color: #34495e;
        border-left: 4px solid {COLORS['primary']};
        font-weight: bold;
    }}
"""