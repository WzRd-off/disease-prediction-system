PRAGMA foreign_keys = ON;

-- 1. Таблиця Регіонів (Regions)
CREATE TABLE IF NOT EXISTS regions (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Id_region
    region_name TEXT NOT NULL UNIQUE             -- region
);

-- 2. Таблиця Районів/Локалей (Locals)
CREATE TABLE IF NOT EXISTS locals (
    local_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Id_local
    local_name TEXT NOT NULL,                    -- local
    region_id INTEGER NOT NULL,                  -- Id_region (FK)
    FOREIGN KEY(region_id) REFERENCES regions(region_id) ON DELETE CASCADE
);

-- 3. Таблиця Клінік (Clinics)
CREATE TABLE IF NOT EXISTS clinics (
    clinic_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Id_clinic
    clinic_name TEXT NOT NULL,                   -- name
    local_id INTEGER,                            -- Id_local (FK)
    address TEXT,                                -- address_clinic
    email TEXT,                                  -- E-mail_clinic
    phone TEXT,                                  -- tel_clinic
    is_archived BOOLEAN DEFAULT 0,               -- Поле для логіки архівації
    FOREIGN KEY(local_id) REFERENCES locals(local_id)
);

-- 4. Таблиця Категорій хвороб (ill_Category)
CREATE TABLE IF NOT EXISTS ill_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT, -- CategoryId
    category_name TEXT NOT NULL UNIQUE             -- CategoryName
);

-- 5. Таблиця Хвороб (ill)
CREATE TABLE IF NOT EXISTS diseases (
    ccode TEXT PRIMARY KEY,                        -- CCode (Код МКХ може бути з літерами, тому TEXT)
    ill_name TEXT NOT NULL UNIQUE,                 -- ill_Name
    category_id INTEGER NOT NULL,                  -- CategoryId (FK)
    FOREIGN KEY(category_id) REFERENCES ill_categories(category_id)
);

-- 6. Таблиця Користувачів (User)
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- UserId
    login TEXT NOT NULL UNIQUE,                  -- Login (email)
    password TEXT NOT NULL,                 -- passwd
    full_name TEXT NOT NULL,                     -- ПІБ (FIO)
    clinic_id INTEGER,                           -- clinic (FK). Nullable для Гол. Адміна
    phone TEXT,                                  -- Phone
    role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'doctor')), -- Role
    FOREIGN KEY(clinic_id) REFERENCES clinics(clinic_id)
);

-- 7. Таблиця Пацієнтів (Pacient)
CREATE TABLE IF NOT EXISTS patients (
    rnkop_code TEXT PRIMARY KEY,                 -- РНКОПП (Код пацієнта - унікальний ключ)
    full_name TEXT NOT NULL,                     -- ПІБ (FIO)
    birth_date DATE NOT NULL,                    -- BirthDate
    address TEXT,                                -- HomeAddres
    phone TEXT,                                  -- Phone
    doctor_id INTEGER,                           -- Licar (FK на користувача-лікаря)
    comments TEXT,                               -- Comment
    status TEXT DEFAULT 'healthy' CHECK(status IN ('healthy', 'sick', 'chronic', 'dead')), -- Stan_p
    FOREIGN KEY(doctor_id) REFERENCES users(user_id)
);

-- 8. Таблиця Історії хвороб (ill_Story)
CREATE TABLE IF NOT EXISTS ill_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT, -- ID_History
    patient_code TEXT NOT NULL,                   -- RNKOP (FK)
    local_id INTEGER,                             -- Id_local (де захворів/звернувся)
    ill_code TEXT NOT NULL,                       -- illId (FK на CCode хвороби)
    is_chronic BOOLEAN DEFAULT 0,                 -- Xronic
    visit_date DATE NOT NULL,                     -- DataZvern
    status TEXT NOT NULL,                         -- Stan (хворіє, одужав, помер)
    prescription TEXT,                            -- Nazn (призначення)
    FOREIGN KEY(patient_code) REFERENCES patients(rnkop_code),
    FOREIGN KEY(local_id) REFERENCES locals(local_id),
    FOREIGN KEY(ill_code) REFERENCES diseases(ccode)
);

-- Додаємо дефолтного головного адміністратора
-- Пароль (в реальності має бути хешований): admin

INSERT OR IGNORE INTO users (login, password, full_name, role, clinic_id) 
VALUES ('admin', 'admin', 'Main Administrator', 'admin', NULL);

-- ... (тут ваші команди CREATE TABLE) ...

-- === ТЕСТОВІ ДАНІ ДЛЯ ПРОГНОЗУВАННЯ (Зима 2025) ===

-- 1. Створюємо базові довідники
INSERT OR IGNORE INTO regions (region_id, region_name) VALUES (1, 'Київська');
INSERT OR IGNORE INTO locals (local_id, local_name, region_id) VALUES (1, 'Шевченківський', 1);
INSERT OR IGNORE INTO ill_categories (category_id, category_name) VALUES (1, 'Інфекційні');
INSERT OR IGNORE INTO diseases (ccode, ill_name, category_id) VALUES ('J10', 'Грип', 1), ('J00', 'ГРВІ', 1);

