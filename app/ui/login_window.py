from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from app.ui.main_window import MainWindow
from app.logic.auth_service import AuthService

class LoginWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        self.auth_service = AuthService(self.db_manager)

        self.setWindowTitle("Login")
        self.setFixedSize(300, 350)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user = self.auth_service.authenticate(username, password)

        if user:
            print(f"Вхід успішний: {user['login']} (Role: {user['role']})")
            
            self.close()
            
            self.main_window = MainWindow(user, self.db_manager)
            self.main_window.show()
        else:
            QMessageBox.warning(self, "Login Failed", "Невірне им'я користувача або пароль.")
