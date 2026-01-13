import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLocale 
from app.database.db_manager import DatabaseManager
from app.ui.login_window import LoginWindow

from app.ui.styles import APP_STYLE

DB_PATH = os.path.join('data', 'app_database.db')
SCHEMA_PATH = os.path.join("app", "database", "schema.sql")

def main():
    QLocale.setDefault(QLocale(QLocale.Language.Ukrainian))
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    
    print("Підключення до БД...")
    db_manager = DatabaseManager(DB_PATH)

    if db_manager.execute_script(SCHEMA_PATH):
        print("БД успішно ініціалізована.")
    else:
        print("Помилка ініціалізації БД!")
        sys.exit(1)


    window = LoginWindow(db_manager)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()