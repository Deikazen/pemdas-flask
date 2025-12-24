from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# --- KONEKSI DATABASE ---


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Biar bisa akses data pakai nama kolom
    return conn

# --- BUAT TABEL OTOMATIS (JIKA BELUM ADA) ---


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Jalankan pembuatan tabel saat aplikasi start
init_db()

# --- ROUTES (JALUR URL) ---

# 1. READ (Tampil Data)


@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', users=users)

# 2. CREATE (Tambah Data)


@app.route('/add', methods=['POST'])
def add_user():
    nama = request.form['nama']
    role = request.form['role']

    conn = get_db_connection()
    conn.execute('INSERT INTO users (nama, role) VALUES (?, ?)', (nama, role))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# 3. EDIT (Tampil Form Edit & Update Process)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    conn = get_db_connection()

    if request.method == 'POST':
        # Proses Update
        nama = request.form['nama']
        role = request.form['role']
        conn.execute(
            'UPDATE users SET nama = ?, role = ? WHERE id = ?', (nama, role, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # Ambil data lama untuk ditampilkan di form
    user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit.html', user=user)

# 4. DELETE (Hapus Data)


@app.route('/delete/<int:id>')
def delete_user(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
