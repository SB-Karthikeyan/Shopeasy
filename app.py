# Libraries and Packages
from flask import Flask, request ,jsonify, render_template, redirect, url_for, flash, session, Response
import sqlite3
import hashlib
from datetime import timedelta, datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_unique_and_secure_secret_key' 
app.permanent_session_lifetime = timedelta(minutes=30)       


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Get the current session details
def get_current_session():
    if 'user_id' not in session:
        return None
    return {
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'email': session.get('email'),
        'role': session.get('role')
    }

def find_role():
    user = get_current_session()
    if not user:
        role = 'user'
    else:
        role = user.get('role')
    return role

# Connecting to Database
def get_db_connection():
    return sqlite3.connect("database/shopeasys.sqlite")

# Getting all the products from product table
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM product ORDER BY RANDOM()")
    products = cursor.fetchall()
    cursor.close()
    
    product_list=[
        {
            "id":p[0],
            "name":p[1],
            "description":p[2],
            "category":p[3],
            "price":p[4],
            "mrp":p[5],
            "rating":p[6],
            "stock":p[7],
            "product_type":p[8],
            "image_url":p[9]
        }
        for p in products
    ]
    return product_list

# Getting the details of product with product name
def get_product_by_name(product_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM product WHERE product_name = ? ",(product_name,))
    product = cursor.fetchone()
    cursor.close()

    if product is None:
        return None

    return {
        "id": product[0],
        "name": product[1],
        "description": product[2],
        "category": product[3],
        "price": product[4],
        "mrp": product[5],
        "rating": product[6],
        "stock": product[7],
        "product_type": product[8],
        "image_url": product[9],
    }

# Database table creation
def init_db():
    # Users table
    with sqlite3.connect('database/shopeasys.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                address TEXT DEFAULT NULL,
                passkey TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            );
        ''')
        conn.commit()

    # Cart table (with user_id and product_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(product_id) REFERENCES product(id)
            );
        ''')
        conn.commit()

    # orders table (with user_id and product_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders(
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(product_id) REFERENCES product(id)
            );
        ''')
        conn.commit()

    #Product table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product (
                id INTEGER PRIMARY KEY,
                product_name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                price INTEGER,
                mrp INTEGER,
                rating INTEGER,
                stock TEXT NOT NULL,
                product_type TEXT NOT NULL,
                image_url TEXT 
            );
        ''')
        conn.commit()

