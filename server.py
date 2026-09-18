import sqlite3
import random
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DATABASE = 'hostel.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- AUTHENTICATION -----------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE email = ? AND password = ?',
        (email, password)
    ).fetchone()
    conn.close()

    if user:
        return jsonify({
            'success': True,
            'role': user['role'],
            'name': user['name'],
            'email': user['email'],
            'room_no': user['room_no'],
            'course': user['course']
        }), 200
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# ----------------- TRANSACTIONS / PAYMENTS -----------------
@app.route('/api/pay-fees', methods=['POST'])
def pay_fees():
    data = request.get_json() or {}
    email = data.get('email', 'student@smarthostel.edu')
    amount = data.get('amount', 5000)
    mode = data.get('payment_mode', 'UPI Gateway')
    receipt = f"#REC-{random.randint(1000, 9999)}"

    conn = get_db()
    conn.execute(
        'INSERT INTO transactions (receipt_id, student_email, description, amount, payment_mode) VALUES (?, ?, ?, ?, ?)',
        (receipt, email, 'Semester Mess Outstanding Balance', amount, mode)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Payment recorded', 'receipt_id': receipt, 'amount': amount}), 201

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    conn = get_db()
    rows = conn.execute('SELECT * FROM transactions ORDER BY id DESC').fetchall()
    txs = [dict(ix) for ix in rows]
    conn.close()
    return jsonify(txs), 200

# ----------------- ADMIN DASHBOARD STATS & BACKUP -----------------
@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    conn = get_db()
    cursor = conn.cursor()

    # Active (non-resolved) complaints count
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status != 'RESOLVED'")
    active_complaints = cursor.fetchone()[0]

    # Total fee collected from transactions
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE status = 'PAID'")
    total_collected = cursor.fetchone()[0]

    # Pending leave requests
    cursor.execute("SELECT COUNT(*) FROM leave_passes WHERE status = 'PENDING'")
    pending_leaves = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        'active_complaints': active_complaints,
        'total_collected': total_collected,
        'pending_leaves': pending_leaves
    }), 200

@app.route('/api/admin/export-db', methods=['GET'])
def export_db():
    return send_file('hostel.db', as_attachment=True, download_name='hostel_backup.db')

# ----------------- COMPLAINTS (STUDENT & RECTOR) -----------------
@app.route('/api/complaints', methods=['GET', 'POST'])
def handle_complaints():
    conn = get_db()
    if request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('student_name', 'Aliza Fayyaz Khan')
        room = data.get('room_no', 'C-204')
        cat = data.get('category', 'Electrical')
        desc = data.get('description', 'Room maintenance')
        prio = data.get('priority', 'HIGH')

        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO complaints (student_name, room_no, category, description, priority) VALUES (?, ?, ?, ?, ?)',
            (name, room, cat, desc, prio)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'message': 'Complaint lodged', 'id': new_id}), 201

    rows = conn.execute('SELECT * FROM complaints ORDER BY id DESC').fetchall()
    complaints = [dict(ix) for ix in rows]
    conn.close()
    return jsonify(complaints), 200

@app.route('/api/complaints/<int:cid>/resolve', methods=['PUT'])
def resolve_complaint(cid):
    conn = get_db()
    conn.execute('UPDATE complaints SET status = "RESOLVED" WHERE id = ?', (cid,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Ticket marked as resolved'}), 200

# ----------------- LEAVES (STUDENT & RECTOR) -----------------
@app.route('/api/leaves', methods=['GET', 'POST'])
def handle_leaves():
    conn = get_db()
    if request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('student_name', 'Aliza Fayyaz Khan')
        room = data.get('room_no', 'C-204')
        dest = data.get('destination', 'Hometown (Pune)')
        start = data.get('start_date', 'Today')
        end = data.get('end_date', 'Tomorrow')
        contact = data.get('contact', '+91 9876543210')
        reason = data.get('reason', 'Weekend family visit')

        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO leave_passes (student_name, room_no, destination, start_date, end_date, contact, reason) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (name, room, dest, start, end, contact, reason)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'message': 'Leave pass requested', 'id': new_id}), 201

    rows = conn.execute('SELECT * FROM leave_passes ORDER BY id DESC').fetchall()
    leaves = [dict(ix) for ix in rows]
    conn.close()
    return jsonify(leaves), 200

