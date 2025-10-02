from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import joblib

app = Flask(__name__)
app.secret_key = '1a2efef47399d56260165cae68e08c0d'  # Change this to a secure key

# ✅ Database Connection Function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='65651',  # Replace with your MySQL password
            database='expense_tracker'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None  # Return None if DB connection fails

@app.route('/')
def landing_page():  # ✅ Renamed from home() to landing_page()
    return render_template('register.html')  # Landing page is the Register Page



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        username = request.form.get('username')
        email = request.form.get('email')
        mobile_number = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        # ✅ Check for empty fields
        if not all([first_name, last_name, username, email, mobile_number, password, confirm_password]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))

        # ✅ Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        # ✅ Hash the password
        password_hash = generate_password_hash(password)

        # ✅ Establish DB connection
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed!", "danger")
            return redirect(url_for('register'))

        cursor = conn.cursor()
        try:
            # ✅ Check if username or email already exists
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()
            if existing_user:
                flash('Username or Email already exists! Try logging in.', 'danger')
                return redirect(url_for('register'))

            # ✅ Insert user data into the `users` table
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, second_name, mobile_number)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, email, password_hash, first_name, last_name, mobile_number))

            # ✅ Create user-specific expenses table
            expenses_table = f"expenses_{username}"
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {expenses_table} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    description VARCHAR(255) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

            # ✅ Fetch user ID after successful insert
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]  # ✅ Save user ID in session

            flash('Registration successful! Redirecting to Home.', 'success')
            return redirect(url_for('user_home'))  # ✅ Redirect to home page

        except mysql.connector.Error as err:
            print(f"Database Error: {err}")  # ✅ Debugging
            flash(f'Database Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed!", "danger")
            return redirect(url_for('login'))

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, username))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            flash('Login successful! Redirecting to Home.', 'success')
            return redirect(url_for('user_home'))  # ✅ Redirect to home page after login
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/home')
def user_home():  # ✅ Renamed from home() to user_home()
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch first_name and last_name of the logged-in user
    cursor.execute("SELECT first_name, second_name FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('login'))

    full_name = f"{user['first_name']} {user['second_name']}"  # ✅ Combine first & last name

    return render_template('home.html', full_name=full_name) 


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Get username
    cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('login'))

    username = user['username']
    expenses_table = f"expenses_{username}"  # User-specific table

    # ✅ Get total, monthly & daily spending
    cursor.execute(f"SELECT SUM(amount) AS total FROM {expenses_table}")
    total_expense = cursor.fetchone()['total'] or 0

    cursor.execute(f"SELECT SUM(amount) AS month_total FROM {expenses_table} WHERE MONTH(created_at) = MONTH(CURRENT_DATE())")
    month_expense = cursor.fetchone()['month_total'] or 0

    cursor.execute(f"SELECT SUM(amount) AS today_total FROM {expenses_table} WHERE DATE(created_at) = CURRENT_DATE()")
    today_expense = cursor.fetchone()['today_total'] or 0

    # ✅ Get category-wise spending (for Bar Chart)
    cursor.execute(f"SELECT category, SUM(amount) AS total FROM {expenses_table} GROUP BY category")
    category_data = cursor.fetchall()
    category_labels = [row['category'] for row in category_data]
    category_values = [row['total'] for row in category_data]

    # ✅ Get monthly spending trend (Fixed Query)
    cursor.execute(f"""
        SELECT DATE_FORMAT(created_at, '%b %Y') AS month, SUM(amount) AS total
        FROM {expenses_table}
        GROUP BY DATE_FORMAT(created_at, '%b %Y')
        ORDER BY MIN(created_at);
    """)
    monthly_data = cursor.fetchall()
    month_labels = [row['month'] for row in monthly_data]
    month_values = [row['total'] for row in monthly_data]

    cursor.close()
    conn.close()

    return render_template(
        'dashboard.html', 
        total_expense=total_expense, 
        month_expense=month_expense, 
        today_expense=today_expense,
        category_labels=category_labels,
        category_values=category_values,
        month_labels=month_labels,
        month_values=month_values
    )



@app.route('/add_expense')
def add_expense_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get username
    cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('login'))

    username = user['username']
    expenses_table = f"expenses_{username}"  # User-specific table

    # Get all expenses
    cursor.execute(f"SELECT * FROM {expenses_table} ORDER BY created_at DESC")
    expenses = cursor.fetchall()

    # Get summary information
    cursor.execute(f"SELECT SUM(amount) AS total FROM {expenses_table}")
    total_spending = cursor.fetchone()['total'] or 0

    cursor.execute(f"SELECT SUM(amount) AS month_total FROM {expenses_table} WHERE MONTH(created_at) = MONTH(CURRENT_DATE())")
    month_spending = cursor.fetchone()['month_total'] or 0

    cursor.execute(f"SELECT SUM(amount) AS today_total FROM {expenses_table} WHERE DATE(created_at) = CURRENT_DATE()")
    today_spending = cursor.fetchone()['today_total'] or 0

    cursor.close()
    conn.close()

    return render_template('add_expense.html', 
                           expenses=expenses, 
                           total_spending=total_spending,
                           month_spending=month_spending, 
                           today_spending=today_spending)


@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    description = request.form.get('expenseName')
    amount = request.form.get('expenseAmount')
    
    # Load and use the ML model to predict category
    try:
        # Assuming you have your model loaded or accessible
        import joblib
        model = joblib.load('E:\\Python\\8th sem\\software engineering\\expense-tracker (2)\\expense-tracker\\ml_model\\expense_classifier_model.pkl')
        
        # Predict category
        predicted_category = model.predict([description])[0]
        
        # Use the predicted category
        category = predicted_category
    except Exception as e:
        # Fallback to a default category if prediction fails
        print(f"Category prediction failed: {str(e)}")
        category = "Miscellaneous"

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed!", "danger")
        return redirect(url_for('add_expense_page'))

    # Change this line - use dictionary=True parameter
    cursor = conn.cursor(dictionary=True)
    
    # Get the username of the logged-in user
    cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('add_expense_page'))
    
    username = user['username']  # Now this will work correctly
    expenses_table = f"expenses_{username}"  # User-specific table name

    # Insert expense into the user's table with predicted category
    cursor.execute(f"INSERT INTO {expenses_table} (description, amount, category) VALUES (%s, %s, %s)", 
                  (description, amount, category))
    conn.commit()
    cursor.close()
    conn.close()
    
    # Optionally inform the user what category was predicted
    flash(f"Expense added with predicted category: {category}", "success")
    
    return redirect(url_for('add_expense_page'))

@app.route('/update_expense_category', methods=['POST'])
def update_expense_category():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    expense_id = data.get('expense_id')
    new_category = data.get('category')

    if not expense_id or not new_category:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    username = user['username']
    expenses_table = f"expenses_{username}"

    cursor.execute(f"UPDATE {expenses_table} SET category = %s WHERE id = %s", (new_category, expense_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': True})



# ✅ Logout Route (Clears Session and Redirects to Home)
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('user_home'))


if __name__ == '__main__':
    app.run(debug=True)
