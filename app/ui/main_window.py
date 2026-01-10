from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame, 
    QSpacerItem, QSizePolicy, QMessageBox
)

from app.ui.views.admins import AdminsView
from app.ui.views.clinics import ClinicsView
from app.ui.views.dir import DirectoriesView
from app.ui.views.doctors import DoctorsView
from app.ui.views.illness import IllnessView
from app.ui.views.managers import ManagersView
from app.ui.views.prediction import PredictionView
from app.ui.views.patients import PatientsView
from app.ui.views.profile import ProfileView
from app.ui.views.statistic import StatisticView


class MainWindow(QMainWindow):
    def __init__(self, user, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.user = user
        self.user_role = user['role']

        self.setFixedSize(1400,800)
        self.setWindowTitle("Система прогнозування захворюваності")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Верхняя панель (Header) с информацией и кнопкой выхода
        self.setup_header()

        # 2. Панель навигации (Меню)
        self.setup_navigation()

        # 3. Область контента (StackedWidget)
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

        # Инициализация экранов в зависимости от роли
        self.init_ui()

    def setup_header(self):
        """Создает верхнюю полосу с именем пользователя и кнопкой выхода"""
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #2c3e50; color: white;")
        header_frame.setFixedHeight(50)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)

        # Логотип / Название
        app_title = QLabel("MedStat System")
        app_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Растяжка
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Инфо о пользователе
        user_info = QLabel(f"Користувач: {self.user['full_name']} | Роль: {self.user_role.upper()}")
        user_info.setStyleSheet("font-size: 14px;")

        # Кнопка выхода
        logout_btn = QPushButton("Вийти")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton { background-color: #c0392b; border: none; padding: 5px 15px; border-radius: 3px; color: white; }
            QPushButton:hover { background-color: #e74c3c; }
        """)
        logout_btn.clicked.connect(self.logout)

        header_layout.addWidget(app_title)
        header_layout.addItem(spacer)
        header_layout.addWidget(user_info)
        header_layout.addSpacing(20)
        header_layout.addWidget(logout_btn)

        self.main_layout.addWidget(header_frame)

    def setup_navigation(self):
        """Создает панель меню"""
        self.nav_frame = QFrame()
        self.nav_frame.setStyleSheet("background-color: #ecf0f1; border-bottom: 1px solid #bdc3c7;")
        self.nav_frame.setFixedHeight(60)
        self.nav_layout = QHBoxLayout(self.nav_frame)
        self.nav_layout.setContentsMargins(10, 5, 10, 5)
        self.nav_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.main_layout.addWidget(self.nav_frame)

    def add_nav_button(self, text, index):
        """Добавляет кнопку в меню, которая переключает экран по индексу"""
        btn = QPushButton(text)
        btn.setFixedSize(120, 40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Простой стиль для кнопок
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; border: none; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1abc9c; }
        """)
        btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(index))
        self.nav_layout.addWidget(btn)

    def init_ui(self):
        """Заполняет интерфейс в зависимости от роли пользователя"""
        
        self.profile_view = ProfileView(self.user, self.db_manager) 
        self.statistic_view = StatisticView()
        self.prediction_view = PredictionView()

        if self.user_role == 'admin':
            self.setup_admin_ui()
        elif self.user_role == 'manager':
            self.setup_manager_ui()
        elif self.user_role == 'doctor':
            self.setup_doctor_ui()
        else:
            QMessageBox.critical(self, "Помилка", "Невідома роль користувача!")
            self.close()

    def setup_admin_ui(self):
        """Меню Адміністратора: Довідники, Профіль, Статистика, Прогнозування, Менеджери + (Центр: Клініки)"""
        
        # 0. Центр: Таблица Клінік (Главная страница)
        clinics_view = ClinicsView()
        self.content_stack.addWidget(clinics_view)
        
        # 1. Довідники (Таблицы: Категории, Болезни, Регионы, Районы)
        directories_view = DirectoriesView()
        self.content_stack.addWidget(directories_view)

        # 2. Менеджери
        managers_view = ManagersView(self.db_manager) # Из файла managers.py
        self.content_stack.addWidget(managers_view)

        # 3. Профиль
        self.content_stack.addWidget(self.profile_view)

        # 4. Статистика
        self.content_stack.addWidget(self.statistic_view)

        # 5. Прогнозирование
        self.content_stack.addWidget(self.prediction_view)

        # --- Создаем Кнопки Меню ---
        self.add_nav_button("Клініки (Головна)", 0)
        self.add_nav_button("Довідники", 1)
        self.add_nav_button("Менеджери", 2)
        self.add_nav_button("Профіль", 3)
        self.add_nav_button("Статистика", 4)
        self.add_nav_button("Прогнозування", 5)

    def setup_manager_ui(self):
        """Меню Менеджера: Довідники, Профіль, Статистика, Прогнозування, Лікарі + (Центр: Пацієнти)"""
        
        # 0. Центр: Таблица Пацієнтів
        patients_view = PatientsView()
        self.content_stack.addWidget(patients_view)

        # 1. Довідники (Только Категории и Болезни)
        directories_view = DirectoriesView()
        self.content_stack.addWidget(directories_view)

        # 2. Лікарі
        doctors_view = DoctorsView() # Из файла doctors.py
        self.content_stack.addWidget(doctors_view)

        # 3. Профиль, Статистика, Прогноз
        self.content_stack.addWidget(self.profile_view)
        self.content_stack.addWidget(self.statistic_view)
        self.content_stack.addWidget(self.prediction_view)

        # --- Кнопки ---
        self.add_nav_button("Пацієнти", 0)
        self.add_nav_button("Довідники", 1)
        self.add_nav_button("Лікарі", 2)
        self.add_nav_button("Профіль", 3)
        self.add_nav_button("Статистика", 4)
        self.add_nav_button("Прогноз", 5)

    def setup_doctor_ui(self):
        """Меню Лікаря: Профіль, Статистика, Прогноз, Пацієнти, Адміни + (Центр: Історія Хвороб)"""

        # 0. Центр: Таблица Хвороб (Приемы)
        illness_view = IllnessView()
        self.content_stack.addWidget(illness_view)

        # 1. Пацієнти (Список пацієнтів лікарні)
        patients_view = PatientsView()
        self.content_stack.addWidget(patients_view)

        # 2. Адміністратори (Список админов)
        admins_view = AdminsView()
        self.content_stack.addWidget(admins_view)

        # 3. Профиль, Статистика, Прогноз
        self.content_stack.addWidget(self.profile_view)
        self.content_stack.addWidget(self.statistic_view)
        self.content_stack.addWidget(self.prediction_view)

        # --- Кнопки ---
        self.add_nav_button("Мої Прийоми", 0)
        self.add_nav_button("Пацієнти", 1)
        self.add_nav_button("Профіль", 3) # Индексы смещаются из-за порядка добавления
        self.add_nav_button("Статистика", 4)
        self.add_nav_button("Прогноз", 5)
        self.add_nav_button("Адміністратори", 2)

    def logout(self):
        """Закрывает это окно и открывает логин (реализуется через возврат управления в app.py)"""
        reply = QMessageBox.question(self, 'Вихід', 'Ви впевнені, що хочете вийти?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.close()

            from app.ui.login_window import LoginWindow
            self.login_window = LoginWindow(self.db_manager)
            self.login_window.show()
