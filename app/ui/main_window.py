from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame, 
    QSpacerItem, QSizePolicy, QMessageBox
)

from app.ui.views.profile import ProfileView
from app.ui.views.statistic import StatisticView
from app.ui.views.prediction import PredictionView
from app.ui.views.managers import ManagersView
from app.ui.views.doctors import DoctorsView
from app.ui.views.clinics import ClinicsView
from app.ui.views.dir import DirectoriesView
from app.ui.views.patients import PatientsView
from app.ui.views.admins import AdminsView
from app.ui.views.illness import IllnessView
from app.ui.styles import SIDEBAR_STYLE, BTN_DANGER

class MainWindow(QMainWindow):
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.user_role = user['role']

        self.setWindowTitle("Система прогнозування захворюваності")
        self.setMinimumSize(1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_header()
        self.setup_navigation()

        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

        self.init_role_based_ui()

    def setup_header(self):
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #2c3e50; color: white;")
        header_frame.setFixedHeight(50)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)

        app_title = QLabel("MedStat System")
        app_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        user_info = QLabel(f"Користувач: {self.user['full_name']} | Роль: {self.user_role.upper()}")
        user_info.setStyleSheet("font-size: 14px;")

        logout_btn = QPushButton("Вийти")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(BTN_DANGER)
        logout_btn.clicked.connect(self.logout)

        header_layout.addWidget(app_title)
        header_layout.addItem(spacer)
        header_layout.addWidget(user_info)
        header_layout.addSpacing(20)
        header_layout.addWidget(logout_btn)

        self.main_layout.addWidget(header_frame)

    def setup_navigation(self):
        self.nav_frame = QFrame()
        self.nav_frame.setStyleSheet(SIDEBAR_STYLE)
        self.nav_frame.setFixedHeight(60)
        self.nav_layout = QHBoxLayout(self.nav_frame)
        self.nav_layout.setContentsMargins(10, 5, 10, 5)
        self.nav_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.main_layout.addWidget(self.nav_frame)

    def add_nav_button(self, text, index):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; border: none; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1abc9c; }
        """)
        btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(index))
        self.nav_layout.addWidget(btn)

    def init_role_based_ui(self):
        # Oбщие views

        self.profile_view = ProfileView(self.user, self.db_manager) 
        self.statistic_view = StatisticView(self.user, self.db_manager)
        self.prediction_view = PredictionView(self.db_manager)
        self.directories_view = DirectoriesView(self.db_manager)


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
        # 0. Clinics (Главная)
        clinics_view = ClinicsView(self.db_manager) 
        self.content_stack.addWidget(clinics_view)
        
        # 1. Directories
        self.content_stack.addWidget(self.directories_view)

        # 2. Managers
        managers_view = ManagersView(self.db_manager)
        self.content_stack.addWidget(managers_view)

        # 3. Profile
        self.content_stack.addWidget(self.profile_view)

        # 4. Statistic
        self.content_stack.addWidget(self.statistic_view)

        # 5. Prediction
        self.content_stack.addWidget(self.prediction_view)

        self.add_nav_button("Клініки", 0)
        self.add_nav_button("Довідники", 1)
        self.add_nav_button("Менеджери", 2)
        self.add_nav_button("Профіль", 3)
        self.add_nav_button("Статистика", 4)
        self.add_nav_button("Прогноз", 5)

    def setup_manager_ui(self):
        patients_view = PatientsView(self.user, self.db_manager)
        self.content_stack.addWidget(patients_view)

        self.content_stack.addWidget(self.directories_view)

        doctors_view = DoctorsView(self.user, self.db_manager)
        self.content_stack.addWidget(doctors_view)

        self.content_stack.addWidget(self.profile_view)
        self.content_stack.addWidget(self.statistic_view)
        self.content_stack.addWidget(self.prediction_view)

        self.add_nav_button("Пацієнти", 0)
        self.add_nav_button("Довідники", 1)
        self.add_nav_button("Лікарі", 2)
        self.add_nav_button("Профіль", 3)
        self.add_nav_button("Статистика", 4)
        self.add_nav_button("Прогноз", 5)

    def setup_doctor_ui(self):
        illness_view = IllnessView(self.user, self.db_manager)
        self.content_stack.addWidget(illness_view)

        patients_view = PatientsView(self.user, self.db_manager)
        self.content_stack.addWidget(patients_view)

        admins_view = AdminsView(self.db_manager)
        self.content_stack.addWidget(admins_view)

        self.content_stack.addWidget(self.profile_view)
        self.content_stack.addWidget(self.statistic_view)
        self.content_stack.addWidget(self.prediction_view)

        self.add_nav_button("Прийоми", 0)
        self.add_nav_button("Пацієнти", 1)
        self.add_nav_button("Адміністратори", 2)
        self.add_nav_button("Профіль", 3)
        self.add_nav_button("Статистика", 4)
        self.add_nav_button("Прогноз", 5)

    def logout(self):
        reply = QMessageBox.question(self, 'Вихід', 'Ви впевнені, що хочете вийти?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            from app.ui.login_window import LoginWindow
            self.login_window = LoginWindow(self.db_manager)
            self.login_window.show()