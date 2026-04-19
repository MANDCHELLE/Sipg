from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)

# --- CONFIGURACIÓN CRUCIAL ---
app.secret_key = os.getenv('SECRET_KEY', 'clave_muy_segura_123') # Necesario para sesiones
app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', '123456789')
app.config['MYSQL_DB'] = os.getenv('DB_NAME', 'bdprueba')
app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT', 3306))
# Esta línea permite usar ficha['id'] en lugar de ficha[0]
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 

mysql = MySQL(app)

# ==========================================
# SEGURIDAD (DECORADOR)
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Por favor, inicie sesión primero.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# RUTAS DE ACCESO (LOGIN / LOGOUT)
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password_candidate):
            session['logged_in'] = True
            session['username'] = username
            flash('Bienvenido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Acceso denegado.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/create_user', methods=['POST'])
@login_required
def create_user():
    if session.get('username') != 'admin':
        return redirect(url_for('index'))


    username = request.form['username']
    password = request.form['password']
    hashed_pw = generate_password_hash(password)
    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, hashed_pw))
        mysql.connection.commit()
        flash(f'Usuario {username} creado.', 'success')
    except:
        flash('Error: El usuario ya existe.', 'danger')
    finally:
        cur.close()
    return redirect(url_for('index'))


@app.route('/delete_user/<int:id>')
def delete_user(id):
    if session.get('username') != 'admin':
        return redirect(url_for('index'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM usuarios WHERE id=%s', (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))
# ==========================================
# RUTAS PROTEGIDAS (Añadir @login_required)
# ==========================================


#ruta para mostrar la pagina de inicio
@app.route('/')
@login_required
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuarios')
    data = cur.fetchall()
    cur.close()
    return render_template('index_copy.html', dato=data)



#----------FICHAS-------------

#ruta para mostrar la tabla de fichas
@app.route('/table' , methods=['GET']) 
def table():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM fichas')
    data = cur.fetchall()
    cur.close()
    return render_template('table.html', fichas=data)

#ruta para agregar una ficha
@app.route('/add_ficha', methods=['POST', 'GET'])
def add_ficha():
    if request.method == 'POST':
        id_estudiante = request.form['id_estudiante']
        grado = request.form['grado']
        tecnica = request.form['tecnica']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']

        cur = mysql.connection.cursor()
        cur.execute('''
            INSERT INTO fichas (id_estudiante,grado,tecnica,descripcion,fecha)
            VALUES (%s, %s, %s, %s, %s)''', 
            (id_estudiante, grado, tecnica, descripcion, fecha)
        )
        
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index')) 
    else:
        return render_template('form.html')
    


#ruta para editar una ficha
@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit_ficha(id):
    if request.method == 'POST':
        id_estudiante = request.form['id_estudiante']
        grado = request.form['grado']
        tecnica = request.form['tecnica']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']

        cur = mysql.connection.cursor()
        cur.execute('UPDATE fichas SET id_estudiante=%s, grado=%s, tecnica=%s, descripcion=%s, fecha=%s WHERE id=%s', (id_estudiante, grado, tecnica, descripcion, fecha, id, ))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))
    else: 
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM fichas WHERE id=%s', (id,))
        data = cur.fetchone()
        cur.close()

        return render_template('edit.html', ficha=data)
    


#ruta para eliminar una ficha
@app.route('/delete/<int:id>')
def delete_ficha(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM fichas WHERE id=%s', (id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('table'))


# ------------ CITAS--------

@app.route('/cita' , methods=['GET'])
def cita():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM citas')
    data = cur.fetchall()
    cur.close()
    return render_template('citas.html', citas=data)

#ruta para agregar una cita
@app.route('/add_cita', methods=['POST', 'GET'])
def add_cita():
    if request.method == 'POST':
        id_estudiante = request.form['id_estudiante']
        citado= request.form['citado']
        contacto = request.form['contacto']
        nombre_psicologo = request.form['nombre_psicologo'] 
        fecha = request.form['fecha']
        hora = request.form['hora']
        motivo = request.form['motivo']
        grado = request.form['grado']
        tecnica = request.form['tecnica']

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO citas (id_estudiante,citado,contacto,nombre_psicologo,fecha,hora,motivo,grado,tecnica) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (id_estudiante, citado, contacto, nombre_psicologo, fecha, hora, motivo, grado, tecnica))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index')) 
    else:
        return render_template('citas_form.html')
    


#ruta para editar una cita
@app.route('/edit_cita/<int:id>', methods=['POST', 'GET'])
def edit_cita(id):
    if request.method == 'POST':
        id_estudiante = request.form['id_estudiante']
        citado= request.form['citado']
        contacto = request.form['contacto']
        nombre_psicologo = request.form['nombre_psicologo'] 
        fecha = request.form['fecha']
        hora = request.form['hora']
        motivo = request.form['motivo']
        grado = request.form['grado']
        tecnica = request.form['tecnica']

        cur = mysql.connection.cursor()
        cur.execute('UPDATE citas SET id_estudiante=%s, citado=%s, contacto=%s, nombre_psicologo=%s, fecha=%s, hora=%s, motivo=%s, grado=%s, tecnica=%s WHERE id=%s', (id_estudiante, citado, contacto, nombre_psicologo, fecha, hora, motivo, grado, tecnica, id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('cita'))
    else: 
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM citas WHERE id=%s', (id,))
        data = cur.fetchone()
        cur.close()

        return render_template('edit_citas.html', cita=data)
    


#ruta para eliminar una cita
@app.route('/delete_cita/<int:id>')
def delete_cita(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM citas WHERE id=%s', (id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('cita'))



#----------------- ESTUDIANTES-----------



# ==========================================
# INICIO DE LA APP Y CREACIÓN DE ADMIN
# ==========================================
if __name__ == '__main__':
    # Crear usuario admin automáticamente si no existe al arrancar
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE username = %s", ('admin',))
            if not cur.fetchone():
                hashed_pw = generate_password_hash('admin123')
                cur.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", ('admin', hashed_pw))
                mysql.connection.commit()
            cur.close()
        except Exception as e:
            print(f"Error inicializando DB: {e}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)