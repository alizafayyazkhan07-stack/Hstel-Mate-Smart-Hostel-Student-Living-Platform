import sqlite3

conn = sqlite3.connect('hostel.db')
cursor = conn.cursor()

# Ensure users table exists
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

# Insert or update default credentials
users_data = [
    ('Aliza Khan', '', 'admin123', 'owner', None, None),
    ('Dr. Suresh Kulkarni', 'rector@smarthostel.edu', 'rector123', 'rector', None, None),
    ('Aliza Fayyaz Khan', 'student@smarthostel.edu', 'password123', 'student', 'C-204', 'B.Com (Computer Applications)')
]

for user in users_data:
    cursor.execute('''
        INSERT INTO users (name, email, password, role, room_no, course)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            password=excluded.password,
            role=excluded.role,
            name=excluded.name
    ''', user)

conn.commit()
print("Default users verified and updated successfully in hostel.db!")

# Print current rows to confirm
cursor.execute("SELECT id, name, email, password, role FROM users")
for row in cursor.fetchall():
    print(row)

conn.close()