-- 1.1. Створюємо Клініку (ВАЖЛИВО: Лікар має належати до клініки)
INSERT OR IGNORE INTO clinics (clinic_id, clinic_name, local_id, address, email, phone, is_archived) 
VALUES (1, 'Тестова Клініка "Здоров''я"', 1, 'м. Київ, вул. Тестова, 1', 'test@clinic.com', '044-000-00-00', 0);

-- 2. Створюємо лікаря і привязуємо до клініки ID=1
INSERT OR IGNORE INTO users (login, password, full_name, role, phone, clinic_id) 
VALUES ('test_doc', '12345', 'Тестовий Лікар', 'doctor', '000', 1);

-- 3. Додаємо 20 пацієнтів (привязані до test_doc)
INSERT OR IGNORE INTO patients (rnkop_code, full_name, birth_date, address, phone, doctor_id, status) VALUES 
('3000000001', 'Пацієнт Тест 1', '1990-01-01', 'Київ', '001', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000002', 'Пацієнт Тест 2', '1991-02-02', 'Київ', '002', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000003', 'Пацієнт Тест 3', '1992-03-03', 'Київ', '003', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000004', 'Пацієнт Тест 4', '1993-04-04', 'Київ', '004', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000005', 'Пацієнт Тест 5', '1994-05-05', 'Київ', '005', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000006', 'Пацієнт Тест 6', '1980-06-06', 'Київ', '006', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000007', 'Пацієнт Тест 7', '1981-07-07', 'Київ', '007', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000008', 'Пацієнт Тест 8', '1982-08-08', 'Київ', '008', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000009', 'Пацієнт Тест 9', '1983-09-09', 'Київ', '009', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000010', 'Пацієнт Тест 10', '1984-10-10', 'Київ', '010', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000011', 'Пацієнт Тест 11', '1985-11-11', 'Київ', '011', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000012', 'Пацієнт Тест 12', '1986-12-12', 'Київ', '012', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000013', 'Пацієнт Тест 13', '1987-01-13', 'Київ', '013', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000014', 'Пацієнт Тест 14', '1988-02-14', 'Київ', '014', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000015', 'Пацієнт Тест 15', '1989-03-15', 'Київ', '015', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000016', 'Пацієнт Тест 16', '2000-04-16', 'Київ', '016', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000017', 'Пацієнт Тест 17', '2001-05-17', 'Київ', '017', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000018', 'Пацієнт Тест 18', '2002-06-18', 'Київ', '018', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000019', 'Пацієнт Тест 19', '2003-07-19', 'Київ', '019', (SELECT user_id FROM users WHERE login='test_doc'), 'sick'),
('3000000020', 'Пацієнт Тест 20', '2004-08-20', 'Київ', '020', (SELECT user_id FROM users WHERE login='test_doc'), 'sick');

-- 4. Додаємо історію хвороб (Розподіляємо дати з 16.01 по 16.02)
INSERT OR IGNORE INTO ill_history (patient_code, local_id, ill_code, is_chronic, visit_date, status, prescription) VALUES
('3000000001', 1, 'J10', 0, '2025-01-16', 'хворіє', 'Тест'),
('3000000002', 1, 'J10', 0, '2025-01-17', 'хворіє', 'Тест'),
('3000000003', 1, 'J00', 0, '2025-01-18', 'хворіє', 'Тест'),
('3000000004', 1, 'J10', 0, '2025-01-19', 'хворіє', 'Тест'),
('3000000005', 1, 'J10', 0, '2025-01-20', 'хворіє', 'Тест'),
('3000000006', 1, 'J00', 0, '2025-01-22', 'хворіє', 'Тест'),
('3000000007', 1, 'J10', 0, '2025-01-24', 'хворіє', 'Тест'),
('3000000008', 1, 'J10', 0, '2025-01-25', 'хворіє', 'Тест'),
('3000000009', 1, 'J00', 0, '2025-01-26', 'хворіє', 'Тест'),
('3000000010', 1, 'J10', 0, '2025-01-28', 'хворіє', 'Тест'),
('3000000011', 1, 'J10', 0, '2025-01-30', 'хворіє', 'Тест'),
('3000000012', 1, 'J00', 0, '2025-02-01', 'хворіє', 'Тест'),
('3000000013', 1, 'J10', 0, '2025-02-02', 'хворіє', 'Тест'),
('3000000014', 1, 'J10', 0, '2025-02-04', 'хворіє', 'Тест'),
('3000000015', 1, 'J00', 0, '2025-02-06', 'хворіє', 'Тест'),
('3000000016', 1, 'J10', 0, '2025-02-08', 'хворіє', 'Тест'),
('3000000017', 1, 'J10', 0, '2025-02-10', 'хворіє', 'Тест'),
('3000000018', 1, 'J00', 0, '2025-02-12', 'хворіє', 'Тест'),
('3000000019', 1, 'J10', 0, '2025-02-14', 'хворіє', 'Тест'),
('3000000020', 1, 'J10', 0, '2025-02-16', 'хворіє', 'Тест');