# Check for user existence in user table for login form
def check_user_credentials(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return "User not found"
    
    stored_password = user[4]
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    if stored_password == hashed_password:
        return user
    return "Incorrect password"

# ---------------       Route Starts         --------------- #

# Offer Update
current_offer = {
    'percentage': 40,
    'expiry': datetime.today().date()
}

@app.route('/offer_update', methods=['GET', 'POST'])
def update_all_offers():
    if request.method == 'POST':
        offer_percentage = int(request.form.get('offer_percentage', 40))

        two_days_later = datetime.today().date() + timedelta(days=2)
        offer_expiry = two_days_later.strftime('%Y-%m-%d')

        current_offer['percentage'] = offer_percentage
        current_offer['expiry'] = offer_expiry

        return redirect(url_for('index'))
    
    return render_template('offer_update.html')

# Index Page
@app.route('/')
def index():
    role = find_role()
    return render_template(
        'index.html',
        offer_percentage=current_offer['percentage'],
        offer_expiry=current_offer['expiry'],
        role=role
    )

# Admin Dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    user = get_current_session()
    if not user:
        flash('Kindly login to view admin details','error')
        return redirect(url_for('registration'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = get_current_session().get('user_id')
    role = cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
    user_role = role[0]

    users = cursor.execute("SELECT COUNT(id) FROM users WHERE role = 'user'").fetchone()
    user_count = users[0]
    orders = cursor.execute("SELECT COUNT(DISTINCT user_id) FROM orders").fetchone()
    order_count = orders[0]
    
    cursor.execute("""
        SELECT SUM(orders.quantity * product.price) AS total_price
        FROM orders
        JOIN product ON orders.product_id = product.id;
    """)
    result = cursor.fetchone()
    total_price = result[0]

    products=cursor.execute(""" SELECT COUNT(quantity) FROM orders""").fetchone()
    product_count = products[0]

    if user_role == 'admin':
        return render_template(
            'admin.html',
            user=user,
            user_count=user_count,
            order_count=order_count,
            total_price=total_price,
            product_count=product_count
        )
    else:
        return redirect(url_for('registration'))

# Add Admin Page
@app.route('/add_admin')
def add_admin():
    return render_template('registration.html', is_admin = True)


# Profile Page
@app.route('/profile')
def profile():
    user = get_current_session()
    if not user:
        flash('Kindly register/login to view profile details','error')
        return redirect(url_for('registration'))

    email = user.get('email')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT address FROM users WHERE email = ?",(email,))
    result = cursor.fetchone()

    role = cursor.execute("SELECT role FROM users WHERE email = ?",(email,)).fetchone()
    user_role = role[0]

    conn.close()

    if result and result[0]:
        address = result[0]         
    else:
        address = "Address not added"

    if user_role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('profile.html', user=user, address=address)



# Address Updation
@app.route('/update-address', methods=['POST'])
def updateAddress():
    address = request.form['address']
    prop_address = address.strip()
    email = get_current_session().get('email')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET address = ? WHERE email = ?",(prop_address,email))
    conn.commit()
    conn.close()

    flash('Address changed successfully!','success')
    return redirect(url_for('profile'))

# Password Update Page
@app.route('/update-password', methods=['POST'])
def updatePassword():
    old_password = request.form['old-password']
    new_password = request.form['new-password']
    con_new_password = request.form['con-new-password']

    user_id = get_current_session().get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute("SELECT passkey FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        flash('User not found.')
        return redirect(url_for('profile'))

    old_password_hash = hashlib.sha256(old_password.encode()).hexdigest()
    stored_passkey = user[0]

    if old_password_hash != stored_passkey:
        flash('Old password is incorrect.','error')
        return redirect(url_for('profile'))

    elif not new_password.strip():
        flash('New password cannot be empty.', 'error')
        return redirect(url_for('profile'))

    elif new_password != con_new_password:
        flash('New passwords do not match.','error')
        return redirect(url_for('profile'))
    
    else:
        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        cursor.execute("UPDATE users SET passkey = ? WHERE id = ?", (new_password_hash, user_id))
        flash('Password updated successfully.','success')

    conn.commit()
    conn.close()
        
    return redirect(url_for('profile'))

# Route for shop/products page
@app.route('/products')
def products_page():
    role = find_role()
    return render_template("products.html", role=role)


#Javascript fetch path to get the products and return ad json 
@app.route('/api/products')
def api_products():
    products = get_products()
    role = find_role()
    return jsonify({'products': products, 'user_status': role})



# Route to get the product details page with product name
@app.route("/templates/product-details/<string:product_name>")
def api_product_details(product_name):
    product = get_product_by_name(product_name)
    role = find_role()
    if product:
        return render_template('product-details.html', product=product, role = role)
    else:
        return render_template('error.html',message="Oops! Product details not found."),404


# Route for registration page
@app.route('/registration')
def registration():
    return render_template('registration.html')


# Route to register ( New user entry )
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        prop_username = username.title()
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email is already registered. Try Logging in.', 'error')
            return render_template('registration.html', is_admin=(role == 'admin'))

        cursor.execute('''
            INSERT INTO users (username, email, passkey, role) VALUES (?, ?, ?, ?)
        ''', (prop_username, email, hashed_password, role))

        flash(f'Welcome {prop_username}! Have a good day!!', 'success')

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        new_user = cursor.fetchone()
        session.permanent = True
        session['user_id'] = new_user[0]
        session['username'] = new_user[1]
        session['email'] = new_user[2]
        session['role'] = new_user[5]

        conn.commit()
        conn.close()

        return redirect(url_for('admin_dashboard') if role == 'admin' else url_for('index'))
    
    return render_template('registration.html')


# Route to login ( existing user entry )
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = check_user_credentials(email, password)

        if user == "User not found":
            flash('User does not exist. Please register.', 'error')
            return render_template('registration.html')
        elif user == "Incorrect password":
            flash('Incorrect password. Please try again.', 'error')
            return render_template('registration.html')
        else:
            session.permanent = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            session['role'] = user[5]
            flash(f'Welcome back, {user[1]}!', 'success')

    return redirect(url_for('index'))

# Cart Products Recovery
@app.route('/api/cart/products')
def cartProducts():
    user = get_current_session()
    user_id = user.get('user_id')
    
    if not user:
        return jsonify({'error': 'User not logged in'}), 401

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
        p.id, p.product_name, p.price, p.image_url, c.quantity
        FROM cart c
        JOIN product p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user_id,))

    cart_items = cursor.fetchall()
    conn.close()

    cartProducts = [
        {
            'id': row['id'],
            'name': row['product_name'],
            'price': row['price'],
            'image_url': row['image_url'],
            'quantity': row['quantity']
        }
        for row in cart_items
    ]

    return jsonify(cartProducts)


# Javascript fetch to check for user login (cart storage)
@app.route('/session/data')
def session_data():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user_id': session['user_id'],
            'username': session.get('username')
        })
    return jsonify({'logged_in': False})

