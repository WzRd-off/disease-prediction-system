from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, 
    QMessageBox, QDialogButtonBox, QComboBox
)

class DiseaseDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
        self.setWindowTitle("Додати хворобу")
        self.setFixedSize(350, 200)
        
        layout = QVBoxLayout()
        
        # Код МКХ
        layout.addWidget(QLabel("Код МКХ (напр. J10):"))
        self.inp_code = QLineEdit()
        self.inp_code.setMaxLength(6) # Ограничение: Макс 6 символов
        # Ограничение: Только английские буквы и цифры
        self.inp_code.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[A-Za-z0-9\.]+$")))
        layout.addWidget(self.inp_code)

        # Назва
        layout.addWidget(QLabel("Назва хвороби:"))
        self.inp_name = QLineEdit()
        self.inp_name.setMaxLength(100) # Ограничение: Макс 100 символов
        layout.addWidget(self.inp_name)
        
        # Категорія
        layout.addWidget(QLabel("Категорія:"))
        self.combo_cat = QComboBox()
        self._load_cats()
        layout.addWidget(self.combo_cat)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _load_cats(self):
        cats = self.db_manager.get_all_ill_categories()
        for c in cats:
            self.combo_cat.addItem(f"{c['category_name']}", c['category_id'])

    def validate_and_accept(self):
        # Защита от дурака
        if len(self.inp_code.text().strip()) < 2:
            QMessageBox.warning(self, "Помилка", "Код занадто короткий")
            return
        if not self.inp_name.text().strip():
            QMessageBox.warning(self, "Помилка", "Назва не може бути порожньою")
            return
        if self.combo_cat.currentIndex() == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть категорію")
            return
        self.accept()

    def get_data(self):
        return {
            'ccode': self.inp_code.text().strip(),
            'name': self.inp_name.text().strip(),
            'category_id': self.combo_cat.currentData()
        }