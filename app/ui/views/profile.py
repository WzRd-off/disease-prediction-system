from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame,
    QHBoxLayout, QMessageBox)

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
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        # Контейнер для формы (белая карточка)
        card = QFrame()
        card.setFixedWidth(500)
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
        self.inp_fullname.setMaxLength(100)
        form_layout.addWidget(self.inp_fullname)

        #Клиника
        form_layout.addWidget(QLabel("Клініка:"))
        self.inp_clinic_id = QLineEdit(str(self.user['clinic_id']))
        self.inp_clinic_id.setReadOnly(True)
        form_layout.addWidget(self.inp_clinic_id)

        # Телефон
        form_layout.addWidget(QLabel("Телефон:"))
        self.inp_phone = QLineEdit(self.user['phone'])
        self.inp_phone.setMaxLength(13) # Ограничение: Макс 13 символов
        self.inp_phone.setPlaceholderText("+380...")
        # Ограничение: Только цифры и плюс
        self.inp_phone.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\+?[0-9]*$")))
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
       
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

    def save_changes(self):
        if not self.inp_fullname.text().strip():
            QMessageBox.warning(self, "Помилка", "ПІБ не може бути порожнім")
            return
        if len(self.inp_phone.text().strip()) < 10:
            QMessageBox.warning(self, "Помилка", "Телефон занадто короткий")
            return

        # ИСПРАВЛЕНО: Передаем .text(), а не сами объекты QLineEdit
        self.db_manager.update_user_profile(
            self.user['user_id'], 
            self.inp_fullname.text(),  # Был self.inp_fullname
            self.inp_phone.text()      # Был self.inp_phone
        )

    def open_password_dialog(self):
        dialog = ChangePasswordDialog(self.db_manager, self.user['user_id'], self.auth_service, self)
        dialog.exec()