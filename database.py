import sqlite3

DATABASE = 'hostel.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        room_no TEXT,
        course TEXT
    )
    ''')

    # 2. Transactions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_id TEXT NOT NULL,
        student_email TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_mode TEXT NOT NULL,
        status TEXT DEFAULT 'PAID',
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 3. Complaints Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        room_no TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        priority TEXT DEFAULT 'MEDIUM',
        status TEXT DEFAULT 'OPEN',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 4. Leave Passes Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leave_passes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        room_no TEXT NOT NULL,
        destination TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        contact TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 5. Notices Table (Moved outside of the users block)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        target TEXT DEFAULT 'ALL',
        date_posted TEXT DEFAULT (datetime('now', 'localtime'))
    )
    ''')

    # Seed Users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO users (name, email, password, role, room_no, course)
        VALUES 
        ('Aliza Fayyaz Khan', 'student@smarthostel.edu', 'password123', 'student', 'C-204', 'B.Com (Computer Applications)'),
        ('Chief Rector', 'rector@smarthostel.edu', 'rector123', 'rector', 'Admin-01', 'Hostel Administration'),
        ('Hostel Owner / Admin', 'admin@smarthostel.edu', 'admin123', 'owner', 'HQ-101', 'Operations Head')
        ''')

    # Seed Notices
    cursor.execute("SELECT COUNT(*) FROM notices")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO notices (title, message, target)
        VALUES ('Semester Mess Audit Notification', 'Mess inspection scheduled for all dining halls this Friday.', 'ALL')
        ''')

    conn.commit()
    conn.close()
    print("Database tables created successfully!")

# Execute the function immediately
init_db()