from flask import Flask, render_template, request, redirect, url_for 
import mysql.connector

app = Flask(__name__)

from flask import session
app.secret_key = 'password' 

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="FUSIONtec777@", 
        database="bestbuy_db"
    )

@app.route('/')
def home():
    if 'user_role' not in session or session['user_role'] != 'customer':
        return redirect('/login')
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.product_id,
            p.UPC,
            p.price,
            b.brand_name,
            pt.type_name
        FROM Product p
        JOIN Brand b ON p.brand_id = b.brand_id
        JOIN ProductType pt ON p.type_id = pt.type_id
    """)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/queries')
def queries():
    return render_template('queries.html')

@app.route('/query1')
def query1():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.store_id, st.location, p.product_id, p.UPC, p.price, SUM(si.quantity) AS total_sold
        FROM SaleItem si
        JOIN Sales s ON si.sale_id = s.sale_id
        JOIN Product p ON si.product_id = p.product_id
        JOIN Store st ON s.store_id = st.store_id
        GROUP BY s.store_id, p.product_id
        ORDER BY s.store_id, total_sold DESC
        LIMIT 20
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('query_results.html', query_title="Top 20 Products per Store", results=results)

@app.route('/query2')
def query2():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT SUBSTRING_INDEX(st.location, ', ', -1) AS state, p.product_id, p.UPC, p.price, SUM(si.quantity) AS total_sold
        FROM SaleItem si
        JOIN Sales s ON si.sale_id = s.sale_id
        JOIN Product p ON si.product_id = p.product_id
        JOIN Store st ON s.store_id = st.store_id
        GROUP BY state, p.product_id
        ORDER BY state, total_sold DESC
        LIMIT 20
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('query_results.html', query_title="Top 20 Products per State", results=results)

@app.route('/query3')
def query3():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.store_id, st.location, COUNT(*) AS total_sales, SUM(s.total_amount) AS total_revenue
        FROM Sales s
        JOIN Store st ON s.store_id = st.store_id
        WHERE YEAR(s.sale_date) = YEAR(CURDATE())
        GROUP BY s.store_id
        ORDER BY total_revenue DESC
        LIMIT 5
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('query_results.html', query_title="Top 5 Stores This Year", results=results)

@app.route('/query4')
def query4():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        WITH brand_sales AS (
            SELECT s.store_id, b.brand_name, SUM(si.quantity) AS units_sold
            FROM SaleItem si
            JOIN Product p ON si.product_id = p.product_id
            JOIN Brand b ON p.brand_id = b.brand_id
            JOIN Sales s ON si.sale_id = s.sale_id
            WHERE b.brand_name IN ('Sony', 'Samsung')
            GROUP BY s.store_id, b.brand_name
        ),
        brand_compare AS (
            SELECT store_id,
                MAX(CASE WHEN brand_name = 'Sony' THEN units_sold ELSE 0 END) AS sony_sales,
                MAX(CASE WHEN brand_name = 'Samsung' THEN units_sold ELSE 0 END) AS samsung_sales
            FROM brand_sales
            GROUP BY store_id
        )
        SELECT COUNT(*) AS stores_where_sony_outsells_samsung
        FROM brand_compare
        WHERE sony_sales > samsung_sales
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('query_results.html', query_title="Stores Where Sony Outsells Samsung", results=results)

@app.route('/query5')
def query5():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        WITH laptop_customers AS (
            SELECT DISTINCT s.customer_id
            FROM Sales s
            JOIN SaleItem si ON s.sale_id = si.sale_id
            JOIN Product p ON si.product_id = p.product_id
            JOIN ProductType pt ON p.type_id = pt.type_id
            WHERE pt.type_name = 'Laptop'
        ),
        other_purchases AS (
            SELECT pt.type_name, COUNT(*) AS purchase_count
            FROM Sales s
            JOIN laptop_customers lc ON s.customer_id = lc.customer_id
            JOIN SaleItem si ON s.sale_id = si.sale_id
            JOIN Product p ON si.product_id = p.product_id
            JOIN ProductType pt ON p.type_id = pt.type_id
            WHERE pt.type_name != 'Laptop'
            GROUP BY pt.type_name
        )
        SELECT type_name, purchase_count
        FROM other_purchases
        ORDER BY purchase_count DESC
        LIMIT 3
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('query_results.html', query_title="Top Complementary Purchases (Laptop Buyers)", results=results)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin123':
            return redirect('/add_product?admin=true')
        else:
            return 'Invalid password'
    return '''
        <form method="post">
            Admin Password: <input type="password" name="password">
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        role = request.form['role']
        
        session['user_email'] = email
        session['user_role'] = role
        
        if role == 'admin' and email == 'admin@bestbuy.com':
            return redirect('/add_product')
        elif role == 'vendor' and email == 'vendor@bestbuy.com':
            return redirect('/vendor_dashboard')
        elif role == 'customer':
            return redirect('/') 
        else:
            return 'Invalid login'
    
    return render_template('login.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        upc = request.form['upc']
        price = request.form['price'].replace('$', '').strip()
        brand_id = request.form['brand_id']
        type_id = request.form['type_id']

        cursor.execute(
            "INSERT INTO Product (UPC, price, brand_id, type_id) VALUES (%s, %s, %s, %s)",
            (upc, price, brand_id, type_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/')
    
    cursor.execute("SELECT brand_id, brand_name FROM Brand")
    brands = cursor.fetchall()
    
    cursor.execute("SELECT type_id, type_name FROM ProductType")
    types = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('add_product.html', brands=brands, types=types)

@app.route('/vendor_dashboard')
def vendor_dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.product_id, p.UPC, b.brand_name, i.stock_quantity
        FROM Product p
        JOIN Brand b ON p.brand_id = b.brand_id
        JOIN Inventory i ON p.product_id = i.product_id
        WHERE i.stock_quantity < 20  # Low stock example
    """)
    low_stock = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('vendor_dashboard.html', low_stock=low_stock)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'user_role' not in session or session['user_role'] != 'customer':
        return redirect('/login')
    
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    session.modified = True
    return redirect('/')

