from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QDialog, 
    QComboBox, QDialogButtonBox, QLineEdit
)

class LocalDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати район")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Назва району:"))
        self.line_name = QLineEdit()
        layout.addWidget(self.line_name)
        
        layout.addWidget(QLabel("Оберіть регіон:"))
        self.combo_regions = QComboBox()
        regions = db_manager.get_all_regions()
        for r in regions:
            self.combo_regions.addItem(f"{r['region_name']} (ID: {r['region_id']})", r['region_id'])
            
        layout.addWidget(self.combo_regions)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        return {
            'name': self.line_name.text(),
            'region_id': self.combo_regions.currentData()
        }
