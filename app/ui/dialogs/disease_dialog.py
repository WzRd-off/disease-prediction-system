from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QDialog, 
    QComboBox, QDialogButtonBox, QLineEdit
)

class DiseaseDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати хворобу")
        self.setFixedSize(350, 200)
        
        layout = QVBoxLayout()
        
        # Код МКХ
        layout.addWidget(QLabel("Код МКХ (напр. J10):"))
        self.inp_code = QLineEdit()
        layout.addWidget(self.inp_code)

        # Назва
        layout.addWidget(QLabel("Назва хвороби:"))
        self.inp_name = QLineEdit()
        layout.addWidget(self.inp_name)
        
        # Категорія
        layout.addWidget(QLabel("Категорія:"))
        self.combo_cat = QComboBox()
        cats = db_manager.get_all_ill_categories()
        for c in cats:
            self.combo_cat.addItem(f"{c['category_name']}", c['category_id'])
            
        layout.addWidget(self.combo_cat)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        return {
            'ccode': self.inp_code.text().strip(),
            'name': self.inp_name.text().strip(),
            'category_id': self.combo_cat.currentData()
        }
