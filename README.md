### Retailer Enterprise Database System (Best Buy Model)
Author: Md Safwan Bin Rashid

Demo: https://drive.google.com/file/d/11os9r0gcYer6dvo-Df9w1cJ0i8B_1_7M/view?usp=sharing

- Database: MySQL 8.0+
- Backend: Python 3.8+ with Flask
- Frontend: HTML5, CSS3
- Database Connector: mysql-connector-python
- Testing: Python threading for concurrency tests


## PROJECT STRUCTURE
│
├── README.txt
├── Code/
│   ├── app.py                 (Main Flask application)
│   ├── concurrency_test.py    (Concurrency simulation)
│   ├── templates/             (HTML templates)
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── queries.html
│   │   ├── query_results.html
│   │   ├── add_product.html
│   │   ├── vendor_dashboard.html
│   │   ├── cart.html
│   │   └── ...
│   └── static/
│       └── style.css          (CSS stylesheet)
│
├── SQL Scripts (CREATE + INSERT + QUERIES).pdf 


### RUN THE APPLICATION
1. pip install flask mysql-connector-python==8.0.33
2. Start the Flask development server: source venv/bin/activate (won't be the same for you tho)
3. python app.py
4. Open web browser and go to:
   http://127.0.0.1:5000/login


## TEST ACCOUNTS

1. CUSTOMER:
   - Email: Any email
   - Role: Select "Customer"
   - Features: Browse products, add to cart, checkout

2. ADMIN:
   - Email: admin@bestbuy.com
   - Role: Select "Admin"
   - Features: Add new products to database

3. VENDOR:
   - Email: vendor@bestbuy.com
   - Role: Select "Vendor"
   - Features: View low-stock products


## CONCURRENCY TESTING

1. The app should NOT be running
2. Run the concurrency test:
   python concurrency_test.py

Simulates two customers purchasing the same product at the same time.