@app.route('/api/leaves/<int:lid>/decision', methods=['PUT'])
def decide_leave(lid):
    data = request.get_json() or {}
    decision = data.get('status', 'APPROVED')
    conn = get_db()
    conn.execute('UPDATE leave_passes SET status = ? WHERE id = ?', (decision, lid))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Leave pass updated to {decision}'}), 200

# ----------------- NOTICES & CIRCULARS -----------------
@app.route('/api/notices', methods=['GET', 'POST'])
def handle_notices():
    conn = get_db()
    if request.method == 'POST':
        data = request.get_json() or {}
        title = data.get('title')
        message = data.get('message')
        target = data.get('target', 'ALL')

        if not title or not message:
            conn.close()
            return jsonify({'error': 'Title and message are required'}), 400

        conn.execute('INSERT INTO notices (title, message, target) VALUES (?, ?, ?)',
                     (title, message, target))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Notice published successfully'}), 201

    rows = conn.execute('SELECT * FROM notices ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows]), 200

# ----------------- MEAL ATTENDANCE -----------------
@app.route('/api/meals/toggle', methods=['POST'])
def toggle_meal():
    data = request.get_json() or {}
    meal_type = data.get('meal_type')
    status = data.get('status')
    student_email = data.get('email', 'student@smarthostel.edu')

    # Terminal output line
    print(f"\n🔔 [MEAL UPDATE] Student: {student_email} | Meal: {meal_type.upper()} | Status: {status}")

    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS meal_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            status TEXT NOT NULL,
            date TEXT DEFAULT (date('now', 'localtime')),
            UNIQUE(student_email, meal_type, date)
        )
    ''')
    conn.execute('''
        INSERT INTO meal_attendance (student_email, meal_type, status)
        VALUES (?, ?, ?)
        ON CONFLICT(student_email, meal_type, date) DO UPDATE SET status=excluded.status
    ''', (student_email, meal_type, status))
    conn.commit()
    conn.close()

    return jsonify({'message': f'{meal_type.title()} marked as {status}'}), 200

# ----------------- ROOMMATE MATCHING -----------------
@app.route('/api/roommate-preferences', methods=['POST'])
def save_roommate_prefs():
    data = request.get_json() or {}
    email = data.get('email', 'student@smarthostel.edu')
    sleep = data.get('sleep', 'Night Owl')
    study = data.get('study', 'Silent Study')
    cleanliness = data.get('cleanliness', 'Moderate')

    print(f"\n🤝 [ROOMMATE PREF] Student: {email} | Sleep: {sleep} | Study: {study} | Cleanliness: {cleanliness}")

    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS roommate_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT UNIQUE NOT NULL,
            sleep_schedule TEXT,
            study_environment TEXT,
            cleanliness_habit TEXT
        )
    ''')
    conn.execute('''
        INSERT INTO roommate_preferences (student_email, sleep_schedule, study_environment, cleanliness_habit)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(student_email) DO UPDATE SET
            sleep_schedule=excluded.sleep_schedule,
            study_environment=excluded.study_environment,
            cleanliness_habit=excluded.cleanliness_habit
    ''', (email, sleep, study, cleanliness))
    conn.commit()
    conn.close()

    # Dynamic peer match simulation
    return jsonify({
        'status': 'success',
        'message': 'Preferences saved successfully!',
        'matched_peer': 'Priya Joshi',
        'peer_room': 'Block C (C-205)',
        'peer_course': 'B.Sc Information Tech',
        'compatibility_score': '94%'
    }), 200
if __name__ == '__main__':
    print("Smart Hostel Backend Server running on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)