# Javascript fetch to pass the local storage cart items and
# Store in cart table with user_id
@app.route('/cart', methods=['POST'])
@login_required
def save_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = session.get('user_id')
    data = request.get_json().get('data')

    try:
        # Clear existing cart if data is empty or None
        if not data:
            cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
            conn.commit()
            return jsonify({'message': 'Cart cleared'}), 200

        # Clear existing cart before inserting new data
        cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))

        for item in data:
            if isinstance(item, dict):
                item_id = item.get('id')
                quantity = item.get('quantity')

                cursor.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                (user_id, item_id, quantity)
                )
        conn.commit()
        return jsonify({'message': 'Data saved successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()

# Add New Product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO product (
                product_name, description, category,
                price, mrp, rating, stock,
                product_type, image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['name'],
            request.form.get('description', ''),
            request.form['category'],
            int(request.form['price']),
            int(request.form['mrp']),
            0,
            request.form['stock'],
            request.form['product_type'],
            ''
        ))
        conn.commit()
        return redirect(url_for('products_page'))
    return render_template('add_product.html')

# Update Existing Product
@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM product WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product:
        return "Product not found", 404

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        price = float(request.form['price'])
        mrp = float(request.form['mrp'])
        stock = request.form['stock']
        product_type = request.form['product_type']

        try:
            cursor.execute("""
                UPDATE product 
                SET product_name = ?, description = ?, category = ?, price = ?, mrp = ?, stock = ?, product_type = ?
                WHERE id = ?
            """, (name, description, category, price, mrp, stock, product_type, product_id))
            conn.commit()
            conn.close()
            flash('Details updated successfully.','success')
            return redirect(url_for('products_page'))
        except Exception as e:
            flash('Something went wrong!.','error')
            conn.close()
            return f"An error occurred: {e}"

    conn.close()
    return render_template('update_product.html', product=product)

# Delete Existing Product
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM product WHERE id = ?",(product_id,))
    conn.commit()
    flash('Product deletion successful.','success')
    return redirect(url_for('products_page'))

