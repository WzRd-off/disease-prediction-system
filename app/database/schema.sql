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
    password_hash TEXT NOT NULL,                 -- passwd
    full_name TEXT NOT NULL,                     -- ПІБ (FIO)
    clinic_id INTEGER,                           -- clinic (FK). Nullable для Гол. Адміна
    phone TEXT,                                  -- Phone
    role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'doctor')), -- Role
    FOREIGN KEY(clinic_id) REFERENCES clinics(clinic_id)
);

[cite_start]-- 7. Таблиця Пацієнтів (Pacient) [cite: 105]
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
INSERT OR IGNORE INTO users (login, password_hash, full_name, role, clinic_id) 
VALUES ('admin@system.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Main Administrator', 'admin', NULL);