@app.route('/cart')
def view_cart():
    if 'user_role' not in session or session['user_role'] != 'customer':
        return redirect('/login')
    
    cart_ids = session.get('cart', [])
    if not cart_ids:
        return "Your cart is empty."
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    placeholders = ','.join(['%s'] * len(cart_ids))
    cursor.execute(f"SELECT product_id, UPC, price FROM Product WHERE product_id IN ({placeholders})", cart_ids)
    cart_items = cursor.fetchall()
    cursor.close()
    conn.close()
    
    total = sum(item['price'] for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/checkout')
def checkout():
    if 'user_role' not in session or session['user_role'] != 'customer':
        return redirect('/login')
    
    cart_ids = session.get('cart', [])
    if not cart_ids:
        return "Cart is empty."
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("START TRANSACTION")
        customer_id = None 
        store_id = 1
        cursor.execute(
            "INSERT INTO Sales (customer_id, store_id, total_amount) VALUES (%s, %s, 0)",
            (customer_id, store_id)
        )
        sale_id = cursor.lastrowid
        
        total = 0
        for pid in cart_ids:
            cursor.execute("SELECT price FROM Product WHERE product_id = %s", (pid,))
            price = cursor.fetchone()[0]
            
            cursor.execute(
                "INSERT INTO SaleItem (sale_id, product_id, quantity, price) VALUES (%s, %s, 1, %s)",
                (sale_id, pid, price)
            )
            total += price
        
        cursor.execute("UPDATE Sales SET total_amount = %s WHERE sale_id = %s", (total, sale_id))
        
        conn.commit()
        session.pop('cart', None) # Clear cart
        
        cursor.close()
        conn.close()
        
        return render_template('checkout_success.html', sale_id=sale_id, total=f"{total:.2f}")
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return f"Checkout failed: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)