# Product Deliverable Pincode
deliverable_pincodes = {
    "600001", "600002", "600003", "600004", "600005", "600006", "600007", "600008", "600009", "600010",
    "600017", "600020", "600028", "600040", "600041", "600083", "600100", "600113", "600115", "600125",
    "625001", "625002", "625003", "625004", "625005", "625006", "625007", "625008", "625009", "625010",
    "620001", "620002", "620003", "620004", "620005", "620006", "620007", "620008", "620009",
    "636001", "636002", "636003", "636004", "636005", "636006", "636007", "636008", "636009", "636102",
    "641001", "641002", "641003", "641004", "641005", "641006", "641007", "641008", "641009", "641012",
    "627001", "627002", "627003", "627004", "627005", "627006", "627007", "627008", "627009",
    "632001", "632002", "632003", "632004", "632005", "632006", "632007", "632008", "632009",
    "613001", "613002", "613003", "613004", "613005", "613006",
    "624001", "624002", "624003", "624004", "624005",
    "628001", "628002", "628003", "628004", "628005",
    "631501", "606601", "605602", "607001", "607002", "607003",
    "639001", "637001", "638001", "638002", "638003"
}

@app.route('/check-delivery')
def check_delivery():
    pincode = request.args.get('pincode')
    if pincode in deliverable_pincodes:
        return jsonify({'available': True})
    else:
        return jsonify({'available': False})

# Route for checkout page
@app.route('/checkout')
def checkout():
    user_id = session.get('user_id')

    if not user_id:
        flash('Kindly login/register to proceed for checkout.', 'error')
        return redirect(url_for('registration'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT address FROM users WHERE id = ?", (user_id,))
    address = cursor.fetchone()
    conn.close()

    result = address[0] if address else None

    if result is None or result.strip() == '':
        flash('Please add your address before proceeding for checkout.', 'error')
        return redirect(url_for('profile'))
    
    return render_template('checkout.html')


# ordered products
@app.route('/order-products')
def orders_products():
    user_id = get_current_session().get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT product_id, quantity FROM cart WHERE user_id = ?', (user_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            return Response(status=204)

        for product_id, quantity in cart_items:
            # Check if the order already exists
            cursor.execute(
                'SELECT quantity FROM orders WHERE user_id = ? AND product_id = ?',
                (user_id, product_id)
            )
            existing_order = cursor.fetchone()

            if existing_order:
                # Update the quantity if order exists
                new_quantity = existing_order[0] + quantity
                cursor.execute(
                    'UPDATE orders SET quantity = ? WHERE user_id = ? AND product_id = ?',
                    (new_quantity, user_id, product_id)
                )
            else:
                # Insert new order if it doesn't exist
                cursor.execute(
                    'INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, ?)',
                    (user_id, product_id, quantity)
                )

        # Clear the cart
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        conn.commit()
        return jsonify({'success': True}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()


# Order History for Profile page
@app.route('/order-history')
def order_history():
    user_id = get_current_session().get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
        p.product_name, p.price, p.image_url, o.quantity
        FROM orders o
        JOIN product p ON o.product_id = p.id
        WHERE o.user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()

    conn.close()
    orders=[
        {
            "name":row[0],
            "price":row[1],
            "image":row[2],
            "quantity":row[3]
        }
        for row in rows
    ]
    
    return jsonify(orders)

# Remove Account
@app.route('/remove-account')
def remove_account():
    user_id = session.get('user_id')
    email = session.get('email')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = ?",(email,))
    cursor.execute("DELETE FROM cart WHERE user_id = ?",(user_id,))
    cursor.execute("DELETE FROM orders WHERE user_id = ?",(user_id,))
    conn.commit()
    conn.close()

    session.clear()
    flash('User account removed successfully.','success')
    return redirect(url_for('index'))


#Route for logout the session
@app.route('/logout')
def logout():
    if session.get('username'):
        session.clear()
        flash('Logged out successfully!', 'success')
        return redirect(url_for('index'))
    flash('No user have logged in!!', 'error')
    return redirect(url_for('index'))

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
 