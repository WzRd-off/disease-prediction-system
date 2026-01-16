from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QDialogButtonBox, QMessageBox
)

class ChangePasswordDialog(QDialog):
    def __init__(self, db_manager, user_id, auth_service, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.auth_service = auth_service
        
        self.setWindowTitle("Зміна пароля")
        self.setFixedSize(300, 250)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Старий пароль:"))
        self.inp_old = QLineEdit()
        self.inp_old.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_old.setMaxLength(50) # Ограничение: Макс 50 символов
        layout.addWidget(self.inp_old)
        
        layout.addWidget(QLabel("Новий пароль:"))
        self.inp_new = QLineEdit()
        self.inp_new.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_new.setMaxLength(50) # Ограничение: Макс 50 символов
        layout.addWidget(self.inp_new)
        
        layout.addWidget(QLabel("Підтвердження:"))
        self.inp_confirm = QLineEdit()
        self.inp_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_confirm.setMaxLength(50) # Ограничение: Макс 50 символов
        layout.addWidget(self.inp_confirm)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def validate_and_accept(self):
        # Защита от дурака
        old_pass = self.inp_old.text()
        new_pass = self.inp_new.text()
        confirm_pass = self.inp_confirm.text()
        
        if len(new_pass) < 4:
            QMessageBox.warning(self, "Помилка", "Новий пароль занадто короткий (мінімум 4 символи)")
            return
            
        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Помилка", "Нові паролі не співпадають")
            return
            
        if not self.db_manager.check_password(self.user_id, old_pass):
             QMessageBox.warning(self, "Помилка", "Старий пароль невірний")
             return

        self.db_manager.change_password(self.user_id, new_pass)
        QMessageBox.information(self, "Успіх", "Пароль успішно змінено!")
        self.accept()