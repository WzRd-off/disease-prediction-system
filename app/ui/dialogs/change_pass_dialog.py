from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox

class ChangePasswordDialog(QDialog):
    def __init__(self, db_manager, user_id, auth_service, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.auth_service = auth_service
        
        self.setWindowTitle("Зміна пароля")
        self.setFixedSize(300, 250)
        
        layout = QVBoxLayout()
        
        self.inp_old = QLineEdit()
        self.inp_old.setPlaceholderText("Поточний пароль")
        self.inp_old.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.inp_new = QLineEdit()
        self.inp_new.setPlaceholderText("Новий пароль")
        self.inp_new.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.inp_confirm = QLineEdit()
        self.inp_confirm.setPlaceholderText("Підтвердження пароля")
        self.inp_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_save = QPushButton("Змінити")
        btn_save.clicked.connect(self.save_password)
        
        layout.addWidget(QLabel("Введіть дані:"))
        layout.addWidget(self.inp_old)
        layout.addWidget(self.inp_new)
        layout.addWidget(self.inp_confirm)
        layout.addWidget(btn_save)
        
        self.setLayout(layout)

    def save_password(self):
        old_pass = self.inp_old.text()
        new_pass = self.inp_new.text()
        confirm_pass = self.inp_confirm.text()
        
        # 1. Проверяем старый пароль
        if not self.db_manager.check_password(self.user_id, old_pass):
            QMessageBox.warning(self, "Помилка", "Невірний поточний пароль.")
            return
            
        # 2. Проверяем совпадение новых
        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Помилка", "Нові паролі не співпадають.")
            return
            
        if len(new_pass) < 4:
            QMessageBox.warning(self, "Помилка", "Пароль надто короткий.")
            return

        # 3. Сохраняем
        self.db_manager.change_password(self.user_id, new_pass)
        
        QMessageBox.information(self, "Успіх", "Пароль успішно змінено.")
        self.accept()