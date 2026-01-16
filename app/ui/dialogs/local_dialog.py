from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, 
    QMessageBox, QDialogButtonBox, QComboBox
)

class LocalDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати район")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Назва району:"))
        self.line_name = QLineEdit()
        self.line_name.setMaxLength(50) # Ограничение: Макс 50 символов
        layout.addWidget(self.line_name)
        
        layout.addWidget(QLabel("Оберіть регіон:"))
        self.combo_regions = QComboBox()
        regions = db_manager.get_all_regions()
        for r in regions:
            self.combo_regions.addItem(f"{r['region_name']} (ID: {r['region_id']})", r['region_id'])
            
        layout.addWidget(self.combo_regions)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def validate_and_accept(self):
        if not self.line_name.text().strip():
            QMessageBox.warning(self, "Помилка", "Назва не може бути порожньою")
            return
        if self.combo_regions.currentIndex() == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть регіон")
            return
        self.accept()

    def get_data(self):
        return {
            'name': self.line_name.text(),
            'region_id': self.combo_regions.currentData()
        }