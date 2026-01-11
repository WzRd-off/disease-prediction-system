from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QHBoxLayout

from app.ui.dialogs.change_pass_dialog import ChangePasswordDialog
from app.logic.auth_service import AuthService

class ProfileView(QWidget):
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.auth_service = AuthService(self.db_manager)
        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout()
        
        header = QLabel("Профіль користувача")
        layout.addWidget(header)

        # Контейнер для формы (белая карточка)
        card = QFrame()
        form_layout = QVBoxLayout(card)

        # Роль (Read-only)
        role = self.user['role']
        self.lbl_role = QLabel(f"Роль у системі: {role}")
        form_layout.addWidget(self.lbl_role)

        # Логин (Read-only)
        form_layout.addWidget(QLabel("Логін:"))
        self.inp_username = QLineEdit(self.user['login'])
        self.inp_username.setReadOnly(True)
        form_layout.addWidget(self.inp_username)

        # ФИО
        form_layout.addWidget(QLabel("ПІБ:"))
        self.inp_fullname = QLineEdit(self.user['full_name'])
        form_layout.addWidget(self.inp_fullname)

        #Клиника
        form_layout.addWidget(QLabel("Клініка:"))
        self.inp_clinic_id = QLineEdit(str(self.user['clinic_id']))
        self.inp_clinic_id.setReadOnly(True)
        form_layout.addWidget(self.inp_clinic_id)

        # Телефон
        form_layout.addWidget(QLabel("Телефон:"))
        self.inp_phone = QLineEdit(self.user['phone'])
        form_layout.addWidget(self.inp_phone)

        # Кнопки действий
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("Зберегти зміни")
        self.btn_save.clicked.connect(self.save_changes)
        
        self.btn_pass = QPushButton("Змінити пароль")
        self.btn_pass.clicked.connect(self.open_password_dialog)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_pass)
        btn_layout.addStretch()
        
        form_layout.addLayout(btn_layout)
        
        layout.addWidget(card)
        layout.addStretch()
        
        self.setLayout(layout)

    def save_changes(self):
        full_name = self.inp_fullname
        phone = self.inp_phone
        self.db.update_user_profile(self.user['id'], full_name, phone)

    def open_password_dialog(self):
        dialog = ChangePasswordDialog(self.db_manager, self.user['user_id'], self.auth_service, self)
        dialog.exec()