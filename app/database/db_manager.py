import sqlite3
import os

class DatabaseManager():
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self._ensure_db_folder_exists()
    

    def connect(self):
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                self.connection.execute("PRAGMA foreign_keys = ON;")
            except sqlite3.Error as e:
                print(f"CRITICAL ERROR: Помилка підключення до БД: {e}")

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: tuple = (), fetch_one=False, fetch_all=False):
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.connection.commit()
                return cursor.lastrowid
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f'Error: {e}')
            return None

    # --- DISEASES & HISTORY (ХВОРОБИ ТА ІСТОРІЯ) ---

    def execute_script(self, script_path: str):
        self.connect()
        if not os.path.exists(script_path):
            return False
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            self.connection.executescript(sql_script)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            return False

    def get_all_ill_categories(self):
        return self.execute_query("SELECT * FROM ill_categories", fetch_all=True)
    
    def add_ill_category(self, name):
        return self.execute_query("INSERT INTO ill_categories (category_name) VALUES (?)", (name,))

    def delete_ill_category(self, cat_id):
        return self.execute_query("DELETE FROM ill_categories WHERE category_id=?", (cat_id,))


    def get_all_diseases(self):
        # Підтягуємо назву категорії
        query = """
            SELECT d.*, c.category_name 
            FROM diseases d
            LEFT JOIN ill_categories c ON d.category_id = c.category_id
            ORDER BY d.ill_name
        """
        return self.execute_query(query, fetch_all=True)

    def add_disease(self, ccode, ill_name, category_id):
        return self.execute_query("INSERT INTO diseases (ccode, ill_name, category_id) VALUES (?, ?, ?)", (ccode, ill_name, category_id))

    def delete_disease(self, ccode):
        return self.execute_query("DELETE FROM diseases WHERE ccode=?", (ccode,))

    def get_ill_history_by_doctor_clinic(self, clinic_id):
        # Отримуємо історію хвороб для пацієнтів клініки лікаря
        # Зв'язок: ill_history -> patients -> doctor -> clinic
        query = """
            SELECT h.*, p.full_name as patient_name, d.ill_name, l.local_name, r.region_name
            FROM ill_history h
            JOIN patients p ON h.patient_code = p.rnkop_code
            JOIN users u ON p.doctor_id = u.user_id
            LEFT JOIN diseases d ON h.ill_code = d.ccode
            LEFT JOIN locals l ON h.local_id = l.local_id
            LEFT JOIN regions r ON l.region_id = r.region_id
            WHERE u.clinic_id = ?
            ORDER BY h.visit_date DESC
        """
        return self.execute_query(query, (clinic_id,), fetch_all=True)

    def add_ill_history(self, patient_code, local_id, ill_code, is_chronic, visit_date, status, prescription):
        query = """
            INSERT INTO ill_history (patient_code, local_id, ill_code, is_chronic, visit_date, status, prescription)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (patient_code, local_id, ill_code, is_chronic, visit_date, status, prescription))

    def update_ill_history(self, history_id, patient_code, local_id, ill_code, is_chronic, visit_date, status, prescription):
        query = """
            UPDATE ill_history
            SET patient_code=?, local_id=?, ill_code=?, is_chronic=?, visit_date=?, status=?, prescription=?
            WHERE history_id=?
        """
        return self.execute_query(query, (patient_code, local_id, ill_code, is_chronic, visit_date, status, prescription, history_id))
    
    def delete_ill_history(self, history_id):
        return self.execute_query("DELETE FROM ill_history WHERE history_id=?", (history_id,))

    # --- USERS (ADMINS & MANAGERS & DOCTORS) ---
    def get_users_by_role_and_clinic(self, role, clinic_id):
        return self.execute_query("SELECT * FROM users WHERE role=? AND clinic_id=?", (role, clinic_id), fetch_all=True)

    def get_all_managers(self):
        return self.execute_query("SELECT * FROM users WHERE role='manager' ORDER BY user_id ASC", fetch_all=True)
    
    def get_all_admins(self):
        return self.execute_query("SELECT * FROM users WHERE role='admin' ORDER BY user_id ASC", fetch_all=True)

    def add_user(self, login, password, full_name, clinic_id, phone, role):
        query = "INSERT INTO users (login, password, full_name, clinic_id, phone, role) VALUES (?, ?, ?, ?, ?, ?)"
        return self.execute_query(query, (login, password, full_name, clinic_id, phone, role))

    def update_user(self, user_id, login, password, full_name, clinic_id, phone):
        query = "UPDATE users SET login=?, password=?, full_name=?, clinic_id=?, phone=? WHERE user_id=?"
        return self.execute_query(query, (login, password, full_name, clinic_id, phone, user_id))

    def delete_user(self, user_id):
        return self.execute_query("DELETE FROM users WHERE user_id=?", (user_id,))

    # Сохраняем старые методы для совместимости
    add_manager = lambda self, l, p, f, c, ph: self.add_user(l, p, f, c, ph, 'manager')
    update_manager = update_user
    delete_manager = delete_user

    # --- PATIENTS (ПАЦІЄНТИ) ---
    def get_patients_by_clinic(self, clinic_id):
        query = """
            SELECT p.*, u.full_name as doctor_name 
            FROM patients p
            LEFT JOIN users u ON p.doctor_id = u.user_id
            WHERE u.clinic_id = ?
        """
        return self.execute_query(query, (clinic_id,), fetch_all=True)
    
    def get_all_patients_extended(self):
        query = """
            SELECT p.*, u.full_name as doctor_name, c.clinic_name
            FROM patients p
            LEFT JOIN users u ON p.doctor_id = u.user_id
            LEFT JOIN clinics c ON u.clinic_id = c.clinic_id
        """
        return self.execute_query(query, fetch_all=True)

    # ОБНОВЛЕННЫЙ МЕТОД: Добавлен status
    def add_patient(self, rnkop, full_name, birth_date, address, phone, doctor_id, comments, status):
        query = "INSERT INTO patients (rnkop_code, full_name, birth_date, address, phone, doctor_id, comments, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        return self.execute_query(query, (rnkop, full_name, birth_date, address, phone, doctor_id, comments, status))

    # ОБНОВЛЕННЫЙ МЕТОД: Добавлен status
    def update_patient(self, rnkop, full_name, birth_date, address, phone, doctor_id, comments, status):
        query = """
            UPDATE patients 
            SET full_name=?, birth_date=?, address=?, phone=?, doctor_id=?, comments=?, status=? 
            WHERE rnkop_code=?
        """
        return self.execute_query(query, (full_name, birth_date, address, phone, doctor_id, comments, status, rnkop))
    
    def update_patient_comment_only(self, rnkop, comments):
        return self.execute_query("UPDATE patients SET comments=? WHERE rnkop_code=?", (comments, rnkop))

    def delete_patient(self, rnkop):
        return self.execute_query("DELETE FROM patients WHERE rnkop_code=?", (rnkop,))

    # --- REGIONS / LOCALS / CLINICS ---
    def get_all_regions(self):
        return self.execute_query("SELECT * FROM regions ORDER BY region_id ASC", fetch_all=True)
    def add_region(self, name):
        return self.execute_query("INSERT INTO regions (region_name) VALUES (?)", (name,))
    def delete_region(self, region_id):
        return self.execute_query("DELETE FROM regions WHERE region_id=?", (region_id,))

    def get_all_locals(self):
        query = "SELECT l.*, r.region_name FROM locals l LEFT JOIN regions r ON l.region_id = r.region_id ORDER BY l.local_id ASC"
        return self.execute_query(query, fetch_all=True)
    def add_local(self, name, region_id):
        return self.execute_query("INSERT INTO locals (local_name, region_id) VALUES (?, ?)", (name, region_id))
    def delete_local(self, local_id):
        return self.execute_query("DELETE FROM locals WHERE local_id=?", (local_id,))

    def get_all_clinics(self):
        return self.execute_query("SELECT * FROM clinics WHERE is_archived = 0 ORDER BY clinic_id ASC", fetch_all=True)
    def add_clinic(self, name, local_id, address, email, phone):
        return self.execute_query("INSERT INTO clinics (clinic_name, local_id, address, email, phone) VALUES (?, ?, ?, ?, ?)", (name, local_id, address, email, phone))
    def update_clinic(self, clinic_id, name, local_id, address, email, phone):
        return self.execute_query("UPDATE clinics SET clinic_name=?, local_id=?, address=?, email=?, phone=? WHERE clinic_id=?", (name, local_id, address, email, phone, clinic_id))
    def delete_clinic(self, clinic_id):
        return self.execute_query("DELETE FROM clinics WHERE clinic_id=?", (clinic_id,))

    # --- PROFILE ---
    def update_user_profile(self, user_id, full_name, phone):
        return self.execute_query("UPDATE users SET full_name=?, phone=? WHERE user_id=?", (full_name, phone, user_id))
    def check_password(self, user_id, password):
        res = self.execute_query("SELECT user_id FROM users WHERE user_id=? AND password=?", (user_id, password), fetch_one=True)
        return res is not None
    def change_password(self, user_id, new_pass):
        return self.execute_query("UPDATE users SET password=? WHERE user_id=?", (new_pass, user_id))

    def _ensure_db_folder_exists(self):
        folder = os.path.dirname(self.db_path)
        if folder and not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except OSError as e:
                print(f"ERROR: Не Вдалося створити папку {folder}: {e}")